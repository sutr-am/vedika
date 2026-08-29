# src/vedika/infrastructure/crawlers/github.py
import base64
import hashlib
from urllib.parse import urlparse
from uuid import UUID, uuid5

from github import Auth, Github
from github.GithubException import GithubException
from github.Repository import Repository
from loguru import logger
from pydantic import HttpUrl
from tqdm import tqdm

from vedika.application.interfaces.crawlers import BaseCrawler
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.types import DataCategory


class GithubCrawler(BaseCrawler):
    category: DataCategory = DataCategory.CODEBASES
    provider = "github"
    version = "1"

    def __init__(
        self,
        github_token: str | None,
        ignore=(
            ".git",
            ".toml",
            ".lock",
            ".png",
            ".jpg",
            "__pycache__",
            ".gitignore",
            ".DS_Store",
        ),
    ) -> None:
        # super().__init__(repository)
        self._ignore = ignore
        if github_token:
            auth = Auth.Token(token=github_token)
            self.gh = Github(auth=auth)
        else:
            self.gh = Github()

    def canonicalize_url(self, url: str) -> str:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname != "github.com":
            raise ValueError(f"Invalid GitHub repository URL: {url}")
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            raise ValueError(f"GitHub repository URL must include owner and repository: {url}")
        owner, repository = parts[:2]
        return f"https://github.com/{owner.lower()}/{repository.removesuffix('.git').lower()}"

    @staticmethod
    def _parse_repo_url(canonical_url: str) -> tuple[str, str]:
        repo_path = urlparse(canonical_url).path.strip("/")
        return repo_path, repo_path.split("/")[-1]

    def get_revision(self, canonical_url: str) -> str:
        repo_path, _ = self._parse_repo_url(canonical_url)
        repo = self.gh.get_repo(repo_path)
        return repo.get_branch(repo.default_branch).commit.sha

    def _should_ignore(self, file_path: str) -> bool:
        return any(file_path.endswith(i) or f"/{i}/" in file_path for i in self._ignore)

    @staticmethod
    def _fetch_file_content(repo: Repository, file_path: str):
        try:
            file_content_encoded = repo.get_contents(file_path)
            # If the API return a list, then it's a dictionary; so we can skip it as it's not code
            if isinstance(file_content_encoded, list):
                return None
            file_content_decoded = base64.b64decode(file_content_encoded.content).decode("utf-8")
            return file_content_decoded
        except (GithubException, UnicodeDecodeError) as e:
            logger.warning(f"Skipped file {file_path} due to error: {e}")
            return None

    def _build_documents(
        self,
        repo: Repository,
        tree,
        user_id: UUID,
        source_id: UUID,
        crawl_id: UUID,
        canonical_url: str,
    ) -> list[CodebaseRawDomain]:
        documents = []
        for element in tqdm(tree, desc=f"Crawling {repo.name} files"):
            if element.type == "tree" or self._should_ignore(element.path):
                continue
            file_content = self._fetch_file_content(repo, element.path)
            if file_content:
                documents.append(
                    CodebaseRawDomain(
                        id=uuid5(crawl_id, element.path),
                        source_id=source_id,
                        crawl_id=crawl_id,
                        title=f"github/{repo.full_name}/{element.path}",
                        content=file_content,
                        platform="github",
                        source_url=HttpUrl(canonical_url),
                        user_id=user_id,
                        repository_path=element.path,
                        upstream_file_sha=element.sha,
                        content_sha256=hashlib.sha256(file_content.encode()).hexdigest(),
                    )
                )
        return documents

    def extract(
        self, canonical_url: str, user_id: UUID, source_id: UUID, crawl_id: UUID
    ) -> list[CodebaseRawDomain]:
        """
        Orchestrates the crawling process and saves the resulting CodebaseDocument
        """
        logger.info(f"Crawling Github Repository: {canonical_url}")

        repo_path, _ = self._parse_repo_url(canonical_url=canonical_url)
        try:
            # Get repo details
            repo = self.gh.get_repo(repo_path)
            tree = repo.get_git_tree(sha=repo.default_branch, recursive=True).tree

            return self._build_documents(
                repo=repo,
                tree=tree,
                user_id=user_id,
                source_id=source_id,
                crawl_id=crawl_id,
                canonical_url=canonical_url,
            )
        except GithubException as e:
            logger.exception(f"Failed to crawl {canonical_url}: {e}")
            raise e

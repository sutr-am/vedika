# src/vedika/infrastructure/crawlers/github.py
import base64

from github import Auth, Github
from github.GithubException import GithubException
from github.Repository import Repository
from loguru import logger
from pydantic import UUID4, HttpUrl
from tqdm import tqdm

from vedika.application.interfaces.crawlers import BaseCrawler
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.types import DataCategory


class GithubCrawler(BaseCrawler):
    category: DataCategory = DataCategory.CODEBASES

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

    @staticmethod
    def _parse_repo_url(url: str) -> tuple[str, str]:
        repo_path = (
            url.replace("https://github.com", "").replace("http://github.com", "").strip("/")
        )
        repo_name = repo_path.split("/")[-1]
        return repo_path, repo_name

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

    def _build_content_str(self, repo: Repository, tree):
        content_str = ""
        # for element in tree:
        for element in tqdm(tree, desc=f"Crawling {repo.name} files"):
            if element.type == "tree" or self._should_ignore(element.path):
                continue
            file_content = self._fetch_file_content(repo, element.path)
            if file_content:
                header = f"{'---' * 10} FILE: {element.path} {'---' * 10}\n"
                footer = f"{'---' * 20}\n\n"
                content_str += header + file_content + footer
        return content_str

    def extract(self, url: str, user_id: UUID4, user_full_name: str) -> CodebaseRawDomain:
        """
        Orchestrates the crawling process and saves the resulting CodebaseDocument
        """
        logger.info(f"Crawling Github Repository: {url}")

        repo_path, repo_name = self._parse_repo_url(url=url)
        try:
            # Get repo details
            repo = self.gh.get_repo(repo_path)
            tree = repo.get_git_tree(sha=repo.default_branch, recursive=True).tree

            # Build the massive content string from all the code in the repo
            content_str = self._build_content_str(repo, tree)

            # 1. Instantiate the pure Domain model
            raw_data = CodebaseRawDomain(
                title=f"github/{repo_name}",
                content=content_str,
                platform="github",
                source_url=HttpUrl(url),
                user_id=user_id,
            )
            return raw_data
        except GithubException as e:
            logger.exception(f"Failed to crawl {url}: {e}")
            raise e

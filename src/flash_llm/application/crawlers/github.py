import base64
import os

from github import Auth, Github
from github.GithubException import GithubException
from github.Repository import Repository
from loguru import logger
from pydantic import UUID4, HttpUrl

from flash_llm.application.crawlers.base import BaseCrawler
from flash_llm.domain.documents import CodebaseDocumentDomain
from flash_llm.domain.repositories import DocumentRepository


class GithubCrawler(BaseCrawler):
    def __init__(
        self,
        repository: DocumentRepository,
        ignore=(".git", ".toml", ".lock", ".png", ".jpg", "__pycache__", ".gitignore", ".DS_Store"),
    ) -> None:
        super().__init__(repository)
        self._ignore = ignore
        token = os.getenv("GITHUB_TOKEN")
        if token:
            auth = Auth.Token(token=token)
            self.gh = Github(auth=auth)
        else:
            self.gh = Github()

    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        repo_path = (
            url.replace("https://github.com", "").replace("http://github.com", "").strip("/")
        )
        repo_name = repo_path.split("/")[-1]
        return repo_path, repo_name

    def _should_ignore(self, file_path: str) -> bool:
        return any(file_path.endswith(i) or f"/{i}/" in file_path for i in self._ignore)

    def _fetch_file_content(self, repo: Repository, file_path: str):
        try:
            file_content_encoded = repo.get_contents(file_path)
            # If the API return a list, the it's a dictionary; so we can skip it as its not code
            if isinstance(file_content_encoded, list):
                return None
            file_content_decoded = base64.b64decode(file_content_encoded.content).decode("utf-8")
            return file_content_decoded
        except (GithubException, UnicodeDecodeError) as e:
            logger.warning(f"Skipped file {file_path} due to error: {e}")
            return None

    def _build_content_str(self, repo: Repository, tree):
        content_str = ""
        for element in tree:
            if element.type == "tree" or self._should_ignore(element.path):
                continue
            file_content = self._fetch_file_content(repo, element.path)
            if file_content:
                header = f"{'---' * 10} FILE: {element.path} {'---' * 10}\n"
                footer = f"{'---' * 20}\n\n"
                content_str += header + file_content + footer
        return content_str

    def extract(self, url: str, user_id: UUID4, user_full_name: str) -> None:
        """
        Orchestrates the crwaling process and saves the resulting CodebaseDocument
        """
        logger.info(f"Crawling Github Repository: {url}")

        repo_path, repo_name = self._parse_repo_url(url=url)
        try:
            # Get repo details
            repo = self.gh.get_repo(repo_path)
            tree = repo.get_git_tree(sha=repo.default_branch, recursive=True).tree

            # Build the massive content string from all teh code in teh repo
            content_str = self._build_content_str(repo, tree)

            # 1. Instantiate the pure Domain model
            domain_doc = CodebaseDocumentDomain(
                title=f"GitHub - {repo_name}",
                source_url=HttpUrl(url),
                platform="github",
                author_id=user_id,
                author_full_name=user_full_name,
                content=content_str,
                name=repo_name,
            )

            # 2. Save using the abstract interface
            self.repository.save_codebase(codebase=domain_doc)
            logger.success(f"Successfully saved codebase: {repo_name}")
        except GithubException as e:
            logger.exception(f"Failed to crawl {url}: {e}")
            raise e

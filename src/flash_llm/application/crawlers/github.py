from github import Auth, Github
from loguru import logger
from pydantic import UUID4, HttpUrl

from flash_llm.application.crawlers.base import BaseCrawler
from flash_llm.domain.documents import CodebaseDocumentDomain


class GithubCrawler(BaseCrawler):
    def extract(self, url: str, user_id: UUID4, user_full_name: str) -> None:
        # return super().extract(url, user_id, user_full_name)
        logger.info(f"Crawling Github Repository: {url}")

        # !TODO: Implement actual Github scrapping using PyGithub (github)
        repo_name = url.rstrip("/").split("/")[-1]
        mock_content = f"This is a mock README.md content for {repo_name}"

        # 1. Instantiate the pure Domain model
        domain_doc = CodebaseDocumentDomain(
            title=f"GitHub - {repo_name}",
            source_url=HttpUrl(url),
            platform="github",
            author_id=user_id,
            author_full_name=user_full_name,
            content=mock_content,
            name=repo_name,
        )

        # 2. Save using the abstract interface
        self.repository.save_codebase(codebase=domain_doc)
        logger.success(f"Successfully saved codebase: {repo_name}")

from flash_llm.application.crawlers.base import BaseCrawler
from flash_llm.application.crawlers.github import GithubCrawler
from flash_llm.domain.repositories import DocumentRepository


class CrawlerDispatcher:
    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    def get_crawler(self, url: str) -> BaseCrawler:
        if "github.com" in url:
            return GithubCrawler(repository=self.repository)
        else:
            raise ValueError(f"No Crawler found for {url}")

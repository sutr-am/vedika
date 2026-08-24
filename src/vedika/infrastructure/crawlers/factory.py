# src/vedika/infrastructure/crawlers/factory.py
import os

from vedika.application.interfaces.crawlers import BaseCrawler
from vedika.infrastructure.crawlers.github import GithubCrawler


class CrawlerDispatcher:
    def __init__(self) -> None:
        self._registry: dict[str, BaseCrawler] = {}

    def register(self, domain_keyword: str, crawler_instance: BaseCrawler) -> None:
        """Registers a crawler class to a specific keyword"""
        self._registry[domain_keyword] = crawler_instance

    def get_crawler(self, url: str) -> BaseCrawler:
        for keyword, crawler_instance in self._registry.items():
            if keyword in url:  # !BUG: need better strategy instead of just 'in' check
                return crawler_instance
        raise ValueError(f"No Crawler found of {url}")


def build_crawler_dispatcher() -> CrawlerDispatcher:
    """Builds and wires up dispatcher with all available crawlers"""
    dispatcher = CrawlerDispatcher()

    # 1. Gather dependencies
    github_token = os.getenv("GITHUB_TOKEN")  # TODO: get it from settigs.py instead
    # bitbucket_token = os.getenv("BITBUCKET_TOKEN")    # TODO: get it from settigs.py instead

    # 2. Instantiate the crawlers
    github_crawler = GithubCrawler(github_token=github_token)
    # bitbucket_crawler = BitbucketCrawler(bitbucket_token=bitbucket_token)

    # 3. Register the instances
    dispatcher.register(domain_keyword="github.com", crawler_instance=github_crawler)
    # dispatcher.register(domain_keyword="bitbucket.com", crawler_instance=bitbucket_crawler)
    # dispatcher.register(domain_keyword="medium.com", crawler_instance=article_crawler)

    return dispatcher

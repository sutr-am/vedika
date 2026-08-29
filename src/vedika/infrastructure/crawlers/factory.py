# src/vedika/infrastructure/crawlers/factory.py
from urllib.parse import urlparse

from vedika.application.interfaces.crawlers import BaseCrawler, BaseCrawlerRouter
from vedika.infrastructure.crawlers.github import GithubCrawler


class CrawlerRouter(BaseCrawlerRouter):
    def __init__(self) -> None:
        self._registry: dict[str, BaseCrawler] = {}

    def register(self, host: str, crawler: BaseCrawler) -> None:
        """Registers a crawler class to a specific keyword"""
        self._registry[host] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        hostname = urlparse(url=url).hostname
        if hostname is None:
            raise ValueError(f"Invalid URL: {url}")

        for registered_host, crawler in self._registry.items():
            if hostname == registered_host or hostname.endswith(f".{registered_host}"):
                return crawler
        raise ValueError(f"No crawler found of {hostname=}")


def build_crawler_router(github_token: str | None = None) -> CrawlerRouter:
    """Builds and wires up router with all available crawlers"""
    router = CrawlerRouter()

    # 2. Instantiate the crawlers
    github_crawler = GithubCrawler(github_token=github_token)
    # bitbucket_crawler = BitbucketCrawler(bitbucket_token=bitbucket_token)

    # 3. Register the instances
    router.register(host="github.com", crawler=github_crawler)
    # router.register(domain_keyword="bitbucket.com", crawler_instance=bitbucket_crawler)
    # router.register(domain_keyword="medium.com", crawler_instance=article_crawler)

    return router

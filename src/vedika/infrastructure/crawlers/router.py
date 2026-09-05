from urllib.parse import urlparse

from vedika.application.interfaces.crawlers import BaseCrawler, BaseCrawlerRouter


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

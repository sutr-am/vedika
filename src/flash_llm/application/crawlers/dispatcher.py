from flash_llm.application.crawlers.base import BaseCrawler


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

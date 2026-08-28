# src/vedika/application/services/crawling_service.py

from loguru import logger
from pydantic import UUID4

from vedika.domain.types import CrawlStatus
from vedika.infrastructure.crawlers.factory import build_crawler_dispatcher
from vedika.infrastructure.db.factory import get_raw_repository


class CrawlerService:
    """Orchestrates extractions and raw persistence"""

    def __init__(self):
        # the service know where the factories are
        self._crawler_registry = build_crawler_dispatcher()

    def crawl_and_save(
        self,
        url: str,
        user_id: UUID4,
        # user_full_name: str,
        force_recrawl: bool = False,
    ) -> CrawlStatus:
        """Return True if successful, False otherwise"""
        try:
            crawler = self._crawler_registry.get_crawler(url=url)
            category = crawler.category
            repository = get_raw_repository(category=category)
            if not force_recrawl and repository.exists_by_url(url=url):
                logger.info(f"Skipping {url}. Already exists")
                return CrawlStatus.SKIPPED
            data = crawler.extract(url=url, user_id=user_id)
            repository.save(data)
            return CrawlStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Error while crawling {url=}: \n{e}")
            return CrawlStatus.FAILED

# src/vedika/application/services/crawling_service.py

from loguru import logger
from pydantic import UUID4

from vedika.application.interfaces.crawlers import BaseCrawlerRouter
from vedika.application.interfaces.providers import BaseRepositoryProvider
from vedika.application.interfaces.repositories import BaseRawRepository
from vedika.domain.types import CrawlStatus


class CrawlerService:
    def __init__(
        self, crawler_router: BaseCrawlerRouter, repository_provider: BaseRepositoryProvider
    ) -> None:
        self._crawler_router = crawler_router
        self._repository_provider = repository_provider

    def crawl_and_save(
        self,
        url: str,
        user_id: UUID4,
        force_recrawl: bool = False,
    ) -> CrawlStatus:
        try:
            crawler = self._crawler_router.get_crawler(url=url)
            repository: BaseRawRepository = self._repository_provider.get_raw_repository(
                category=crawler.category
            )

            if not force_recrawl and repository.exists_by_url(url=url):
                logger.info(f"Skipping {url}. Already exists")
                return CrawlStatus.SKIPPED

            data = crawler.extract(url=url, user_id=user_id)
            repository.save(data)
            return CrawlStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Error while crawling {url=}: \n{e}")
            return CrawlStatus.FAILED

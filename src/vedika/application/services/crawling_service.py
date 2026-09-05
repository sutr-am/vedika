# src/vedika/application/services/crawling_service.py

from uuid import UUID

from loguru import logger

from vedika.application.interfaces.crawlers import BaseCrawlerRouter
from vedika.application.interfaces.providers import BaseRepositoryProvider
from vedika.application.interfaces.repositories import BaseCrawlRepository, BaseRawRepository
from vedika.domain.sources import CrawlDomain
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
        user_id: UUID,
        force_recrawl: bool = False,
    ) -> CrawlStatus:
        crawl_repository: BaseCrawlRepository | None = None
        crawl_id: UUID | None = None
        try:
            crawler = self._crawler_router.get_crawler(url=url)
            raw_repository: BaseRawRepository = self._repository_provider.get_raw_repository(
                category=crawler.category
            )
            source_repository = self._repository_provider.get_source_repository()
            crawl_repository = self._repository_provider.get_crawl_repository()
            canonical_url = crawler.canonicalize_url(url)
            source = source_repository.get_or_create(
                user_id=user_id,
                provider=crawler.provider,
                canonical_url=canonical_url,
            )
            selected_ref = crawler.get_ref(url)
            revision = crawler.get_revision(canonical_url, selected_ref)

            existing_crawl = crawl_repository.get_successful_crawl(
                source_id=source.id, revision=revision, crawler_version=crawler.version
            )
            crawl_data_exists = existing_crawl is not None and raw_repository.has_crawl_documents(
                crawl_id=existing_crawl.id, expected_count=existing_crawl.document_count
            )

            if crawl_data_exists and not force_recrawl:
                logger.info(f"Skipping {canonical_url} at revision {revision}. Already crawled")
                return CrawlStatus.SKIPPED

            if existing_crawl:
                crawl_repository.mark_running(existing_crawl.id)
                crawl = existing_crawl
            else:
                crawl_data = {
                    "source_id": source.id,
                    "requested_url": url,
                    "canonical_url": canonical_url,
                    "selected_ref": selected_ref,
                    "revision": revision,
                    "crawler_version": crawler.version,
                    "status": CrawlStatus.RUNNING,
                }
                crawl = crawl_repository.get_or_create(CrawlDomain(**crawl_data))

            crawl_id = crawl.id
            documents = crawler.extract(
                canonical_url=canonical_url,
                ref=selected_ref,
                user_id=user_id,
                source_id=source.id,
                crawl_id=crawl.id,
            )
            raw_repository.replace_crawl_documents(crawl_id=crawl.id, documents=documents)
            crawl_repository.mark_succeeded(crawl_id=crawl.id, document_count=len(documents))
            return CrawlStatus.SUCCESS
        except Exception as e:
            logger.exception(f"Error while crawling {url=}: \n{e}")
            if crawl_repository and crawl_id:
                crawl_repository.mark_failed(crawl_id=crawl_id, error_message=str(e))
            return CrawlStatus.FAILED

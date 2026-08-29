# src/vedika/application/bootstrap/container.py
from vedika.application.services.crawling_service import CrawlerService
from vedika.infrastructure.crawlers.factory import build_crawler_router
from vedika.infrastructure.db.mongo.connection import MongoDatabaseConnector
from vedika.infrastructure.db.providers import RepositoryProvider
from vedika.settings import Settings


class ApplicationContainer:
    def __init__(self, settings: Settings) -> None:
        self.mongo_connector = MongoDatabaseConnector(settings=settings)
        self.repository_provider = RepositoryProvider(
            settings=settings, mongo_connector=self.mongo_connector
        )
        self.crawler_router = build_crawler_router(github_token=settings.github_token)
        self.crawler_service = CrawlerService(
            crawler_router=self.crawler_router, repository_provider=self.repository_provider
        )

# src/vedika/application/bootstrap/container.py
from vedika.application.services.crawling_service import CrawlerService
from vedika.infrastructure.crawlers.factory import build_crawler_router
from vedika.infrastructure.db.mongo.connection import MongoDatabaseConnector
from vedika.infrastructure.db.providers import RepositoryProvider
from vedika.settings import Settings


class ApplicationContainer:
    """
    This the main app-container which hosts various assets
    necessary for differnt parts of the application.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        ############# ASSETS ##########################
        #############
        # The mongo connector (used to query, fetch, dump data to/from DB)
        self.mongo_connector = MongoDatabaseConnector(settings=settings)

        # The repository provider which gives various repositories
        # for saving different types of users, cralwed data
        self.repository_provider = RepositoryProvider(
            settings=settings, mongo_connector=self.mongo_connector
        )

        ############# The Services ##########################
        self._crawler_service: CrawlerService | None = None  # Crawling Service

        ############# The Cleaning Service ##########################
        ############# The Chunking Service ##########################
        ############# The Embedding Service ##########################
        ############# The Retrieving Service ##########################

    @property
    def crawler_service(self) -> CrawlerService:
        if self._crawler_service is None:
            router = build_crawler_router(settings=self.settings)
            self._crawler_service = CrawlerService(
                crawler_router=router, repository_provider=self.repository_provider
            )
        return self._crawler_service

# src/vedika/application/interfaces/providers.py
from abc import ABC, abstractmethod

from vedika.application.interfaces.repositories import (
    # BaseCleanedRepository,
    BaseCrawlRepository,
    BaseRawRepository,
    BaseRepository,
    BaseSourceRepository,
    BaseUserRepository,
)
from vedika.domain.types import DataCategory, DataState


class BaseRepositoryProvider(ABC):
    """This class provides various types of repositories for downstream tasks"""

    @abstractmethod
    def get_user_repository(self) -> BaseUserRepository:
        """Returns the User Repository; which is used to fetch/dump user data"""
        pass

    @abstractmethod
    def get_source_repository(self) -> BaseSourceRepository:
        """Returns the Source Repository; which is used to fetch/dump Source information"""
        pass

    @abstractmethod
    def get_crawl_repository(self) -> BaseCrawlRepository:
        """
        Returns the Crawl Repository; which is used to fetch/dump Crawl information
        (not the actual data that was crawled)
        """
        pass

    @abstractmethod
    def get_repository(self, category: DataCategory, state: DataState) -> BaseRepository:
        """Returns the various types of Repository; which are used to fetch/dump content data"""
        pass

    @abstractmethod
    def get_raw_repository(self, category: DataCategory) -> BaseRawRepository:
        """It's a utility method to return the repository for RAW data-class to fetch/dump data"""
        pass

    # @abstractmethod
    # def get_cleaned_repository(self, category: DataCategory) -> BaseCleanedRepository:
    #     pass

# src/vedika/application/interfaces/providers.py
from abc import ABC, abstractmethod

from vedika.application.interfaces.repositories import (
    BaseCleanedRepository,
    BaseRawRepository,
    BaseRepository,
    BaseUserRepository,
)
from vedika.domain.types import DataCategory, DataState


class BaseRepositoryProvider(ABC):
    @abstractmethod
    def get_user_repository(self) -> BaseUserRepository:
        pass

    @abstractmethod
    def get_repository(self, category: DataCategory, state: DataState) -> BaseRepository:
        pass

    @abstractmethod
    def get_raw_repository(self, category: DataCategory) -> BaseRawRepository:
        pass

    @abstractmethod
    def get_cleaned_repository(self, category: DataCategory) -> BaseCleanedRepository:
        pass

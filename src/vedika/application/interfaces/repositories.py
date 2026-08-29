# src/vedika/application/interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseRawDomain
from vedika.domain.sources import CrawlDomain, SourceDomain
from vedika.domain.users import UserDomain

# A generic type that is of DocumentDomain or its subclass
RawT = TypeVar("RawT", bound=BaseRawDomain)
UserT = TypeVar("UserT", bound=UserDomain)
CleanT = TypeVar("CleanT", bound=BaseCleanedDomain)


class BaseUserRepository(Generic[UserT], ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> UserT:
        pass


class BaseRepository(ABC):
    pass


class BaseRawRepository(Generic[RawT], BaseRepository):
    @abstractmethod
    def exists_by_url(self, url: str) -> bool:
        pass

    @abstractmethod
    def save(self, document: RawT) -> None:
        pass

    @abstractmethod
    def replace_crawl_documents(self, crawl_id: UUID, documents: list[RawT]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[RawT]:
        pass


class BaseSourceRepository(ABC):
    @abstractmethod
    def get_or_create(self, user_id: UUID, provider: str, canonical_url: str) -> SourceDomain:
        pass


class BaseCrawlRepository(ABC):
    @abstractmethod
    def get_successful(
        self, source_id: UUID, revision: str, crawler_version: str
    ) -> CrawlDomain | None:
        pass

    @abstractmethod
    def get_or_create(self, crawl: CrawlDomain) -> CrawlDomain:
        pass

    @abstractmethod
    def mark_succeeded(self, crawl_id: UUID, document_count: int) -> None:
        pass

    @abstractmethod
    def mark_failed(self, crawl_id: UUID, error_message: str) -> None:
        pass


class BaseCleanedRepository(Generic[CleanT], BaseRepository):
    @abstractmethod
    def exists_by_id(self, document_id: UUID) -> bool:
        pass

    @abstractmethod
    def save(self, document: CleanT) -> None:
        pass

    @abstractmethod
    def get_by_id(self, document_id: UUID) -> CleanT | None:
        pass

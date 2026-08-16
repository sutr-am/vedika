from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from vedika.domain.chunked import BaseChunkDomain
from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseContentDomain, UserDomain

# A generic type that is of DocumentDomain or its subclass
ContentDomainType = TypeVar("ContentDomainType", bound=BaseContentDomain)
UserDomainType = TypeVar("UserDomainType", bound=UserDomain)
CleanedDomainType = TypeVar("CleanedDomainType", bound=BaseCleanedDomain)


C = TypeVar("C", bound=BaseChunkDomain)


class BaseContentRepository(Generic[ContentDomainType], ABC):
    @abstractmethod
    def exists_by_url(self, url: str) -> bool:
        """Check if a document is already stored without fetching the full payload."""
        pass

    @abstractmethod
    def save(self, document: ContentDomainType) -> None:
        """Saves a document to the underlying storage"""
        pass


class BaseUserRepository(Generic[UserDomainType], ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomainType:
        pass


class BaseCleanedRepository(Generic[CleanedDomainType], ABC):
    @abstractmethod
    def exists_by_id(self, document_id: UUID) -> bool:
        """Checks if a cleaned document already exists by its original **document_id**"""
        pass

    @abstractmethod
    def save(self, document: CleanedDomainType) -> None:
        """Saves a cleaned document to its storage"""
        pass

    @abstractmethod
    def get_by_id(self, document_id: UUID) -> CleanedDomainType | None:
        """Fetches a cleaned domain document by its ID"""
        pass


class BaseVectorRepository(Generic[C], ABC):
    @abstractmethod
    def save(self, chunk: C) -> None:
        """Saves a chunk to the vector storage"""
        pass

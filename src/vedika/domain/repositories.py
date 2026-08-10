from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from vedika.domain.chunks import BaseChunkDomain
from vedika.domain.documents import BaseContentDomain, UserDomain

# A generic type that is of DocumentDomain or its subclass
T = TypeVar("T", bound=BaseContentDomain)
U = TypeVar("U", bound=UserDomain)
C = TypeVar("C", bound=BaseChunkDomain)


class BaseContentRepository(Generic[T], ABC):
    @abstractmethod
    def exists_by_url(self, url: str) -> bool:
        """Check if a document is already stored without fetching the full payload."""
        pass

    @abstractmethod
    def save(self, document: T) -> None:
        """Saves a document to the underlying storage"""
        pass


class BaseUserRepository(Generic[U], ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> U:
        pass


class BaseVectorRepository(Generic[C], ABC):
    @abstractmethod
    def save(self, chunk: C) -> None:
        """Saves a chunk to the vector storage"""
        pass

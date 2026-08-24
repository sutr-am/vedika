# src/vedika/application/interfaces/repositories.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseRawDomain
from vedika.domain.users import UserDomain

# A generic type that is of DocumentDomain or its subclass
RawT = TypeVar("RawT", bound=BaseRawDomain)
UserT = TypeVar("UserT", bound=UserDomain)
CleanT = TypeVar("CleanT", bound=BaseCleanedDomain)


class BaseUserRepository(Generic[UserT], ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> UserT:
        pass


class BaseRawRepository(Generic[RawT], ABC):
    @abstractmethod
    def exists_by_url(self, url: str) -> bool:
        """Check if a document is already stored without fetching the full payload."""
        pass

    @abstractmethod
    def save(self, document: RawT) -> None:
        """Saves a document to the underlying storage"""
        pass

    @abstractmethod
    def get_all(self) -> list[RawT]:
        """Fetches all documents from repository"""
        pass


class BaseCleanedRepository(Generic[CleanT], ABC):
    @abstractmethod
    def exists_by_id(self, document_id: UUID) -> bool:
        """Checks if a cleaned document already exists by its original **document_id**"""
        pass

    @abstractmethod
    def save(self, document: CleanT) -> None:
        """Saves a cleaned document to its storage"""
        pass

    @abstractmethod
    def get_by_id(self, document_id: UUID) -> CleanT | None:
        """Fetches a cleaned domain document by its ID"""
        pass

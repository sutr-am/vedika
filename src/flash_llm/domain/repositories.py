from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from flash_llm.domain.documents import (
    ArticleDocumentDomain,
    CodebaseDocumentDomain,
    DocumentDomain,
    PostDocumentDomain,
    UserDomain,
)

# A generic type that is of DocumentDomain or its subclass
T = TypeVar("T", bound=DocumentDomain)

# A generic type that is of DocumentDomain or its subclass
U = TypeVar("U", bound=UserDomain)


class BaseDocumentRepository(Generic[T], ABC):
    @abstractmethod
    def save(self, document: T) -> None:
        """Saves a document to the underlying storage"""
        pass


class BaseUserRepository(Generic[U], ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> U:
        pass


class DocumentRepository(ABC):
    @abstractmethod
    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        pass

    @abstractmethod
    def save_codebase(self, codebase: CodebaseDocumentDomain) -> None:
        pass

    @abstractmethod
    def save_article(self, article: ArticleDocumentDomain) -> None:
        pass

    @abstractmethod
    def save_post(self, post: PostDocumentDomain) -> None:
        pass

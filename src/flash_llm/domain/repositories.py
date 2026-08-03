from abc import ABC, abstractmethod

from flash_llm.domain.documents import (
    ArticleDocumentDomain,
    CodebaseDocumentDomain,
    PostDocumentDomain,
    UserDomain,
)


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

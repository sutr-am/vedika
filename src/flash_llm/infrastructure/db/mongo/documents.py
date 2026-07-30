from abc import ABC
from typing import Optional

from pydantic import UUID4, Field

from flash_llm.domain.types import DataCategory
from flash_llm.infrastructure.db.mongo.base import NoSQLBaseDocument


class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    class Settings:
        collection_name: DataCategory = DataCategory.USERS

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Document(NoSQLBaseDocument, ABC):
    """
    Abstract infrastructure base.
    Mirrors fields in DocumentDomain
    """

    title: str
    link: str
    platfrom: str
    author_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")
    content: str


class CodebaseDocument(Document):
    codebase_name: str

    class Settings:
        collection_name: DataCategory = DataCategory.CODEBASES


class ArticleDocument(Document):
    class Settings:
        collection_name: DataCategory = DataCategory.ARTICLES


class PostDocument(Document):
    image: Optional[str] = None

    class Settings:
        collection_name: DataCategory = DataCategory.POSTS

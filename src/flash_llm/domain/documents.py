from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from flash_llm.domain.types import DataCategory


class UserDomain(BaseModel):
    """Core domain entity representing a user"""

    id: UUID = Field(default_factory=uuid4)
    category: DataCategory = DataCategory.USERS
    first_name: str
    last_name: str
    bio: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class DocumentDomain(BaseModel):
    """Abstract base domain entity for all text-based content"""

    id: UUID = Field(default_factory=uuid4)
    title: str
    category: DataCategory
    source_url: HttpUrl
    platform: str
    author_id: UUID
    author_full_name: str
    content: str

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class CodebaseDocumentDomain(DocumentDomain):
    category: DataCategory = DataCategory.CODEBASES
    name: str


class ArticleDocumentDomain(DocumentDomain):
    category: DataCategory = DataCategory.ARTICLES


class PostDocumentDomain(DocumentDomain):
    category: DataCategory = DataCategory.POSTS
    image: Optional[str]

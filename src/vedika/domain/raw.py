from typing import Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import DataCategory


class UserDomain(BaseModel):
    """Core domain entity representing a user"""

    id: UUID = Field(default_factory=uuid4)
    category: Literal[DataCategory.USERS] = DataCategory.USERS
    first_name: str
    last_name: str
    bio: Optional[str] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class BaseContentDomain(BaseModel):
    """Abstract base domain entity for all text-based content"""

    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    category: DataCategory
    author_id: UUID
    author_full_name: str

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class CodebaseDomain(BaseContentDomain):
    category: DataCategory = DataCategory.CODEBASES
    name: str


class ArticleDomain(BaseContentDomain):
    category: DataCategory = DataCategory.ARTICLES


class PostDomain(BaseContentDomain):
    category: DataCategory = DataCategory.POSTS
    image: Optional[str]

from abc import ABC
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from vedika.domain.types import DataCategory


class BaseChunkDomain(BaseModel, ABC):
    """Abstract domain entity for all chunks."""

    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    platform: str
    author_id: UUID
    author_full_name: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[list[float]] = None


class CodebaseChunkDomain(BaseChunkDomain):
    category: DataCategory = DataCategory.CODEBASES


class ArticleChunkDomain(BaseChunkDomain):
    category: DataCategory = DataCategory.ARTICLES


class PostChunkDomain(BaseChunkDomain):
    category: DataCategory = DataCategory.POSTS

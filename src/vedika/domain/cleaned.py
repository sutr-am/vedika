# src/vedika/domain/cleaned.py
"""Loads the document after removing the noise from the document"""

from abc import ABC
from uuid import UUID

from pydantic import BaseModel, HttpUrl

from vedika.domain.types import DataCategory, DataState


class BaseCleanedDomain(BaseModel, ABC):
    """Abstract domain entity for a cleaned, full-length document"""

    id: UUID
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID
    category: DataCategory
    state: DataState = DataState.CLEANED

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class CodebaseCleanedDomain(BaseCleanedDomain):
    """Cleaned state specific to a codebase"""

    category: DataCategory = DataCategory.CODEBASES

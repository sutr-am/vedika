# src/vedika/domain/cleaned.py

from uuid import UUID

from pydantic import BaseModel, HttpUrl

from vedika.domain.types import DataCategory, DataState


class BaseCleanedDomain(BaseModel):
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
    category: DataCategory = DataCategory.CODEBASES

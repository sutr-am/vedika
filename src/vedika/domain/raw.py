# src/vedika/domain/raw.py
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import DataCategory, DataState


class BaseRawDomain(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID
    category: DataCategory
    state: DataState = DataState.RAW

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class CodebaseRawDomain(BaseRawDomain):
    category: DataCategory = DataCategory.CODEBASES

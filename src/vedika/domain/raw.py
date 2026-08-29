# src/vedika/domain/raw.py
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import DataCategory, DataState


class BaseRawDomain(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    crawl_id: UUID
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID
    repository_path: str
    upstream_file_sha: str
    content_sha256: str
    category: DataCategory
    state: DataState = DataState.RAW

    @property
    def word_count(self) -> int:
        return len(self.content.split())


class CodebaseRawDomain(BaseRawDomain):
    category: DataCategory = DataCategory.CODEBASES

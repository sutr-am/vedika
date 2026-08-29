# src/vedika/infrastructure/db/mongo/models.py
import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar

from pydantic import UUID4, AnyUrl, BaseModel, Field, HttpUrl

from vedika.domain.types import DataCategory, DataState

# from vedika.infrastructure.db.mongo.base import BaseMongoDocument

MongoDocT = TypeVar("MongoDocT", bound="BaseMongoDocument")


class BaseMongoDocument(BaseModel, Generic[MongoDocT], ABC):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        # for comparing two databases
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self) -> int:
        # for serialization
        return hash(self.id)

    @classmethod
    def from_mongo(cls: Type[MongoDocT], data: dict[str, Any] | None) -> MongoDocT | None:
        if not data:
            return None
        data = data.copy()
        raw_id = data.pop("_id", None)
        if raw_id is None:
            raise ValueError(f"Mongo document is missing _id => _id = {raw_id}")
        return cls(**{**data, "id": raw_id})

    def to_mongo(self: MongoDocT, **kwargs) -> dict[str, Any]:
        parsed = self.model_dump(
            exclude_unset=kwargs.pop("exclude_unset", False),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))
        data = {k: (str(v) if isinstance(v, (uuid.UUID, AnyUrl)) else v) for k, v in parsed.items()}
        return data


class UserMongoDocument(BaseMongoDocument):
    first_name: str
    last_name: str
    category: DataCategory = DataCategory.USERS

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class SourceMongoDocument(BaseMongoDocument):
    user_id: UUID4
    provider: str
    canonical_url: HttpUrl


class CrawlMongoDocument(BaseMongoDocument):
    source_id: UUID4
    requested_url: HttpUrl
    canonical_url: HttpUrl
    selected_ref: str | None = None
    revision: str
    crawler_version: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    document_count: int = 0
    error_message: str | None = None


class CodebaseRawMongoDocument(BaseMongoDocument):
    source_id: UUID4
    crawl_id: UUID4
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID4
    repository_path: str
    upstream_file_sha: str
    content_sha256: str
    category: DataCategory = DataCategory.CODEBASES
    state: DataState = DataState.RAW


class CodebaseCleanedMongoDocument(BaseMongoDocument):
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID4
    category: DataCategory = DataCategory.CODEBASES
    state: DataState = DataState.CLEANED

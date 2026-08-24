# src/vedika/infrastructure/db/qdrant/base.py
from abc import ABC
from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import UUID4, BaseModel, Field
from qdrant_client.models import PointStruct, Record, VectorStructOutput

T = TypeVar("T", bound="QdrantBaseDocument")


class QdrantBaseDocument(BaseModel, Generic[T], ABC):
    id: UUID4 = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: VectorStructOutput | list[float] | None = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        settings_cls = getattr(cls, "Settings", None)
        if not getattr(settings_cls, "collection_name", None):
            raise TypeError(
                f"{cls.__name__} must define a nested Settings class with 'collection_name' attribute."
            )

    @classmethod
    def get_collection_name(cls) -> str:
        settings_cls = getattr(cls, "Settings", None)
        collection_name = getattr(settings_cls, "collection_name", None)
        if not collection_name:
            raise TypeError(
                f"{cls.__name__} must define a nested Settings class with 'collection_name' attribute."
            )
        return collection_name

    @classmethod
    def from_record(cls: type[T], point: Record) -> T:
        """Maps a Qdrant record back to infrastructure document"""
        _id = UUID(str(point.id))
        payload = point.payload or {}
        vector = point.vector or None
        return cls(id=_id, embedding=vector, **payload)

    def to_point(self: T, **kwargs) -> PointStruct:
        """Maps the infrastructure document to Qdrant PointStruct"""
        parsed = self.model_dump(exclude={"id", "embedding"}, **kwargs)
        _id = str(self.id)
        vector = getattr(self, "embedding", None) or {}
        return PointStruct(id=_id, vector=vector, payload=parsed)

    def save(self: T, **kwargs) -> T | None:
        """Persists the infrastructure document to QDrant"""
        from loguru import logger

        from vedika.infrastructure.db.qdrant.connection import qdrant_connection

        client = qdrant_connection.get_client()
        collection_name = self.get_collection_name()
        point = self.to_point(**kwargs)

        try:
            client.upsert(
                collection_name=collection_name,
                points=[
                    point,
                ],
            )
            logger.success(f"Successfully upsert-ed point into {collection_name=}")
            return self
        except Exception as e:
            logger.error(f"Failed to upsert document in {collection_name=}: {e}")
            return None

import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar

from loguru import logger
from pydantic import UUID4, BaseModel, Field
from pymongo import errors

from flash_llm.infrastructure.db.mongo.connection import connection
from flash_llm.settings import settings

T = TypeVar("T", bound="NoSQLBaseDocument")


class NoSQLBaseDocument(BaseModel, Generic[T], ABC):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        # for comparing two databses
        return isinstance(other, self.__class__) and self.id == other.id

    def __hash__(self) -> int:
        # for serialization
        return hash(self.id)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        settings_cls = getattr(cls, "Settings", None)
        if not getattr(settings_cls, "collection_name", None):
            raise TypeError(
                f"{cls.__name__} must define a nested Settings class with 'collection_name' attribute."
            )

    @classmethod
    def _sanitize_filters(cls, filter_options: dict[str, Any]) -> dict[str, Any]:
        sanitized: dict[str, Any] = {}
        for key, value in filter_options.items():
            target_key = "_id" if key == "id" else key
            sanitized[target_key] = str(value) if isinstance(value, uuid.UUID) else value
        return sanitized

    @classmethod
    def _get_database(cls):
        return connection.get_database(settings.mongo.db_name)

    @classmethod
    def _get_collection(cls):
        return cls._get_database()[cls.get_collection_name()]

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
    def from_mongo(cls: Type[T], data: dict[str, Any] | None) -> T | None:
        if not data:
            return None
        data = data.copy()
        raw_id = data.pop("_id", None)
        if raw_id is None:
            raise ValueError(f"Mongo document is missing _id => _id = {raw_id}")
        return cls(**{**data, "id": raw_id})

    def to_mongo(self: T, **kwargs) -> dict[str, Any]:
        parsed = self.model_dump(
            exclude_unset=kwargs.pop("exclude_unset", False),
            by_alias=kwargs.pop("by_alias", True),
            **kwargs,
        )

        if "_id" not in parsed and "id" in parsed:
            parsed["_id"] = str(parsed.pop("id"))
        data = {k: (str(v) if isinstance(v, uuid.UUID) else v) for k, v in parsed.items()}
        return data

    def save(self: T, **kwargs) -> T | None:
        collection = self._get_collection()
        mongo_doc = self.to_mongo(**kwargs)
        doc_id = mongo_doc.get("_id")
        self.updated_at = datetime.now(timezone.utc)

        if not doc_id:
            logger.error(f"Cannot save document of type {self.__class__.__name__} without an id.")
            return None

        try:
            result = collection.replace_one({"_id": doc_id}, mongo_doc, upsert=True)
            if result.acknowledged:
                logger.success(f"Save was acknowledged for ID = {doc_id}")
                return self
            logger.warning(f"Save was NOT acknowledge for ID = {doc_id}")
            return None
        except errors.PyMongoError:
            logger.exception(
                f"Failed to save document of type {self.__class__.__name__} with ID = {doc_id}"
            )
            return None

    @classmethod
    def find(cls: type[T], **filter_options) -> T | None:
        collection = cls._get_collection()
        sanitized_filters = cls._sanitize_filters(filter_options=filter_options)
        try:
            instance = collection.find_one(sanitized_filters)
        except errors.OperationFailure:
            logger.exception(f"Failed to retrieve document of type {cls.__name__}")
            return None
        return cls.from_mongo(instance) if instance else None

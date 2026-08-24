# src/vedika/infrastructure/db/mongo/base.py
import uuid
from abc import ABC
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar

from loguru import logger
from pydantic import UUID4, AnyUrl, BaseModel, Field
from pymongo import errors

from vedika.infrastructure.db.mongo.connection import mongo_connection

MongoDocT = TypeVar("MongoDocT", bound="BaseMongoDocument")


class BaseMongoDocument(BaseModel, Generic[MongoDocT], ABC):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __eq__(self, other: object) -> bool:
        # for comparing two databases
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
        # Fetch all valid field names from the Pydantic model
        valid_fields = set(cls.model_fields.keys())
        valid_fields.add(
            "_id"
        )  # Add MongoDB's internal _id just in case we ever query by it explicitly
        for key, value in filter_options.items():
            if key not in valid_fields:
                raise ValueError(
                    f"Invalid query field: {key=}.\nValid fields for {cls.__name__} are: \n{valid_fields}\n"
                )
            target_key = "_id" if key == "id" else key
            sanitized[target_key] = str(value) if isinstance(value, (uuid.UUID, AnyUrl)) else value
        return sanitized

    @classmethod
    def _get_database(cls):
        connection_name = cls.get_connection_name()
        return mongo_connection.get_database(connection_name=connection_name)

    @classmethod
    def _get_collection(cls):
        collection_name = cls.get_collection_name()
        return cls._get_database()[collection_name]

    @classmethod
    def get_connection_name(cls) -> str:
        settings_cls = getattr(cls, "Settings", None)
        connection_name = getattr(settings_cls, "connection_name", None)
        if not connection_name:
            raise TypeError(
                f"{cls.__name__} must define a nested 'Settings' class with 'connection_name' attribute."
            )
        return connection_name

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
    def find(cls: type[MongoDocT], **filter_options) -> MongoDocT | None:
        collection = cls._get_collection()
        sanitized_filters = cls._sanitize_filters(filter_options=filter_options)
        try:
            instance = collection.find_one(sanitized_filters)
        except errors.OperationFailure:
            logger.exception(f"Failed to retrieve document of type {cls.__name__}")
            return None
        return cls.from_mongo(instance) if instance else None

    @classmethod
    def find_all(cls: type[MongoDocT], **filter_options) -> list[MongoDocT] | None:
        collection = cls._get_collection()
        sanitized_filters = cls._sanitize_filters(filter_options=filter_options)
        try:
            cursor = collection.find(sanitized_filters)
            results = []
            for instance in cursor:
                doc = cls.from_mongo(data=instance)
                if doc:
                    results.append(doc)
            return results
        except errors.OperationFailure:
            logger.exception(f"Failed to retrieve document of type {cls.__name__}")
            return []

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

    def save(self: MongoDocT, **kwargs) -> MongoDocT | None:
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

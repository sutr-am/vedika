# src/vedika/infrastructure/db/mongo/models.py
from pydantic import UUID4, HttpUrl

from vedika.domain.types import DataCategory, DataState
from vedika.infrastructure.db.mongo.base import BaseMongoDocument
from vedika.settings import settings


class UserMongoDocument(BaseMongoDocument):
    first_name: str
    last_name: str
    category: DataCategory = DataCategory.USERS

    class Settings:
        _route = settings.storage_routes.users
        if _route:
            connection_name: str = _route.connection
            collection_name: str = _route.target

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CodebaseRawMongoDocument(BaseMongoDocument):
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID4
    category: DataCategory = DataCategory.CODEBASES
    state: DataState = DataState.RAW

    class Settings:
        _route = settings.storage_routes.get_route(
            category_name=DataCategory.CODEBASES.value, state=DataState.RAW.value
        )
        if _route:
            connection_name: str = _route.connection
            collection_name: str = _route.target


class CodebaseCleanedMongoDocument(BaseMongoDocument):
    title: str
    content: str
    platform: str
    source_url: HttpUrl
    user_id: UUID4
    category: DataCategory = DataCategory.CODEBASES
    state: DataState = DataState.CLEANED

    class Settings:
        _route = settings.storage_routes.get_route(
            category_name=DataCategory.CODEBASES.value, state=DataState.CLEANED.value
        )
        if _route:
            connection_name: str = _route.connection
            collection_name: str = _route.target

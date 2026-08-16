from pydantic import UUID4, Field

from vedika.infrastructure.db.mongo.base import NoSQLBaseDocument
from vedika.settings import settings


class UserDocument(NoSQLBaseDocument):
    first_name: str
    last_name: str

    class Settings:
        _route = settings.storage_routes.users
        connection_name: str = _route.connection
        collection_name: str = _route.target

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


class CodebaseDocument(NoSQLBaseDocument):
    title: str
    link: str
    codebase_name: str
    content: str
    platform: str
    author_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")

    class Settings:
        _route = settings.storage_routes.get_route("codebases", "raw")
        connection_name: str = _route.connection
        collection_name: str = _route.target


class CleanedCodebaseDocument(NoSQLBaseDocument):
    content: str
    platform: str
    author_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="author_full_name")

    class Settings:
        _route = settings.storage_routes.get_route("codebases", "cleaned")
        connection_name: str = _route.connection
        collection_name: str = _route.target

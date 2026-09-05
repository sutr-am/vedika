# src/vedika/infrastructure/db/registry.py
from typing import TypeAlias

from vedika.application.interfaces.repositories import (
    # BaseCleanedRepository,
    BaseRawRepository,
    BaseUserRepository,
)
from vedika.domain.types import DataCategory, DataState
from vedika.infrastructure.db.mongo.repositories import (
    # CodebaseCleanedMongoRepository,
    CodebaseRawMongoRepository,
    UserMongoRepository,
)

Repository: TypeAlias = (
    type[BaseUserRepository] | type[BaseRawRepository]  # | type[BaseCleanedRepository]
)

RepositoryKey: TypeAlias = tuple[DataCategory, DataState | None, str]

REPOSITORY_REGISTRY: dict[RepositoryKey, Repository] = {
    (DataCategory.USERS, None, "mongo"): UserMongoRepository,
    (DataCategory.CODEBASES, DataState.RAW, "mongo"): CodebaseRawMongoRepository,
    # (DataCategory.CODEBASES, DataState.CLEANED, "mongo"): CodebaseCleanedMongoRepository,
}

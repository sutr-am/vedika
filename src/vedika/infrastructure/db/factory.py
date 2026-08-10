import os
from typing import Union, cast

from vedika.domain.repositories import (
    BaseContentRepository,
    BaseUserRepository,
    BaseVectorRepository,
)
from vedika.domain.types import DataCategory

# Type alias for the internal cache
_Repository = Union[BaseUserRepository, BaseContentRepository, BaseVectorRepository]
_repository_cache: dict[DataCategory, _Repository] = {}
_vector_repository_cache: dict[DataCategory, _Repository] = {}


def _initialize_repositories() -> None:
    """Internal bootstrapping function."""
    user_db_type = os.getenv("USER_DATABASE_TYPE", "mongo").lower()
    doc_db_type = os.getenv("DOCUMENT_DATABASE_TYPE", "mongo").lower()
    vector_db_type = os.getenv("VECTOR_DATABASE_TYPE", "qdrant").lower()

    if user_db_type == "mongo":
        from vedika.infrastructure.db.mongo.repositories import MongoUserRepository

        _repository_cache[DataCategory.USERS] = MongoUserRepository()
    else:
        raise ValueError(f"Unsupported user database type: {user_db_type=}")

    if doc_db_type == "mongo":
        from vedika.infrastructure.db.mongo.repositories import (
            MongoArticleRepository,
            MongoCodebaseRepository,
            MongoPostRepository,
        )

        _repository_cache[DataCategory.CODEBASES] = MongoCodebaseRepository()
        _repository_cache[DataCategory.ARTICLES] = MongoArticleRepository()
        _repository_cache[DataCategory.POSTS] = MongoPostRepository()
    else:
        raise ValueError(f"Unsupported document database type: {doc_db_type=}")

    if vector_db_type == "qdrant":
        from vedika.infrastructure.db.qdrant.repositories import QdrantCodebaseRepository

        _repository_cache[DataCategory.CODEBASES] = QdrantCodebaseRepository()
    else:
        raise ValueError(f"Unsupported vector databse type: {vector_db_type=}")


# ==========================================
# PUBLIC API (Strictly Typed, No Overloads)
# ==========================================


def get_user_repository() -> BaseUserRepository:
    """Fetches the User repository."""
    if not _repository_cache:
        _initialize_repositories()

    repo = _repository_cache.get(DataCategory.USERS)
    if not repo:
        raise ValueError("User repository failed to initialize.")

    # We cast internally so the consumer never has to worry about it
    return cast(BaseUserRepository, repo)


def get_document_repository(category: DataCategory) -> BaseContentRepository:
    """Fetches the correct Document repository based on the category."""
    if category == DataCategory.USERS:
        raise ValueError("Use get_user_repository() to fetch the User repository.")

    if not _repository_cache:
        _initialize_repositories()

    repo = _repository_cache.get(category)
    if not repo:
        raise ValueError(f"No document repository registered for {category=}")

    # We cast internally so the consumer never has to worry about it
    return cast(BaseContentRepository, repo)


def get_vector_repository(category: DataCategory) -> BaseVectorRepository:
    """fectches the correct Vector repository based on the category"""
    if not _vector_repository_cache:
        _initialize_repositories()

    repo = _vector_repository_cache.get(category)
    if not repo:
        raise ValueError(f"No Vector Repository registered for {category=}")
    return cast(BaseVectorRepository, repo)

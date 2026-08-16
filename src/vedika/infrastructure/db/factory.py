from typing import cast

from loguru import logger

from vedika.domain.repositories import (
    BaseCleanedRepository,
    BaseContentRepository,
    BaseUserRepository,
)
from vedika.domain.types import DataCategory
from vedika.infrastructure.db.mongo.repositories import (
    MongoCleanedCodebaseRepository,
    MongoCodebaseRepository,
    MongoUserRepository,
)
from vedika.settings import settings

# Type alias for the internal cache
# _Repository = Union[BaseUserRepository, BaseContentRepository, BaseVectorRepository]


# Dedicated repository-caches for each state
_user_repository_cache: dict[DataCategory, BaseUserRepository] = {}
_raw_repository_cache: dict[DataCategory, BaseContentRepository] = {}
_cleaned_repository_cache: dict[DataCategory, BaseCleanedRepository] = {}

# Registry map for each state's (category, driver) combo
_USER_REGISTRY = {(DataCategory.USERS, "mongo"): MongoUserRepository}
_RAW_REGISTRY = {(DataCategory.CODEBASES, "mongo"): MongoCodebaseRepository}
_CLEANED_REGISTRY = {(DataCategory.CODEBASES, "mongo"): MongoCleanedCodebaseRepository}


def _get_driver_for_connection(connection_name: str) -> str:
    conn_config = settings.connections.get(connection_name)
    if not conn_config:
        raise ValueError(
            f"Connection profile '{connection_name=}' not found in settings.connections"
        )
    return conn_config.driver


def _initialize_repositories() -> None:
    """Dynamically bootstrap repositories based on settings.storage_routes"""

    #####---- USER Repositories
    user_connection_name = settings.storage_routes.users.connection
    user_driver = _get_driver_for_connection(connection_name=user_connection_name)
    user_repo_class = _USER_REGISTRY.get((DataCategory.USERS, user_driver))
    if user_repo_class:
        _user_repository_cache[DataCategory.USERS] = user_repo_class()

    ###### Document Repositories
    for category, category_route in settings.storage_routes.categories.items():
        try:
            category = DataCategory(category)
        except ValueError:
            logger.error(
                f"Category '{category=}' in YAML is not a valid DaatCategory enum. Skipping"
            )
            continue

        ###---- RAW Repositories ----
        if getattr(category_route, "raw", None):
            connection_name = category_route.raw.connection
            driver = _get_driver_for_connection(connection_name=connection_name)
            repo_class = _RAW_REGISTRY.get((category, driver))
            if repo_class:
                _raw_repository_cache[category] = repo_class()
            else:
                logger.warning(
                    f"No RAW repository implementation found for {category=} & {driver=}"
                )

        ###------ CLEANED Repositories
        if getattr(category_route, "cleaned", None):
            connection_name = category_route.cleaned.connection
            driver = _get_driver_for_connection(connection_name=connection_name)
            repo_class = _CLEANED_REGISTRY.get((category, driver))
            if repo_class:
                _cleaned_repository_cache[category] = repo_class()
            else:
                logger.warning(
                    f"No RAW repository implementation found for {category=} & {driver=}"
                )


# ==========================================
# PUBLIC API
# ==========================================


def get_user_repository(category: DataCategory = DataCategory.USERS) -> BaseUserRepository:
    """Fetches the User repository."""
    if not _user_repository_cache:
        _initialize_repositories()

    repo = _user_repository_cache.get(category)
    if not repo:
        raise ValueError("User repository failed to initialize.")

    # We cast internally so the consumer never has to worry about it
    return cast(BaseUserRepository, repo)


def get_raw_repository(category: DataCategory) -> BaseContentRepository:
    """Fetches the correct Document repository based on the category."""
    if not _raw_repository_cache:
        _initialize_repositories()

    repo = _raw_repository_cache.get(category)
    if not repo:
        raise ValueError(f"No RAW repository registered for {category=}")

    # We cast internally so the consumer never has to worry about it
    return cast(BaseContentRepository, repo)


def get_cleaned_repository(category: DataCategory) -> BaseCleanedRepository:
    """fectches the correct Vector repository based on the category"""
    if not _cleaned_repository_cache:
        _initialize_repositories()

    repo = _cleaned_repository_cache.get(category)
    if not repo:
        raise ValueError(f"No CLEANED Repository registered for {category=}")
    return cast(BaseCleanedRepository, repo)

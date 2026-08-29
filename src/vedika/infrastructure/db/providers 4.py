# src/vedika/infrastructure/db/providers.py
from typing import Any, cast

from vedika.application.interfaces.providers import BaseRepositoryProvider
from vedika.application.interfaces.repositories import (
    BaseCleanedRepository,
    BaseRawRepository,
    BaseRepository,
    BaseUserRepository,
)
from vedika.domain.types import DataCategory, DataState
from vedika.infrastructure.db.mongo.connection import MongoDatabaseConnector
from vedika.infrastructure.db.registry import REPOSITORY_REGISTRY
from vedika.settings import Settings


class RepositoryProvider(BaseRepositoryProvider):
    def __init__(
        self,
        settings: Settings,
        mongo_connector: MongoDatabaseConnector,
        # qdrant_connector: QdrantDatabaseConnector | None = None,
    ) -> None:
        self._mongo_connector: MongoDatabaseConnector | None = mongo_connector
        # self._qdrant_connector: QdrantDatabaseConnector | None = qdrant_connector
        self._user_repository: BaseUserRepository | None = None
        self._repositories: dict[tuple[DataCategory, DataState], BaseRepository] = {}
        self._build_repositories(settings=settings)

    def get_user_repository(self) -> BaseUserRepository:
        if self._user_repository is None:
            raise ValueError("No user repository configured.")
        return self._user_repository

    def get_repository(self, category: DataCategory, state: DataState) -> BaseRepository:
        try:
            return self._repositories[(category, state)]
        except KeyError as error:
            raise ValueError(f"No repository configured for {category=}, {state=}") from error

    def get_raw_repository(self, category: DataCategory) -> BaseRawRepository:
        return cast(BaseRawRepository, self.get_repository(category=category, state=DataState.RAW))

    def get_cleaned_repository(self, category: DataCategory) -> BaseCleanedRepository:
        return cast(
            BaseCleanedRepository, self.get_repository(category=category, state=DataState.CLEANED)
        )

    def _build_mongo_repository(self, repository_class: type, connection: str, target: str):
        if self._mongo_connector:
            client = self._mongo_connector.get_client(connection_name=connection)
            db_name = self._mongo_connector.get_db_name(connection_name=connection)
            return repository_class(client=client, db_name=db_name, target=target)
        else:
            return None

    def _build_repository(
        self,
        *,
        category: DataCategory,
        state: DataState | None,
        connection: str,
        target: str,
        settings: Settings,
    ) -> Any:
        connection_config = settings.connections.get(connection)
        if connection_config is None:
            raise ValueError(f"No connection configured for {connection=}")

        driver = connection_config.driver

        repository_class = REPOSITORY_REGISTRY.get((category, state, driver))
        if repository_class is None:
            raise ValueError(f"No repository registered for {category=}, {state=}, {driver=}")

        # route the instantiation based on the driver type
        if driver == "mongo":
            return self._build_mongo_repository(
                repository_class=repository_class, connection=connection, target=target
            )
        else:
            raise ValueError(f"Unsupported database driver: {driver=}")

    def _build_repositories(self, settings: Settings) -> None:
        user_route = settings.storage_routes.users

        self._user_repository = self._build_repository(
            category=DataCategory.USERS,
            state=None,
            connection=user_route.connection,
            target=user_route.target,
            settings=settings,
        )

        for category_name, state_routes in settings.storage_routes.categories.items():
            category = DataCategory(category_name)

            for state_name, route in state_routes.items():
                state = DataState(state_name)

                repository = self._build_repository(
                    category=category,
                    state=state,
                    connection=route.connection,
                    target=route.target,
                    settings=settings,
                )
                self._repositories[(category, state)] = repository

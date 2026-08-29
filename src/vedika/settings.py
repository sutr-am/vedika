# src/vedika/settings.py
import os
from pathlib import Path
from typing import Any, Self, cast
from urllib.parse import urlparse

from dotenv import load_dotenv
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel, Field, ValidationError, field_validator

from vedika.domain.types import DataCategory, DataState

# 1. Load environment variables from .env file FIRST
load_dotenv()

# 2. Register the environment resolver
# Note: replace=True ensures it doesn't throw an error if this module is reloaded
OmegaConf.register_new_resolver(
    name="oc.env",
    resolver=lambda key, default="": os.environ.get(key, default),
    replace=True,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = PROJECT_ROOT / "configs"


###########################################################
class ConnectionConfig(BaseModel):
    driver: str = Field(..., pattern="^(mongo|postgres|qdrant)$")
    host: str | None = None
    db_name: str | None = None
    path: str | None = None

    def __repr__(self) -> str:
        # Mask secrets in repr
        return (
            f"ConnectionConfig(driver={self.driver!r}, "
            f"host=*****, db_name={self.db_name!r}, path={self.path!r})"
        )

    def model_dump(self, **kwargs) -> dict[str, Any]:
        # Pydantic's dump method also masks
        return {
            "driver": self.driver,
            "host": "*****" if self.host else None,
            "db_name": self.db_name,
            "path": self.path,
        }

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str | None) -> str | None:
        if v is None:
            return v
        try:
            parsed = urlparse(v)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Missing scheme or netloc")
            if parsed.scheme not in ("mongodb", "postgres", "http", "https"):
                raise ValueError(f"Unsupported scheme: {parsed.scheme}")
        except Exception as e:
            raise ValueError(f"Invalid connection URI: {v}") from e
        return v


class StateRouteConfig(BaseModel):
    connection: str = Field(..., min_length=1)
    target: str = Field(..., min_length=1)

    @field_validator("connection")
    @classmethod
    def validate_connection_name(cls, v):
        if not v or len(v) > 255:
            raise ValueError("connection name must be 1-255 characters")
        # Note: can't validate it exists here without all_connections
        # That's why validate_connections() still exists
        return v


class StorageRouteConfig(BaseModel):
    users: StateRouteConfig
    sources: StateRouteConfig
    crawls: StateRouteConfig
    categories: dict[DataCategory, dict[DataState, StateRouteConfig]]

    @field_validator("categories")
    @classmethod
    def validate_categories_not_empty(cls, v):
        if not v:
            raise ValueError("At least one category must be configured")
        return v

    def validate_connections(self, all_connections: dict[str, ConnectionConfig]) -> None:
        # Validate user route
        if self.users.connection not in all_connections:
            raise ValueError(f"User route references unknown connection: {self.users.connection}")
        for route_name, route in (("source", self.sources), ("crawl", self.crawls)):
            if route.connection not in all_connections:
                raise ValueError(
                    f"{route_name} route references unknown connection: {route.connection}"
                )

        # Validate category routes
        for category, states in self.categories.items():
            for state, route in states.items():
                if route.connection not in all_connections:
                    raise ValueError(
                        f"Route {category}/{state} references unknown connection: "
                        f"{route.connection}"
                    )


class Settings(BaseModel):
    """
    Application configuration loaded from YAML.

    Config structure:
    ```yaml
    connections:
        <connection-name>:
            driver: mongo | postgres | qdrant
            host: connection string
            db_name: database name
        ...

    storage_routes:
        users:
            connection: <connection-name>
            target: <collection-name>
        categories:
            <category>:
            raw:
                connection: <connection-name>
                target: <collection-name>
            cleaned:
                connection: <connection-name>
                target: <collection-name>
    ```

    Environment variables are resolved at load time using ${oc.env:VAR_NAME} syntax.

    Config is loaded in this priority order:
    1. base.yaml (committed to repo)
    2. <environment>.yaml (staging.yaml, prod.yaml)
    3. local.yaml (local overrides, not committed)
    """

    connections: dict[str, ConnectionConfig] = Field(default_factory=dict)
    storage_routes: StorageRouteConfig
    github_token: str | None = None
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "local"))

    @classmethod
    def load_settings(cls, env: str | None = None, config_name: str = "base.yaml") -> Self:
        if env is None:
            env = os.getenv("ENVIRONMENT", "local")
        logger.info(f"Loading settings for environment: {env}")

        base_config_path = CONFIGS_DIR / config_name
        env_config_path = CONFIGS_DIR / f"envs/{env}.yaml"

        if env != "local" and not env_config_path.exists():
            raise FileNotFoundError(
                f"Environment config for '{env}' not found at {env_config_path}. "
                f"Create {env_config_path} or set ENVIRONMENT=local"
            )

        local_config_path = CONFIGS_DIR / "envs/local.yaml"

        # Start with base.yaml
        if not base_config_path.exists():
            logger.error(f"Config file not found at {base_config_path}.")
            raise FileNotFoundError(f"Missing configuration: {base_config_path=}")

        cfg = OmegaConf.load(base_config_path)

        # load environment specific config
        if env_config_path.exists():
            logger.info(f"Loading {env} config from {env_config_path=}")
            env_cfg = OmegaConf.load(env_config_path)
            cfg = OmegaConf.merge(cfg, env_cfg)

        # Merge local overides if local.yaml exists. always lowest priority
        if local_config_path.exists():
            logger.info(f"Merging local configuration overrides from {local_config_path}")
            local_cfg = OmegaConf.load(local_config_path)
            cfg = OmegaConf.merge(cfg, local_cfg)

        # Convert OmegaConf object to primitive dict() object and resolve variables
        dict_cfg = OmegaConf.to_container(cfg, resolve=True)
        if not isinstance(dict_cfg, dict):
            raise ValueError(f"Expected dict, got {type(dict_cfg)}")

        # Instantiate and validate via Pydantic
        try:
            dict_cfg_typed: dict[str, Any] = cast(dict[str, Any], dict_cfg)
            settings = cls(**dict_cfg_typed, environment=env)

            # Validate cross-references
            settings.storage_routes.validate_connections(settings.connections)
            logger.info(f"Settings loaded successfully (environment={settings.environment})")
            return settings
        except ValidationError as e:
            logger.error(f"Config validation failed: {e}")
            raise e


# def get_settings() -> Settings:
#     return Settings.load_settings()

_SETTINGS_CACHE: Settings | None = None


def get_settings(reload: bool = False) -> Settings:
    global _SETTINGS_CACHE
    if reload or _SETTINGS_CACHE is None:
        _SETTINGS_CACHE = Settings.load_settings()
        logger.info(f"Settings loaded from disk (environment={_SETTINGS_CACHE.environment})")
    return _SETTINGS_CACHE


def reset_settings_cache() -> None:
    """For testing; clears the cached settings."""
    global _SETTINGS_CACHE
    _SETTINGS_CACHE = None

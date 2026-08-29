# src/vedika/settings.py
import os
from pathlib import Path
from typing import Any, Self

from dotenv import load_dotenv
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel

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
    driver: str
    host: str | None = None
    db_name: str | None = None
    path: str | None = None


class StateRouteConfig(BaseModel):
    connection: str
    target: str


class StorageRouteConfig(BaseModel):
    users: StateRouteConfig
    categories: dict[DataCategory, dict[DataState, StateRouteConfig]]


class Settings(BaseModel):
    connections: dict[str, ConnectionConfig]
    storage_routes: StorageRouteConfig
    github_token: str | None = None

    @classmethod
    def load_settings(cls, config_name: str = "base.yaml") -> Self:
        base_config_path = CONFIGS_DIR / config_name
        local_config_path = CONFIGS_DIR / "local.yaml"

        # 1. Start with base.yaml
        if not base_config_path.exists():
            logger.error(f"Config file not found at {base_config_path}.")
            raise FileNotFoundError(f"Missing configuration: {base_config_path=}")

        cfg = OmegaConf.load(base_config_path)

        # 2. Merge local overides if local.yaml exists
        if local_config_path.exists():
            logger.info(f"Merging local configuration overrides from {local_config_path}")
            local_cfg = OmegaConf.load(local_config_path)
            cfg = OmegaConf.merge(cfg, local_cfg)

        # 3. Convert OmegaConf object to primitive dict() object and resolve variables
        dict_cfg: dict[str, Any] = OmegaConf.to_container(cfg, resolve=True)  # type: ignore

        # 4. Instantiate and validate via Pydantic
        return cls(**dict_cfg)


def get_settings() -> Settings:
    return Settings.load_settings()


###################################################################
##### OLD code ########
# !!! BUG !!! Singleton Module Instance
# settings = Settings.load_settings()x


# class CategoryRouteConfig(BaseModel):
#     # users: StateRouteConfig
#     # categories: dict[str, dict[DataState, StateRouteConfig]]
#     raw: StateRouteConfig
#     cleaned: StateRouteConfig


# class GithubCredentials(BaseModel):
#     token: str | None = None


# class MediumCredentials(BaseModel):
#     username: str
#     password: str


# class RedditCredentials(BaseModel):
#     client_id: str
#     client_secret: str
#     user_agent: str


# class StorageRouteConfig(BaseModel):
#     users: StateRouteConfig
#     categories: dict[str, CategoryRouteConfig]

#     def get_route(self, category_name: str, state: str) -> StateRouteConfig | None:
#         category_config = self.categories.get(category_name)
#         if not category_config:
#             raise ValueError(f"Category '{category_name}' not found in storage_routes.")

#         # Safely fetch the state (raw, cleaned, etc.)
#         state_config = getattr(category_config, state, None)
#         if not state_config:
#             raise ValueError(f"State '{state}' is missing for category '{category_name}'.")
#         return state_config

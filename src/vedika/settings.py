import os
from pathlib import Path
from typing import Any, Self

from dotenv import load_dotenv
from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel

# 1. Load environment variables from .env file FIRST
load_dotenv()

# 2. Register the environment resolver
# Note: replace=True ensures it doesn't throw an error if this module is reloaded
OmegaConf.register_new_resolver(
    "oc.env", lambda key, default="": os.environ.get(key, default), replace=True
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = PROJECT_ROOT / "configs"


class MongoConfig(BaseModel):
    # Remove hardcoded defaults; Pydantic will now fail if base.yaml doesn't provide these
    host: str
    db_name: str


# class QdrantConfig(BaseModel):
#     host: str
#     port: str


# class QdrantConfig(BaseModel):
#     host: str
#     port: str


class Settings(BaseModel):
    # database_name: Literal["mongo", "qdrant"] = "mongo"
    mongo: MongoConfig
    # qdrant: Optional[QdrantConfig] = None

    @classmethod
    def load_settings(cls, config_name: str = "base.yaml") -> Self:
        base_config_path = CONFIGS_DIR / config_name
        local_config_path = CONFIGS_DIR / "local.yaml"

        # 1. Start with base.yaml
        if not base_config_path.exists():
            logger.warning(
                f"Config file not found at {base_config_path}. Defaulting to Pydantic Settings"
            )
            return cls(
                mongo=MongoConfig(host="", db_name="")
            )  # Fallback #!BUG: should raise error

        cfg = OmegaConf.load(base_config_path)

        # 2. Merge local overides if local.yaml exists
        if local_config_path.exists():
            logger.info(
                f"Merging local configuration overrides from {local_config_path}"
            )
            local_cfg = OmegaConf.load(local_config_path)
            cfg = OmegaConf.merge(cfg, local_cfg)

        # 3. Convert OmegaConf object to primitive dict() object and resolve variables in interpolation
        dict_cfg: dict[str, Any] = OmegaConf.to_container(cfg, resolve=True)  # type: ignore

        # 4. Instantiate and validate via Pydantic
        return cls(**dict_cfg)


# Singleton Module Instance
settings = Settings.load_settings()

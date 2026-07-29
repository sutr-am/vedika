from pathlib import Path
from typing import Any, Self

from loguru import logger
from omegaconf import OmegaConf
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIGS_DIR = PROJECT_ROOT / "configs"


class MongoConfig(BaseModel):
    host: str = "mongodb://flash_llm:flash_llm@127.0.0.1:27017"
    db_name: str = "flash_llm"


class Settings(BaseModel):
    mongo: MongoConfig = Field(default_factory=MongoConfig)

    @classmethod
    def load_settings(cls, config_name: str = "base.yaml") -> Self:
        base_config_path = CONFIGS_DIR / config_name
        local_config_path = CONFIGS_DIR / "local.yaml"

        # 1. Start with base.yaml
        if not base_config_path.exists():
            logger.warning(f"Config file not found at {base_config_path}. Defaulting to Pydantic Settings")
            return cls()
        cfg = OmegaConf.load(base_config_path)

        # 2. Merge local overides if local.yaml exists
        if local_config_path.exists():
            logger.info(f"Merging local configuration overrides from {local_config_path}")
            local_cfg = OmegaConf.load(local_config_path)
            cfg = OmegaConf.merge(cfg, local_cfg)

        # 3. Convert OmegaConf object to primitive dict() object and resolve variables in interpolation
        dict_cfg: dict[str, Any] = OmegaConf.to_container(cfg, resolve=True)  # type: ignore

        # 4. Instantiate and validate via Pydantic
        return cls(**dict_cfg)


# Singleton Modeule Instance
settings = Settings.load_settings()

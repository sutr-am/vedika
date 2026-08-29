from pathlib import Path

from loguru import logger
from omegaconf import OmegaConf

from vedika.orchestration.pipelines.etl import extract_transform_load

if __name__ == "__main__":
    master_config_path = Path("configs/etl_run_config.yaml")
    if not master_config_path.exists():
        raise FileNotFoundError(f"Master ETL config file not found at {master_config_path}")

    master_cfg = OmegaConf.load(master_config_path)
    active_configs: list = master_cfg.active_user_configs

    # 1. Identify active user-configs to be processed
    for cfg_file in active_configs:
        cfg_path = Path(cfg_file)
        if not cfg_path.exists():
            logger.warning(f"Config file {cfg_path} does not exist. Skipping...")
            continue
        cfg = OmegaConf.load(cfg_path)
        logger.info(f"🚀 Triggering the Digital Data ETL Pipeline... for {cfg_path=}")

        # 2. Trigger the Pipeline
        # 2.a: ETL pipeline
        extract_transform_load.with_options(enable_cache=False)(
            user_first_name=cfg.parameters.user_first_name,
            user_last_name=cfg.parameters.user_last_name,
            links=list(cfg.parameters.links),
        )

        logger.info(f"\n\n{'---' * 30}\n")

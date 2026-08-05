from pathlib import Path

from loguru import logger
from omegaconf import OmegaConf

from flash_llm.orchestration.pipelines.etl import digital_data_etl

if __name__ == "__main__":
    master_config_path = Path("configs/etl_run_config.yaml")
    if not master_config_path:
        raise FileNotFoundError(f"Master ETL config file not found at {master_config_path}")

    master_cfg = OmegaConf.load(master_config_path)
    active_configs: list = master_cfg.active_user_configs
    for cfg_file in active_configs:
        cfg_path = Path(cfg_file)
        if not cfg_path.exists():
            logger.warning(f"Config file {cfg_path} does not exist. Skipping...")
            continue
        cfg = OmegaConf.load(cfg_path)
        logger.info(f"🚀 Triggering the Digital Data ETL Pipeline... for {cfg_path=}")
        digital_data_etl.with_options(enable_cache=False)(
            user_full_name=cfg.parameters.user_full_name,
            links=list(cfg.parameters.links),
        )
        logger.info(f"\n\n{'---'*30}\n")

    print("✅ Pipeline execution finished!")

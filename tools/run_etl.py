import os

from omegaconf import OmegaConf

from flash_llm.orchestration.pipelines.etl import digital_data_etl

if __name__ == "__main__":
    os.environ["DATABASE_TYPE"] = "mongo"

    # Load parameters from the YAML configuration
    config_path = "configs/etl.yaml"
    cfg = OmegaConf.load(config_path)

    print("🚀 Triggering the Digital Data ETL Pipeline...")

    digital_data_etl.with_options(enable_cache=False)(
        user_full_name=cfg.parameters.user_full_name,
        links=list(cfg.parameters.links),
    )

    print("✅ Pipeline execution finished!")

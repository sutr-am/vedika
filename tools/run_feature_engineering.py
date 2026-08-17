from loguru import logger

from vedika.domain.types import DataCategory
from vedika.orchestration.pipelines.feature_engineering import feature_engineering_pipeline

if __name__ == "__main__":
    logger.info("triggering the Feature Engineering PIepline")
    pipeline_instance = feature_engineering_pipeline.with_options(enable_cache=False)
    pipeline_instance(category=DataCategory.CODEBASES)
    logger.info(f"\n{'---' * 30}\n")

from loguru import logger
from zenml import pipeline

from flash_llm.orchestration.steps.etl import crawl_links, get_or_create_user

logger.info(">>>>>>>>>>>>>")


@pipeline(name="flash_llm_etl")
def digital_data_etl(user_full_name: str, links: list[str]):
    user = get_or_create_user(user_full_name=user_full_name)
    crawl_links(user=user, links=links)

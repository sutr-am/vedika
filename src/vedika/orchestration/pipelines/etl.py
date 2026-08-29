# src/vedika/orchestration/pipelines/etl.py
from zenml import pipeline

from vedika.orchestration.steps.etl import crawl_urls
from vedika.orchestration.steps.users import get_or_create_user


@pipeline(name="VEDIKA_extract_transform_load")
def extract_transform_load(
    user_first_name: str, user_last_name: str, links: list[str], force_recrawl=False
):
    user = get_or_create_user(first_name=user_first_name, last_name=user_last_name)
    crawl_urls(user=user, urls=links, force_recrawl=force_recrawl)

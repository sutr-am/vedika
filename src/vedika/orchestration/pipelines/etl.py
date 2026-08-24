# src/vedika/orchestration/pipelines/etl.py
from zenml import pipeline

from vedika.orchestration.steps.etl import crawl_urls
from vedika.orchestration.steps.users import get_or_create_user


@pipeline(name="vedika_etl")
def digital_data_etl(user_full_name: str, links: list[str], force_recrawl=False):
    user = get_or_create_user(user_full_name=user_full_name)
    crawl_urls(user=user, urls=links, force_recrawl=force_recrawl)

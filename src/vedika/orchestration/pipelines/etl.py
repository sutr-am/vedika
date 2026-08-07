from zenml import pipeline

from vedika.orchestration.steps.etl import crawl_links, get_or_create_user


@pipeline(name="vedika_etl")
def digital_data_etl(user_full_name: str, links: list[str]):
    user = get_or_create_user(user_full_name=user_full_name)
    crawl_links(user=user, links=links)

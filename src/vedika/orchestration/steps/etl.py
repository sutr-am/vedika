# src/vedika/orchestration/steps/etl.py
from typing import Annotated

from tqdm import tqdm
from zenml import get_step_context, step

from vedika import log_json_dict
from vedika.application.bootstrap.container import ApplicationContainer
from vedika.application.services.crawling_service import CrawlStatus
from vedika.domain.users import UserDomain
from vedika.orchestration.utils.trackers import CrawlMetadataTracker
from vedika.settings import get_settings


@step()
def crawl_urls(
    user: UserDomain, urls: list[str], force_recrawl: bool = False
) -> Annotated[list[str], "crawled_urls"]:
    # 1. Bootstrap the application
    settings = get_settings()
    container = ApplicationContainer(settings=settings)

    # 2. Extract the fully wired service
    service = container.crawler_service
    tracker = CrawlMetadataTracker()
    successful_urls = []
    for url in tqdm(urls):
        # the service handle the dedupe check, crawler routing and database save
        # the zenml step just tells it to run
        status = service.crawl_and_save(url=url, user_id=user.id, force_recrawl=force_recrawl)
        tracker.record(url=url, status=status)

        # necessary because different host will be captured in different struct in the metadata
        # so, can't use the  metadata here. Need to capture the successuly crawled urls separately
        if status == CrawlStatus.SUCCESS:
            successful_urls.append(url)

    # zenml context logging
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_urls", metadata=tracker.full_metadata)
    log_json_dict(data=tracker.summary_counts, message="Crawl Summary Metadata")

    return successful_urls

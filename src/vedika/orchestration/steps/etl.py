from typing import Annotated, Any
from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from zenml import get_step_context, step

from vedika import log_json_dict
from vedika.application.crawlers.factory import build_crawler_dispatcher
from vedika.domain.documents import UserDomain
from vedika.domain.repositories import BaseContentRepository, BaseUserRepository
<<<<<<< HEAD
from vedika.infrastructure.db.factory import (
    get_document_repository,
    get_user_repository,
)
=======
from vedika.infrastructure.db.factory import get_document_repository, get_user_repository
>>>>>>> d68c9a7 (refactor)


@step
def get_or_create_user(user_full_name: str) -> Annotated[UserDomain, "user"]:
    logger.info(f"Retrieving or Creating user: {user_full_name}")
    first_name, last_name = user_full_name.split(" ", 1)

    # 1. Dynamically load the repository via the factory
    repository: BaseUserRepository = get_user_repository()
    user = repository.get_or_create_user(first_name=first_name, last_name=last_name)

    # 2. Attach metadata to the 'user' artifact
    metadata = {
        "query": {"user_full_name": user_full_name},
        "retrieved": {
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    }
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="user", metadata=metadata)
    return user


@step
def crawl_links(
    user: UserDomain, links: list[str], force_recrawl: bool = False
) -> Annotated[list[str] | None, "crawled_links"]:
    crawler_dispatcher = build_crawler_dispatcher()
    metadata: dict[str, dict[str, Any]] = {}
    successful_urls: list[str] = []

    for url in tqdm(links, "Crawling links"):
        crawled_domain = urlparse(url).netloc
        if crawled_domain not in metadata:
            metadata[crawled_domain] = {
                "successful": [],
                "skipped": [],
                "failed": [],
                "count": {"successful": 0, "skipped": 0, "failed": 0, "total": 0},
            }
        metadata[crawled_domain]["count"]["total"] += 1
        try:
            crawler = crawler_dispatcher.get_crawler(url=url)

            # Get the specific repository for this document's category
            repository: BaseContentRepository = get_document_repository(category=crawler._category)
            if not force_recrawl and repository.exists_by_url(url=url):
                logger.info(
                    f"Skipping {url} - already exists in database. Use force_recrawl=True to override."
                )
                metadata[crawled_domain]["skipped"].append(url)
                metadata[crawled_domain]["count"]["skipped"] += 1
                # successful_urls.append(url)
                continue
            # Extract the document
            logger.info(f"Crawling {url=}...")
            document = crawler.extract(url=url, user_id=user.id, user_full_name=user.full_name)

            # 3. Save it using polymorphic method
            repository.save(document)
            successful_urls.append(url)
            metadata[crawled_domain]["successful"].append(url)
            metadata[crawled_domain]["count"]["successful"] += 1
        except Exception as e:
            logger.error(f"Failed to crawl and save {url=}:\n {e}")
            metadata[crawled_domain]["failed"].append(url)
            metadata[crawled_domain]["count"]["failed"] += 1
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)
    logger.info(f"Successfully crawled {len(successful_urls)} / {len(links)} links.")
    # logger.info(f"{metadata=}")
    # print_json(data=metadata)
    counts_only = {domain: data["count"] for domain, data in metadata.items()}
    log_json_dict(data=counts_only, message="metadata")
    return successful_urls

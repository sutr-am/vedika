from typing import Annotated
from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from zenml import get_step_context, step

from flash_llm.application.crawlers.dispatcher import CrawlerDispatcher
from flash_llm.domain.documents import UserDomain
from flash_llm.domain.repositories import DocumentRepository
from flash_llm.infrastructure.db.factory import get_document_repository


@step
def get_or_create_user(user_full_name: str) -> Annotated[UserDomain, "user"]:
    logger.info(f"\nRetrieving or Creating user: {user_full_name}")
    first_name, last_name = user_full_name.split(" ", 1)

    # 1. Dynamicallay load the repository via the factory
    repository: DocumentRepository = get_document_repository()
    user = repository.get_or_create_user(first_name=first_name, last_name=last_name)

    # 2. Attach metadat to teh 'user' artifact
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
def crawl_links(user: UserDomain, links: list[str]) -> Annotated[list[str] | None, "crawled_links"]:
    # 1. Dynamically load the repository via the factory
    repository: DocumentRepository = get_document_repository()

    # 2. Inject the repository into the Dispatcher
    dispatcher = CrawlerDispatcher(repository=repository)

    metadata = {}
    successful_crawls = 0

    for url in tqdm(links):
        crawled_domain = urlparse(url).netloc
        try:
            crawler = dispatcher.get_crawler(url=url)
            crawler.extract(url=url, user_id=user.id, user_full_name=user.full_name)
            success = 1
            successful_crawls += 1
        except Exception as e:
            logger.error(f"\nAn error occured while crawling {url}: {e}")
            success = 0

        # Aggregate metrics per domain
        if crawled_domain not in metadata:
            metadata[crawled_domain] = {"successful": 0, "total": 0}
        metadata[crawled_domain]["successful"] += success
        metadata[crawled_domain]["total"] += 1

    # 3. Attach metadata to the 'crawled_links' artifact
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)
    logger.info(f"\nSuccessfully crawled {successful_crawls} / {len(links)} links.")
    return links

from typing import Annotated
from urllib.parse import urlparse

from loguru import logger
from tqdm import tqdm
from zenml import get_step_context, step

from flash_llm.application.crawlers.factory import build_crawler_dispatcher
from flash_llm.domain.documents import UserDomain
from flash_llm.domain.repositories import BaseDocumentRepository, BaseUserRepository
from flash_llm.infrastructure.db.factory import get_document_repository, get_user_repository


@step
def get_or_create_user(user_full_name: str) -> Annotated[UserDomain, "user"]:
    logger.info(f"\nRetrieving or Creating user: {user_full_name}")
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
def crawl_links(user: UserDomain, links: list[str]) -> Annotated[list[str] | None, "crawled_links"]:
    crawler_dispatcher = build_crawler_dispatcher()
    metadata: dict[str, dict[str, int]] = {}
    successful_urls: list[str] = []

    for url in tqdm(links, "Crawling links"):
        crawled_domain = urlparse(url).netloc
        if crawled_domain not in metadata:
            metadata[crawled_domain] = {"successful": 0, "total": 0}
        metadata[crawled_domain]["total"] += 1

        try:
            # 1 extract teh document
            crawler = crawler_dispatcher.get_crawler(url=url)
            document = crawler.extract(url=url, user_id=user.id, user_full_name=user.full_name)

            # 2. Get the specific repository for this document's category
            repository: BaseDocumentRepository = get_document_repository(category=document.category)

            # 3. Save it using polymorphic method
            repository.save(document)
            successful_urls.append(url)
            metadata[crawled_domain]["successful"] += 1
        except Exception as e:
            logger.error(f"Failed to crawl and save {url=}:\n {e}")
    step_context = get_step_context()
    step_context.add_output_metadata(output_name="crawled_links", metadata=metadata)
    logger.info(f"\nSuccessfully crawled {successful_urls} / {len(links)} links.")
    return successful_urls

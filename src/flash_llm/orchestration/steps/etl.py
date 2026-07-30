from zenml import step
from loguru import logger
from flash_llm.domain.repositories import DocumentRepository
from flash_llm.domain.documents import UserDomain
from flash_llm.application.crawlers.dispatcher import CrawlerDispatcher
from flash_llm.infrastructure.db.factory import get_document_repository

@step
def get_or_create_user(user_full_name:str):
    logger.info(f"retrieving or Creating user: {user_full_name}")
    first_name, last_name = user_full_name.split(" ", 1)

    # 1. Dynamicallay load the repository via the factory
    repository: DocumentRepository = get_document_repository()
    user = repository.get_or_create_user(first_name=first_name, last_name=last_name)
    return user

@step
def crawl_links(user: UserDomain, links:list[str])-> None:
    # 1. Dynamically load the repository via the factory
    repository: DocumentRepository = get_document_repository()

    # 2. Inject the repository into the Dispatcher
    dispatcher = CrawlerDispatcher(repository=repository)
    for url in links:
        crawler = dispatcher.get_crawler(url=url)
        crawler.extract(url=url, user_id=user.id, user_full_name=user.full_name)
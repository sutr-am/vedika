import os

from flash_llm.application.crawlers.dispatcher import CrawlerDispatcher
from flash_llm.application.crawlers.github import GithubCrawler
from flash_llm.domain.types import DataCategory
from flash_llm.infrastructure.db.factory import get_document_repository


def build_crawler_dispatcher() -> CrawlerDispatcher:
    """Builds and wires up dispatcher with all available crawlers"""
    dispatcher = CrawlerDispatcher()

    # 1. Gather dependencies
    github_token = os.getenv("GITHUB_TOKEN")  # TODO: get it from settigs.py instead
    # bitbucket_token = os.getenv("BITBUCKET_TOKEN")    # TODO: get it from settigs.py instead

    # 2. Instantiate the crawlers
    github_crawler = GithubCrawler(
        repository=get_document_repository(category=DataCategory.CODEBASES),
        github_token=github_token,
    )

    # bitbucket_crawler = BitbucketCrawler(
    #     repository=get_document_repository(category=DataCategory.CODEBASES),
    #     bitbucket_token=bitbucket_token
    # )

    # 3. Register the instances
    dispatcher.register(domain_keyword="github.com", crawler_instance=github_crawler)
    # dispatcher.register(domain_keyword="bitbucket.com", crawler_instance=bitbucket_crawler)
    # dispatcher.register(domain_keyword="medium.com", crawler_instance=article_crawler)

    return dispatcher

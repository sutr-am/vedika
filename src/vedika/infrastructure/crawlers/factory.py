# src/vedika/infrastructure/crawlers/factory.py
from vedika.infrastructure.crawlers.github import GithubCrawler
from vedika.infrastructure.crawlers.router import CrawlerRouter
from vedika.settings import Settings


def build_crawler_router(settings: Settings) -> CrawlerRouter:
    """Builds and wires up router with all available crawlers"""

    router = CrawlerRouter()

    router.register(host="github.com", crawler=GithubCrawler(token=settings.github_token))
    # router.register(host="bitbucket.com", crawler=BitbucketCrawler(token=settings.bitbucket_token))
    # router.register(host="medium.com", crawler=article_crawler)

    return router

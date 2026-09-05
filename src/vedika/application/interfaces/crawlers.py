# src/vedika/application/interfaces/crawlers.py
from abc import ABC, abstractmethod
from uuid import UUID

from vedika.domain.raw import BaseRawDomain
from vedika.domain.types import DataCategory


class BaseCrawler(ABC):
    category: DataCategory  # the DataCategory this crawler is designed for
    provider: str  # eg. github, bitbucket, medium etc
    version: str  # version of this crawler

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "category"):
            raise NotImplementedError(
                "Subclasses of BaseCrawler must define a 'category' attribute. "
                f"{cls.__name__} does not."
            )

    @abstractmethod
    def canonicalize_url(self, url: str) -> str:
        pass

    @abstractmethod
    def get_ref(self, url: str) -> str | None:
        pass

    @abstractmethod
    def get_revision(self, canonical_url: str, ref: str | None) -> str:
        pass

    @abstractmethod
    def extract(
        self,
        canonical_url: str,  # the cleaned/base URL from the requested_url
        ref: str | None,  # the branch/ref it is supposed to crawl
        user_id: UUID,  # the user.id it is tied to
        source_id: UUID,  # the source.id it is crawling
        crawl_id: UUID,  # the crawl.id it is tied to
    ) -> list[BaseRawDomain]:
        pass


class BaseCrawlerRouter(ABC):
    """This returns the Crawler based on the queried URL"""

    @abstractmethod
    def get_crawler(self, url: str) -> BaseCrawler:
        pass

# src/vedika/application/interfaces/crawlers.py
from abc import ABC, abstractmethod
from uuid import UUID

from vedika.domain.raw import BaseRawDomain
from vedika.domain.types import DataCategory


class BaseCrawler(ABC):
    category: DataCategory
    provider: str
    version: str

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
        canonical_url: str,
        ref: str | None,
        user_id: UUID,
        source_id: UUID,
        crawl_id: UUID,
    ) -> list[BaseRawDomain]:
        pass


class BaseCrawlerRouter(ABC):
    @abstractmethod
    def get_crawler(self, url: str) -> BaseCrawler:
        pass

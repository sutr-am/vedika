# src/vedika/application/interfaces/crawlers.py
from abc import ABC, abstractmethod

from pydantic import UUID4

from vedika.domain.raw import BaseRawDomain
from vedika.domain.types import DataCategory


class BaseCrawler(ABC):
    """
    Abstract Base class for all Base Crawlers.
    Uses Dependency Injection to receive a database repository.
    """

    category: DataCategory

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "category"):
            raise NotImplementedError(
                f"Subclasses of BaseCrawler must define a 'category' attribute. {cls.__name__} does not."
            )

    @abstractmethod
    def extract(self, url: str, user_id: UUID4) -> BaseRawDomain:
        """
        Extracts data from the URL and saves it using the Repository.
        """
        pass

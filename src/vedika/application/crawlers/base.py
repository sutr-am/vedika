from abc import ABC, abstractmethod

from pydantic import UUID4

from vedika.domain.documents import BaseContentDomain
from vedika.domain.repositories import BaseContentRepository
from vedika.domain.types import DataCategory


class BaseCrawler(ABC):
    """
    Abstract Base class for all Base Crawlers.
    Uses Dependency Injection to receive a database repository.
    """

    _category: DataCategory

    def __init__(self, repository: BaseContentRepository) -> None:
        self.repository = repository

    @abstractmethod
    def extract(self, url: str, user_id: UUID4, user_full_name: str) -> BaseContentDomain:
        """
        Extracts data from the URL and saves it using the Repository.
        """
        pass

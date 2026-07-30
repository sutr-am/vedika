from abc import ABC, abstractmethod

from pydantic import UUID4

from flash_llm.domain.repositories import DocumentRepository


class BaseCrawler(ABC):
    """
    Abstract Base class for all Base Crawlers.
    Uses Dependency Injection to receive a database repository.
    """

    def __init__(self, repository: DocumentRepository) -> None:
        self.repository = repository

    @abstractmethod
    def extract(self, url: str, user_id: UUID4, user_full_name: str) -> None:
        """
        Extracts data from the URL and saves it using the Repository.
        """
        pass

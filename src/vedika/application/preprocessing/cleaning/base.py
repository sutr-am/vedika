from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseContentDomain

TDoc = TypeVar("TDoc", bound=BaseContentDomain)
TCleaned = TypeVar("TCleaned", bound=BaseCleanedDomain)


class BaseCleaningHandler(ABC, Generic[TDoc, TCleaned]):
    """
    Abstract Base Class for all cleaning handlers.
    Enforces a strict transformation froma raw document to a cleaned document.
    """

    @abstractmethod
    def clean(self, data: TDoc) -> TCleaned:
        """Applies data-category-specific cleaning logic to the raw document content"""
        pass

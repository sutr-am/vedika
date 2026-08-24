# src/vedika/application/interfaces/cleaners.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from vedika.domain.cleaned import BaseCleanedDomain
from vedika.domain.raw import BaseRawDomain

RawT = TypeVar("RawT", bound=BaseRawDomain)
CleanT = TypeVar("CleanT", bound=BaseCleanedDomain)


class BaseCleaningHandler(ABC, Generic[RawT, CleanT]):
    """
    Abstract Base Class for all cleaning handlers.
    Enforces a strict transformation from a raw document to a cleaned document.
    """

    @abstractmethod
    def clean(self, data: RawT) -> CleanT:
        """Applies data-category-specific cleaning logic to the raw document content"""
        pass

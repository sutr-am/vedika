"""Loads the document after removing the noise from the document"""

from abc import ABC
from uuid import UUID

from pydantic import BaseModel

from vedika.domain.types import DataCategory


class BaseCleanedDomain(BaseModel, ABC):
    """Abstract domain entity for a cleaned, full-length document"""

    id: UUID
    content: str
    platform: str
    author_id: UUID
    author_full_name: str


class CleanedCodebaseDomain(BaseCleanedDomain):
    """Cleaned state specific to a codebase"""

    category: DataCategory = DataCategory.CODEBASES

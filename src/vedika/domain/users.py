# src/vedika/domain/users.py
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from vedika.domain.types import DataCategory


class UserDomain(BaseModel):
    """Core domain entity representing a user"""

    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    category: Literal[DataCategory.USERS] = DataCategory.USERS

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

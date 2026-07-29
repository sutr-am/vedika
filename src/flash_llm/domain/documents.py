from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from flash_llm.domain.types import DataCategory


class DocumentDomain(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    source_url: HttpUrl
    content: str
    category: DataCategory

    @property
    def word_count(self) -> int:
        return len(self.content.split())

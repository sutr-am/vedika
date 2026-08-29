from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import CrawlStatus


class SourceDomain(BaseModel):
    """A user-owned, stable reference to an external data source."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    provider: str
    canonical_url: HttpUrl


class CrawlDomain(BaseModel):
    """An immutable source snapshot identified by its upstream revision."""

    id: UUID = Field(default_factory=uuid4)
    source_id: UUID
    requested_url: HttpUrl
    canonical_url: HttpUrl
    selected_ref: str | None = None
    revision: str
    crawler_version: str
    status: CrawlStatus = CrawlStatus.PENDING
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    document_count: int = 0
    error_message: str | None = None

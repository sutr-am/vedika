from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import CrawlStatus


class SourceDomain(BaseModel):
    """A user-owned, stable reference to an external data source."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID  # links the owning USER to this source
    provider: str  # eg. github, bitbucket etc.
    canonical_url: HttpUrl


class CrawlDomain(BaseModel):
    """An immutable source snapshot identified by its upstream revision."""

    id: UUID = Field(default_factory=uuid4)
    source_id: UUID  # the id linking the source from SourceDomain
    requested_url: HttpUrl  # the actual request URL to be crawled
    canonical_url: HttpUrl  # the cleaned-up canonical URL (same gets stored in SourceDomain too)
    selected_ref: str | None = None  # the branch/ref in a git repo or simialr field in generic urls
    revision: str  # the unique hash of state of data in the canonical url @ ref (eg. a commit hash)
    crawler_version: str  # teh version of the actual Crawler (liek GithubCrawler_v2)
    status: CrawlStatus = CrawlStatus.PENDING  # teh status of the crawl
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    document_count: int = 0  # the number of documents to be crawled in this crawl
    error_message: str | None = None

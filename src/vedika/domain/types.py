# src/vedika/domain/types.py
from enum import StrEnum

from pydantic import BaseModel, Field, computed_field


class DataCategory(StrEnum):
    USERS = "users"  # stores details about user data (eg. UserDomain)
    CODEBASES = "codebases"  # stores data from code repos like github, bitbucket etc
    # POSTS = "posts"
    # ARTICLES = "articles"


class DataState(StrEnum):
    RAW = "raw"
    # CLEANED = "cleaned"
    # CHUNKED = "chunked"
    # EMBEDDED = "embedded"


class CrawlStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"


class CrawlHostMetadata(BaseModel):
    """
    _metadata = {
        "github": {
            "counts": {
                "total": 0,
                "success": 0,
                "skipped": 0,
                "failed": 0
            },
            "urls_by_status" {
                "success": [],
                "skipped": [],
                "failed": [],
            },
        }
    }
    """

    urls_by_status: dict[CrawlStatus, list[str]] = Field(
        default_factory=lambda: {status: [] for status in CrawlStatus}
    )

    @computed_field
    @property
    def counts(self) -> dict[str, int]:
        counts = {status.value: len(urls) for status, urls in self.urls_by_status.items()}
        counts["total"] = sum(counts.values())
        return counts


class UserQueryMetadata(BaseModel):
    user_full_name: str  # user.full_name (full-name of the user)


class RetrievedUserMetadata(BaseModel):
    user_id: str  # the user.id
    first_name: str  # user.first_name
    last_name: str  # user.last_name


class UserMetadata(BaseModel):
    """
    {
        "query": {"user_full_name": ""},
        "retrieved": {
            "user_id": "",
            "first_name": "",
            "last_name": "",
        },
    }
    """

    query: UserQueryMetadata
    retrieved: RetrievedUserMetadata

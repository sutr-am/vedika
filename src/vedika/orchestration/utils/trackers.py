# src/vedika/orchestration/utils/trackers.py
from urllib.parse import urlparse

from vedika.domain.types import (
    CrawlHostMetadata,
    CrawlStatus,
    RetrievedUserMetadata,
    UserMetadata,
    UserQueryMetadata,
)
from vedika.domain.users import UserDomain


class CrawlMetadataTracker:
    """Encapsulate metadata tracking logic for crawling pipelines"""

    def __init__(self):
        self._metadata: dict[str, CrawlHostMetadata] = {}

    def _initialize_host(self, host: str) -> None:
        if host not in self._metadata:
            self._metadata[host] = CrawlHostMetadata()

    def record(self, url: str, status: CrawlStatus) -> None:
        """Parses the URL and stores ist metadata"""
        host = urlparse(url).hostname or ""
        self._initialize_host(host)

        self._metadata[host].urls_by_status[status].append(url)

    @property
    def full_metadata(self) -> dict[str, dict]:
        return {host: data.model_dump(mode="json") for host, data in self._metadata.items()}

    @property
    def summary_counts(self) -> dict[str, dict[str, int]]:
        return {host: data.counts for host, data in self._metadata.items()}


class UserMetadataTracker:
    """Encapsulate metadata tracking logic for users"""

    def __init__(self):
        self._metadata: UserMetadata | None = None

    def record(self, user: UserDomain | None) -> None:
        if user:
            self._metadata = UserMetadata(
                query=UserQueryMetadata(user_full_name=user.full_name),
                retrieved=RetrievedUserMetadata(
                    user_id=str(user.id), first_name=user.first_name, last_name=user.last_name
                ),
            )

    @property
    def full_metadata(self) -> dict:
        if self._metadata is None:
            return {}

        return self._metadata.model_dump(mode="json")

# src/vedika/orchestration/utils/trackers.py
from typing import Any
from urllib.parse import urlparse

from vedika.application.services.crawling_service import CrawlStatus
from vedika.domain.users import UserDomain


class CrawlMetadataTracker:
    """Encapsulate metadata tracking logic for crawling pipelines"""

    def __init__(self):
        self._metadata: dict[str, dict[str, Any]] = {}

    def _initialize_domain(self, domain: str) -> None:
        if domain not in self._metadata:
            self._metadata[domain] = {"count": {"total": 0}}
            for status in CrawlStatus:
                status = status.value
                self._metadata[domain][status] = []
                self._metadata[domain]["count"][status] = 0

    def record(self, url: str, status: CrawlStatus) -> None:
        """Parses the URL and stores ist metadata"""
        domain = urlparse(url).netloc
        self._initialize_domain(domain)
        self._metadata[domain][status.value].append(url)
        self._metadata[domain]["count"][status.value] += 1
        self._metadata[domain]["count"]["total"] += 1

    @property
    def full_metadata(self):
        return self._metadata

    @property
    def summary_counts(self):
        return {domain: data["count"] for domain, data in self._metadata.items()}


class UserMetadataTracker:
    """Encapsulate metadata tracking logic for users"""

    def __init__(self):
        self._metadata = {
            "query": {"user_full_name": ""},
            "retrieved": {
                "user_id": "",
                "first_name": "",
                "last_name": "",
            },
        }

    def record(self, user: UserDomain) -> None:
        self._metadata["query"]["user_full_name"] = user.full_name
        self._metadata["retrieved"]["user_id"] = str(user.id)
        self._metadata["retrieved"]["first_name"] = user.first_name
        self._metadata["retrieved"]["last_name"] = user.last_name

    @property
    def full_metadata(self):
        return self._metadata

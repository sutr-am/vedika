# src/vedika/domain/raw.py
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl

from vedika.domain.types import DataCategory, DataState


class BaseRawDomain(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source_id: UUID  # the linking filed to actual SourceDomain.id (that defines details of data)
    crawl_id: UUID  # the linking field to teh CrawlDomain.id (which crawled this data)
    title: str  # the title for the data
    content: str  # the actual CONTENT of teh crawled data
    platform: str  # the platform from which it was crawled like github, bitbucker, medium etc
    source_url: HttpUrl  # the actual URL (CrawlDOmain.request_url)
    user_id: UUID  # the user.id which owns this crawl (not the owner/author of teh actual website)
    repository_path: str  # !TODO: root path of the url (useful for code repos mainly)
    upstream_file_sha: str  # the SHA256 hash of the crawled filepath
    content_sha256: str  # the SHA256 hash of teh actual content in the file
    category: DataCategory  # the data-category (eg. codebases, articles, posts etc)
    state: DataState = DataState.RAW  # (always DataCategory.RAW b'coz this is BaseRawDomain )

    @property
    def word_count(self) -> int:
        """Returns the totoal word count in the content of the cralwed file"""
        return len(self.content.split())


class CodebaseRawDomain(BaseRawDomain):
    category: DataCategory = DataCategory.CODEBASES

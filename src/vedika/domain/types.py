# src/vedika/domain/types.py
from enum import StrEnum


class DataCategory(StrEnum):
    USERS = "users"
    CODEBASES = "codebases"
    # POSTS = "posts"
    # ARTICLES = "articles"


class DataState(StrEnum):
    RAW = "raw"
    CLEANED = "cleaned"
    # CHUNKED = "chunked"
    # EMBEDDED = "embedded"


class CrawlStatus(StrEnum):
    SUCCESS = "success"
    SKIPPED = "skipped"
    FAILED = "failed"

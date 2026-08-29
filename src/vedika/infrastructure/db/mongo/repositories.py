# src/vedika/infrastructure/db/mongo/repositories.py
from datetime import datetime, timezone
from uuid import UUID

from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.operations import ReplaceOne

from vedika.application.interfaces.repositories import (
    BaseCleanedRepository,
    BaseRawRepository,
    BaseUserRepository,
)
from vedika.domain.cleaned import CodebaseCleanedDomain
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.sources import CrawlDomain, SourceDomain
from vedika.domain.types import CrawlStatus
from vedika.domain.users import UserDomain
from vedika.infrastructure.db.mongo.models import (
    CodebaseCleanedMongoDocument,
    CodebaseRawMongoDocument,
    CrawlMongoDocument,
    SourceMongoDocument,
    UserMongoDocument,
)


class UserMongoRepository(BaseUserRepository[UserDomain]):
    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        # 1. Initialize the specific MongoDB collection directly in memory
        self._collection: Collection = client[db_name][target]
        self._collection.create_index(
            [("first_name", ASCENDING), ("last_name", ASCENDING)], unique=True
        )

    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        new_user = UserMongoDocument(first_name=first_name, last_name=last_name)
        db_data = self._collection.find_one_and_update(
            {"first_name": first_name, "last_name": last_name},
            {"$setOnInsert": new_user.to_mongo()},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )

        # Map back to the pure Domain model
        return UserDomain(
            id=db_data.get("_id", db_data.get("id")),
            first_name=db_data["first_name"],
            last_name=db_data["last_name"],
        )


class CodebaseRawMongoRepository(BaseRawRepository[CodebaseRawDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM documents.
    """

    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        # Initialize the specific MongoDB collection directly in memory
        self._collection: Collection = client[db_name][target]
        self._collection.create_index(
            [("crawl_id", ASCENDING), ("repository_path", ASCENDING)], unique=True
        )

    def exists_by_url(self, url: str) -> bool:
        return self._collection.find_one({"source_url": url}) is not None

    def save(self, document: CodebaseRawDomain) -> None:
        db_doc = CodebaseRawMongoDocument(
            id=document.id,
            source_id=document.source_id,
            crawl_id=document.crawl_id,
            title=document.title,
            content=document.content,
            platform=document.platform,
            source_url=document.source_url,
            user_id=document.user_id,
            repository_path=document.repository_path,
            upstream_file_sha=document.upstream_file_sha,
            content_sha256=document.content_sha256,
        )

        self._collection.replace_one({"_id": str(db_doc.id)}, db_doc.to_mongo(), upsert=True)

    def replace_crawl_documents(self, crawl_id: UUID, documents: list[CodebaseRawDomain]) -> None:
        if any(document.crawl_id != crawl_id for document in documents):
            raise ValueError("All raw documents must belong to the supplied crawl")

        operations = []
        for document in documents:
            db_doc = CodebaseRawMongoDocument(
                id=document.id,
                source_id=document.source_id,
                crawl_id=document.crawl_id,
                title=document.title,
                content=document.content,
                platform=document.platform,
                source_url=document.source_url,
                user_id=document.user_id,
                repository_path=document.repository_path,
                upstream_file_sha=document.upstream_file_sha,
                content_sha256=document.content_sha256,
            )
            operations.append(ReplaceOne({"_id": str(db_doc.id)}, db_doc.to_mongo(), upsert=True))

        if operations:
            self._collection.bulk_write(operations, ordered=False)
        paths = [document.repository_path for document in documents]
        self._collection.delete_many(
            {"crawl_id": str(crawl_id), "repository_path": {"$nin": paths}}
        )

    def get_all(self) -> list[CodebaseRawDomain]:
        cursor = self._collection.find()
        domain_docs = []

        for doc in cursor:
            domain_docs.append(
                CodebaseRawDomain(
                    id=doc.get("_id", doc.get("id")),
                    source_id=doc["source_id"],
                    crawl_id=doc["crawl_id"],
                    title=doc.get("title"),
                    content=doc.get("content"),
                    platform=doc.get("platform"),
                    source_url=doc.get("source_url"),
                    user_id=doc.get("user_id"),
                    repository_path=doc["repository_path"],
                    upstream_file_sha=doc["upstream_file_sha"],
                    content_sha256=doc["content_sha256"],
                )
            )

        return domain_docs


class SourceMongoRepository:
    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        self._collection: Collection = client[db_name][target]
        self._collection.create_index(
            [("user_id", ASCENDING), ("provider", ASCENDING), ("canonical_url", ASCENDING)],
            unique=True,
        )

    def get_or_create(self, user_id: UUID, provider: str, canonical_url: str) -> SourceDomain:
        source = SourceMongoDocument(
            user_id=user_id,
            provider=provider,
            canonical_url=canonical_url,
        )
        db_doc = self._collection.find_one_and_update(
            {"user_id": str(user_id), "provider": provider, "canonical_url": canonical_url},
            {"$setOnInsert": source.to_mongo()},
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return SourceDomain(
            id=db_doc["_id"],
            user_id=db_doc["user_id"],
            provider=db_doc["provider"],
            canonical_url=db_doc["canonical_url"],
        )


class CrawlMongoRepository:
    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        self._collection: Collection = client[db_name][target]
        self._collection.create_index(
            [("source_id", ASCENDING), ("revision", ASCENDING), ("crawler_version", ASCENDING)],
            unique=True,
        )

    @staticmethod
    def _to_domain(db_doc: dict) -> CrawlDomain:
        return CrawlDomain(
            id=db_doc["_id"],
            source_id=db_doc["source_id"],
            requested_url=db_doc["requested_url"],
            canonical_url=db_doc["canonical_url"],
            selected_ref=db_doc.get("selected_ref"),
            revision=db_doc["revision"],
            crawler_version=db_doc["crawler_version"],
            status=db_doc["status"],
            started_at=db_doc["started_at"],
            completed_at=db_doc.get("completed_at"),
            document_count=db_doc.get("document_count", 0),
            error_message=db_doc.get("error_message"),
        )

    def get_successful(
        self, source_id: UUID, revision: str, crawler_version: str
    ) -> CrawlDomain | None:
        db_doc = self._collection.find_one(
            {
                "source_id": str(source_id),
                "revision": revision,
                "crawler_version": crawler_version,
                "status": CrawlStatus.SUCCESS.value,
            }
        )
        return self._to_domain(db_doc) if db_doc else None

    def get_or_create(self, crawl: CrawlDomain) -> CrawlDomain:
        crawl_data = CrawlMongoDocument(**crawl.model_dump(exclude={"id"})).to_mongo()
        crawl_data.pop("status")
        crawl_data.pop("error_message")
        crawl_data.pop("completed_at")
        db_doc = self._collection.find_one_and_update(
            {
                "source_id": str(crawl.source_id),
                "revision": crawl.revision,
                "crawler_version": crawl.crawler_version,
            },
            {
                "$setOnInsert": crawl_data,
                "$set": {
                    "status": CrawlStatus.RUNNING.value,
                    "error_message": None,
                    "completed_at": None,
                },
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return self._to_domain(db_doc)

    def mark_succeeded(self, crawl_id: UUID, document_count: int) -> None:
        self._collection.update_one(
            {"_id": str(crawl_id)},
            {
                "$set": {
                    "status": CrawlStatus.SUCCESS.value,
                    "document_count": document_count,
                    "completed_at": datetime.now(timezone.utc),
                    "error_message": None,
                }
            },
        )

    def mark_failed(self, crawl_id: UUID, error_message: str) -> None:
        self._collection.update_one(
            {"_id": str(crawl_id)},
            {
                "$set": {
                    "status": CrawlStatus.FAILED.value,
                    "completed_at": datetime.now(timezone.utc),
                    "error_message": error_message,
                }
            },
        )


class CodebaseCleanedMongoRepository(BaseCleanedRepository[CodebaseCleanedDomain]):
    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        # 1. Initialize the specific MongoDB collection directly in memory
        self._collection: Collection = client[db_name][target]

    def exists_by_id(self, document_id: UUID) -> bool:
        return self._collection.find_one({"_id": str(document_id)}) is not None

    def save(self, document: CodebaseCleanedDomain) -> None:
        db_doc = CodebaseCleanedMongoDocument(
            id=document.id,
            title=document.title,
            content=document.content,
            platform=document.platform,
            source_url=document.source_url,
            user_id=document.user_id,
        )

        self._collection.replace_one({"_id": str(db_doc.id)}, db_doc.to_mongo(), upsert=True)

    def get_by_id(self, document_id: UUID) -> CodebaseCleanedDomain | None:
        db_doc = self._collection.find_one({"_id": str(document_id)})
        if db_doc:
            return CodebaseCleanedDomain(
                id=db_doc.get("_id", db_doc.get("id")),
                title=db_doc["title"],
                content=db_doc["content"],
                platform=db_doc["platform"],
                source_url=db_doc["source_url"],
                user_id=db_doc["user_id"],
            )
        return None

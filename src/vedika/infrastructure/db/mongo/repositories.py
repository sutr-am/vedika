# src/vedika/infrastructure/db/mongo/repositories.py
from uuid import UUID

from pymongo import MongoClient
from pymongo.collection import Collection

from vedika.application.interfaces.repositories import (
    BaseCleanedRepository,
    BaseRawRepository,
    BaseUserRepository,
)
from vedika.domain.cleaned import CodebaseCleanedDomain
from vedika.domain.raw import CodebaseRawDomain
from vedika.domain.users import UserDomain
from vedika.infrastructure.db.mongo.models import (
    CodebaseCleanedMongoDocument,
    CodebaseRawMongoDocument,
    UserMongoDocument,
)


class UserMongoRepository(BaseUserRepository[UserDomain]):
    def __init__(self, client: MongoClient, db_name: str, target: str) -> None:
        # 1. Initialize the specific MongoDB collection directly in memory
        self._collection: Collection = client[db_name][target]

    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        # 2. Query the database using the injected PyMongo collection
        db_data = self._collection.find_one({"first_name": first_name, "last_name": last_name})
        if not db_data:
            new_user_doc = UserMongoDocument(first_name=first_name, last_name=last_name)
            mongo_dict = new_user_doc.to_mongo()
            # 3. Save using the injected PyMongo collection
            self._collection.insert_one(mongo_dict)
            db_data = mongo_dict

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

    def exists_by_url(self, url: str) -> bool:
        return self._collection.find_one({"source_url": url}) is not None

    def save(self, document: CodebaseRawDomain) -> None:
        db_doc = CodebaseRawMongoDocument(
            title=document.title,
            content=document.content,
            platform=document.platform,
            source_url=document.source_url,
            user_id=document.user_id,
        )

        self._collection.replace_one({"_id": str(db_doc.id)}, db_doc.to_mongo(), upsert=True)

    def get_all(self) -> list[CodebaseRawDomain]:
        cursor = self._collection.find()
        domain_docs = []

        for doc in cursor:
            domain_docs.append(
                CodebaseRawDomain(
                    id=doc.get("_id", doc.get("id")),
                    title=doc.get("title"),
                    content=doc.get("content"),
                    platform=doc.get("platform"),
                    source_url=doc.get("source_url"),
                    user_id=doc.get("user_id"),
                )
            )

        return domain_docs


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

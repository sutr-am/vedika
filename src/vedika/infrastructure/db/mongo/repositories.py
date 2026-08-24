# src/vedika/infrastructure/db/mongo/repositories.py
from uuid import UUID

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
    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        db_user = UserMongoDocument.find(first_name=first_name, last_name=last_name)
        if not db_user:
            db_user = UserMongoDocument(first_name=first_name, last_name=last_name)
            db_user.save()

        return UserDomain(id=db_user.id, first_name=db_user.first_name, last_name=db_user.last_name)


class CodebaseRawMongoRepository(BaseRawRepository[CodebaseRawDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM documents.
    """

    def exists_by_url(self, url: str) -> bool:
        return CodebaseRawMongoDocument.find(source_url=url) is not None

    def save(self, document: CodebaseRawDomain) -> None:
        db_doc = CodebaseRawMongoDocument(
            title=document.title,
            content=document.content,
            platform=document.platform,
            source_url=document.source_url,
            user_id=document.user_id,
        )

        db_doc.save()

    def get_all(self) -> list[CodebaseRawDomain]:
        db_docs = CodebaseRawMongoDocument.find_all()
        domain_docs = []

        if db_docs:
            for doc in db_docs:
                domain_docs.append(
                    CodebaseRawDomain(
                        id=doc.id,
                        title=doc.title,
                        content=doc.content,
                        platform=doc.platform,
                        source_url=doc.source_url,
                        user_id=doc.user_id,
                    )
                )

        return domain_docs


class CodebaseCleanedMongoRepository(BaseCleanedRepository[CodebaseCleanedDomain]):
    def exists_by_id(self, document_id: UUID) -> bool:
        return CodebaseCleanedMongoDocument.find(id=document_id) is not None

    def save(self, document: CodebaseCleanedDomain) -> None:
        db_doc = CodebaseCleanedMongoDocument(
            id=document.id,
            title=document.title,
            content=document.content,
            platform=document.platform,
            source_url=document.source_url,
            user_id=document.user_id,
        )

        db_doc.save()

    def get_by_id(self, document_id: UUID) -> CodebaseCleanedDomain | None:
        db_doc: CodebaseCleanedDomain | None = CodebaseCleanedMongoDocument.find(id=document_id)
        if db_doc:
            doc = CodebaseCleanedDomain(
                title=db_doc.title,
                id=db_doc.id,
                content=db_doc.content,
                platform=db_doc.platform,
                source_url=db_doc.source_url,
                user_id=db_doc.user_id,
            )
            return doc
        return None

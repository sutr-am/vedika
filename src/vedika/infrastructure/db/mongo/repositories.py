from uuid import UUID

from vedika.domain.cleaned import CleanedCodebaseDomain
from vedika.domain.raw import CodebaseDomain, UserDomain
from vedika.domain.repositories import (
    BaseCleanedRepository,
    BaseContentRepository,
    BaseUserRepository,
)
from vedika.infrastructure.db.mongo.documents import (
    CleanedCodebaseDocument,
    CodebaseDocument,
    UserDocument,
)


class MongoUserRepository(BaseUserRepository[UserDomain]):
    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        db_user = UserDocument.find(first_name=first_name, last_name=last_name)
        if not db_user:
            db_user = UserDocument(first_name=first_name, last_name=last_name)
            db_user.save()

        return UserDomain(id=db_user.id, first_name=db_user.first_name, last_name=db_user.last_name)


class MongoCodebaseRepository(BaseContentRepository[CodebaseDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM docuemnts.
    """

    def exists_by_url(self, url: str) -> bool:
        return CodebaseDocument.find(link=url) is not None

    def save(self, document: CodebaseDomain) -> None:
        db_doc = CodebaseDocument(
            title=document.title,
            link=str(document.source_url),
            platform=document.platform,
            author_id=document.author_id,
            author_full_name=document.author_full_name,
            content=document.content,
            codebase_name=document.name,
        )
        db_doc.save()


class MongoCleanedCodebaseRepository(BaseCleanedRepository[CleanedCodebaseDomain]):
    def exists_by_id(self, document_id: UUID) -> bool:
        return CleanedCodebaseDocument.find(id=document_id) is not None

    def save(self, document: CleanedCodebaseDomain) -> None:
        db_doc = CleanedCodebaseDocument(
            id=document.id,
            content=document.content,
            platform=document.platform,
            author_id=document.author_id,
            author_full_name=document.author_full_name,
        )
        db_doc.save()

    def get_by_id(self, document_id: UUID) -> CleanedCodebaseDomain | None:
        db_doc: CleanedCodebaseDocument | None = CleanedCodebaseDocument.find(id=document_id)
        if not db_doc:
            return None
        doc = CleanedCodebaseDomain(
            id=db_doc.id,
            content=db_doc.content,
            platform=db_doc.platform,
            author_id=db_doc.author_id,
            author_full_name=db_doc.author_full_name,
        )
        return doc


# class MongoArticleRepository(BaseContentRepository[ArticleDomain]):
#     """
#     MongoDB concrete implementation of DocumentRepository interface.
#     Handles translating between Domain data-models and MongoDB ODM docuemnts.
#     """

#     def exists_by_url(self, url: str) -> bool:
#         return ArticleDocument.find(link=url) is not None

#     def save(self, document: ArticleDomain) -> None:
#         article = document
#         db_doc = ArticleDocument(
#             title=article.title,
#             link=str(article.source_url),
#             platform=article.platform,
#             author_id=article.author_id,
#             author_full_name=article.author_full_name,
#             content=article.content,
#         )
#         db_doc.save()


# class MongoPostRepository(BaseContentRepository[PostDomain]):
#     """
#     MongoDB concrete implementation of DocumentRepository interface.
#     Handles translating between Domain data-models and MongoDB ODM docuemnts.
#     """

#     def exists_by_url(self, url: str) -> bool:
#         return PostDocument.find(link=url) is not None

#     def save(self, document: PostDomain) -> None:
#         post = document
#         db_doc = PostDocument(
#             title=post.title,
#             link=str(post.source_url),
#             platform=post.platform,
#             author_id=post.author_id,
#             author_full_name=post.author_full_name,
#             content=post.content,
#         )
#         db_doc.save()

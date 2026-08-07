from vedika.domain.documents import (
    ArticleDomain,
    CodebaseDomain,
    PostDomain,
    UserDomain,
)
from vedika.domain.repositories import BaseContentRepository, BaseUserRepository
from vedika.infrastructure.db.mongo.documents import (
    ArticleDocument,
    CodebaseDocument,
    PostDocument,
    UserDocument,
)


class MongoCodebaseRepository(BaseContentRepository[CodebaseDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM docuemnts.
    """

    def exists_by_url(self, url: str) -> bool:
        return CodebaseDocument.find(link=url) is not None

    def save(self, document: CodebaseDomain) -> None:
        codebase = document
        db_doc = CodebaseDocument(
            title=codebase.title,
            link=str(codebase.source_url),
            platform=codebase.platform,
            author_id=codebase.author_id,
            author_full_name=codebase.author_full_name,
            content=codebase.content,
            codebase_name=codebase.name,
        )
        db_doc.save()


class MongoArticleRepository(BaseContentRepository[ArticleDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM docuemnts.
    """

    def exists_by_url(self, url: str) -> bool:
        return ArticleDocument.find(link=url) is not None

    def save(self, document: ArticleDomain) -> None:
        article = document
        db_doc = ArticleDocument(
            title=article.title,
            link=str(article.source_url),
            platform=article.platform,
            author_id=article.author_id,
            author_full_name=article.author_full_name,
            content=article.content,
        )
        db_doc.save()


class MongoPostRepository(BaseContentRepository[PostDomain]):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM docuemnts.
    """

    def exists_by_url(self, url: str) -> bool:
        return PostDocument.find(link=url) is not None

    def save(self, document: PostDomain) -> None:
        post = document
        db_doc = PostDocument(
            title=post.title,
            link=str(post.source_url),
            platform=post.platform,
            author_id=post.author_id,
            author_full_name=post.author_full_name,
            content=post.content,
        )
        db_doc.save()


class MongoUserRepository(BaseUserRepository[UserDomain]):
    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        db_user = UserDocument.find(first_name=first_name, last_name=last_name)
        if not db_user:
            db_user = UserDocument(first_name=first_name, last_name=last_name)
            db_user.save()

        return UserDomain(
            id=db_user.id, first_name=db_user.first_name, last_name=db_user.last_name
        )

from flash_llm.domain.documents import (
    ArticleDocumentDomain,
    CodebaseDocumentDomain,
    PostDocumentDomain,
    UserDomain,
)
from flash_llm.domain.repositories import DocumentRepository
from flash_llm.infrastructure.db.mongo.documents import (
    ArticleDocument,
    CodebaseDocument,
    PostDocument,
    UserDocument,
)


class MongoDocumentRepository(DocumentRepository):
    """
    MongoDB concrete implementation of DocumentRepository interface.
    Handles translating between Domain data-models and MongoDB ODM docuemnts.
    """

    def get_or_create_user(self, first_name: str, last_name: str) -> UserDomain:
        db_user = UserDocument.find(first_name=first_name, last_name=last_name)
        if not db_user:
            # 1. create a new db-user
            db_user = UserDocument(first_name=first_name, last_name=last_name)
            # 2. save the new db-user to the DB
            db_user.save()

        return UserDomain(id=db_user.id, first_name=db_user.first_name, last_name=db_user.last_name)

    def save_codebase(self, codebase: CodebaseDocumentDomain) -> None:
        db_doc = CodebaseDocument(
            title=codebase.title,
            link=str(codebase.source_url),
            platfrom=codebase.platform,
            author_id=codebase.author_id,
            author_full_name=codebase.author_full_name,
            content=codebase.content,
            codebase_name=codebase.name,
        )
        db_doc.save()

    def save_article(self, article: ArticleDocumentDomain) -> None:
        db_doc = ArticleDocument(
            title=article.title,
            link=str(article.source_url),
            platfrom=article.platform,
            author_id=article.author_id,
            author_full_name=article.author_full_name,
            content=article.content,
        )
        db_doc.save()

    def save_post(self, post: PostDocumentDomain) -> None:
        db_doc = PostDocument(
            title=post.title,
            link=str(post.source_url),
            platfrom=post.platform,
            author_id=post.author_id,
            author_full_name=post.author_full_name,
            content=post.content,
        )
        db_doc.save()

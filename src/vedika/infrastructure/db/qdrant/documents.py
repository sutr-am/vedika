from uuid import UUID

from vedika.domain.types import DataCategory
from vedika.infrastructure.db.qdrant.base import QdrantBaseDocument


class ChunkDocument(QdrantBaseDocument):
    """
    Abstracts infrastructure base for Qdrant chunks.
    Mirrors fields in the pure domain chunks.
    """

    document_id: UUID
    content: str
    platform: str
    author_id: UUID
    author_full_name: str


class CodebaseChunkDocument(ChunkDocument):
    class Settings:
        collection_name: DataCategory = DataCategory.CODEBASES


class ArticleChunkDocument(ChunkDocument):
    class Settings:
        collection_name: DataCategory = DataCategory.ARTICLES


class PostChunkDocument(ChunkDocument):
    class Settings:
        collection_name: DataCategory = DataCategory.POSTS

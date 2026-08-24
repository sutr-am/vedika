# src/vedika/infrastructure/db/qdrant/models.py
from uuid import UUID

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

    class Settings:
        collection_name: str = "_abstract_vector_document_"


class CodebaseChunkDocument(ChunkDocument):
    class Settings(ChunkDocument.Settings):
        collection_name: str = ""

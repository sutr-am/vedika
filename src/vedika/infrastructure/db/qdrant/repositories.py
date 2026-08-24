# src/vedika/infrastructure/db/qdrant/repositories.py
from vedika.domain.chunked import CodebaseChunkDomain
from vedika.application.interfaces.repositories import BaseVectorRepository
from vedika.infrastructure.db.qdrant.documents import CodebaseChunkDocument


class QdrantCodebaseRepository(BaseVectorRepository[CodebaseChunkDomain]):
    def save(self, chunk: CodebaseChunkDomain) -> None:
        # maps pure domain entities to infrastructure qdrant document
        db_doc = CodebaseChunkDocument(
            id=chunk.id,
            document_id=chunk.document_id,
            content=chunk.content,
            platform=chunk.platform,
            author_id=chunk.author_id,
            author_full_name=chunk.author_full_name,
            embedding=chunk.embedding,
        )

        db_doc.save()

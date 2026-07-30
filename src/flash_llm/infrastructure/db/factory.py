from flash_llm.domain.repositories import DocumentRepository
import os

def get_document_factory()-> DocumentRepository:
    """
    Factory function to instantiate teh correct database repository based on settings or env
    """
    db_type = os.getenv("DATABASE_TYPE", "mongo").lower()
    if db_type == "mongo":
        from flash_llm.infrastructure.db.mongo.repositories import MongoDocumentRepository
        return MongoDocumentRepository()
    elif db_type == "postgres":
        raise NotImplementedError("Postgres repository not yet implemented.")
    else:
        raise ValueError(f"Unsupported DATABASE_TYPE: {db_type}")


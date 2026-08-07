from loguru import logger
from qdrant_client import QdrantClient

from vedika import settings


class QdrantDatabaseConnector:
    _instance: QdrantClient | None = None

    @classmethod
    def get_client(cls) -> QdrantClient:
        if cls._instance is None:
            try:
                cls._instance = QdrantClient(host=settings.qdrant.host)

                # verify connection by fetching collection
                _ = cls._instance.get_collections()
                logger.info(f"Successfully connected to Qdrant at {settings.qdrant.host = }")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant at {settings.qdrant.host = }")
                raise e
        return cls._instance

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            logger.info(f"Connection closed to Qdrant at {settings.qdrant.host = }")


qdrant_connection = QdrantDatabaseConnector()

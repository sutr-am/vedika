from loguru import logger
from pymongo import MongoClient

from vedika.settings import settings


class MongoDatabaseConnector:
    _instance: MongoClient | None = None

    @classmethod
    def get_client(cls) -> MongoClient:
        if cls._instance is None:
            try:
                cls._instance = MongoClient(settings.mongo.host, serverSelectionTimeoutMS=5000)
                # verify connection with a ping
                cls._instance.admin.command("ping")
                logger.info(f"Successfully connected to MongoDB at {settings.mongo.host}")
            except ConnectionError as e:
                logger.error(f"Failed to connect to MongoDB at {settings.mongo.host}: {e}")
                raise
        return cls._instance

    @classmethod
    def get_database(cls, db_name: str | None = None):
        client = cls.get_client()
        name = db_name or settings.mongo.db_name
        db = client.get_database(name=name)
        return db

    @classmethod
    def close(cls):
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            logger.info(f"Connection closed to MongoDB at {settings.mongo.host}")


mongo_connection = MongoDatabaseConnector()

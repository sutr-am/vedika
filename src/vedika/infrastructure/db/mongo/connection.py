from loguru import logger
from pymongo import MongoClient

from vedika.settings import settings


class MongoDatabaseConnector:
    _instances: dict[str, MongoClient] = {}

    @classmethod
    def get_client(cls, connection_name: str) -> MongoClient:
        if connection_name not in cls._instances:
            conn_config = settings.connections.get(connection_name)
            if not conn_config or conn_config.driver != "mongo":
                raise ValueError(f"Invalid Mongo Connection profile: {connection_name=}")

            try:
                client = MongoClient(conn_config.host, serverSelectionTimeoutMS=5000)
                client.admin.command("ping")  # verify connection with a ping
                cls._instances[connection_name] = client
                logger.success(f"Successfully connected to MongoDB at {conn_config.host}")
            except ConnectionError as e:
                logger.exception(f"Failed to connect to MongoDB at {conn_config.host}: {e}")
                raise

        return cls._instances[connection_name]

    @classmethod
    def get_database(cls, connection_name: str):
        client = cls.get_client(connection_name=connection_name)
        conn_config = settings.connections.get(connection_name)

        if not conn_config or not conn_config.db_name:
            raise ValueError(f"No db_name configured for profile: {connection_name=}")
        return client.get_database(name=conn_config.db_name)

    @classmethod
    def close(cls, connection_name: str):
        try:
            client = cls._instances.pop(connection_name)
            client.close()
            logger.info(f"Connection closed for MongoDB profile: {connection_name=}")
        except KeyError:
            raise

    @classmethod
    def close_all(cls):
        for name, client in cls._instances.items():
            client.close()
            logger.info(f"Connection closed for MongoDB profile: {name=}")
        cls._instances.clear()


mongo_connection = MongoDatabaseConnector()

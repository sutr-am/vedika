# src/vedika/infrastructure/db/mongo/connection.py
from loguru import logger
from pymongo import MongoClient

from vedika.settings import Settings


class MongoDatabaseConnector:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._instances: dict[str, MongoClient] = {}

    def get_db_name(self, connection_name: str):
        conn_config = self._settings.connections.get(connection_name)
        if conn_config:
            return conn_config.db_name
        return None

    def get_client(self, connection_name: str) -> MongoClient:
        if connection_name not in self._instances:
            conn_config = self._settings.connections.get(connection_name)
            if not conn_config or conn_config.driver != "mongo":
                raise ValueError(f"Invalid Mongo Connection profile: {connection_name=}")

            try:
                client = MongoClient(conn_config.host, serverSelectionTimeoutMS=5000)
                client.admin.command("ping")  # verify connection with a ping
                self._instances[connection_name] = client
                logger.success(f"Successfully connected to MongoDB at {conn_config.host}")
            except ConnectionError as e:
                logger.exception(f"Failed to connect to MongoDB at {conn_config.host}: {e}")
                raise

        return self._instances[connection_name]

    def get_database(self, connection_name: str):
        client = self.get_client(connection_name=connection_name)
        db_name = self.get_db_name(connection_name=connection_name)
        if db_name:
            return client.get_database(name=db_name)
        else:
            return None

    def close(self, connection_name: str):
        try:
            client = self._instances.pop(connection_name)
            client.close()
            logger.info(f"Connection closed for MongoDB profile: {connection_name=}")
        except KeyError:
            raise

    def close_all(self):
        for name, client in self._instances.items():
            client.close()
            logger.info(f"Connection closed for MongoDB profile: {name=}")
        self._instances.clear()

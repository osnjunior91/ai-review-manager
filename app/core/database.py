from pymongo import MongoClient

from app.core.config import get_settings


class MongoDatabase:

    def __init__(self):
        settings = get_settings()

        self.client = MongoClient(
            settings.mongodb_uri,
            serverSelectionTimeoutMS=5000
        )

        self.database = self.client[settings.mongodb_database]

    def ping(self) -> bool:
        self.client.admin.command("ping")
        return True

    def get_collection(self, name: str):
        return self.database[name]

    def close(self) -> None:
        self.client.close()
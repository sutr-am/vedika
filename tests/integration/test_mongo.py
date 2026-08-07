import os

import pytest
from pymongo import AsyncMongoClient


@pytest.mark.asyncio
async def test_mongo_connection():
    db_url = os.getenv(
        "DATABASE_URL",
        "",
    )

    # 1. Connect using native PyMongo Async
    client = AsyncMongoClient(db_url)

    try:
        # 2. Ping MongoDB
        pong = await client.admin.command("ping")
        assert pong["ok"] == 1.0

        # 3. Insert and read back a test document
        db = client.get_default_database()
        test_collection = db["test_collection"]

        result = await test_collection.insert_one({"message": "Hello from vedika!"})
        assert result.inserted_id is not None

        doc = await test_collection.find_one({"_id": result.inserted_id})
        assert doc["message"] == "Hello from vedika!"

        # Clean up test collection
        await test_collection.drop()
    finally:
        await client.close()

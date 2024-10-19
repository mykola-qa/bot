# db/mongo_db_operation.py
import logging
import os

import pymongo
from dotenv import load_dotenv
from pymongo import AsyncMongoClient, DeleteMany


class MongoDBClient:
    def __init__(self):
        load_dotenv()
        self.uri = f"mongodb+srv://{os.environ['MONGO_DB_USERNAME']}:{os.environ['MONGO_DB_PASSWORD']}@cluster0.i0sos.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client: AsyncMongoClient | None = None
        self.database_name = "bot_data"
        self.collection_messages = "messages"

    def connect(self):
        # Connect to MongoDB cluster:
        self.client = AsyncMongoClient(self.uri)

    async def save_message(self, user_id: str, message: str, assistant: bool) -> None:
        db = self.client[self.database_name]
        collection = db[self.collection_messages]
        await collection.insert_one(
            {"user_id": user_id, "message": message, "assistant": assistant}
        )
        logging.info(f"Message {user_id}{message[:10]}... is saved to db. ")

    async def get_context_by_user_id(self, user_id: str) -> list:
        db = self.client[self.database_name]
        collection = db[self.collection_messages]
        async_cursor = collection.find({"user_id": user_id}).sort(
            key_or_list="_id", direction=pymongo.DESCENDING
        )
        counter = 30
        messages = []
        async for entry in async_cursor.sort(
            key_or_list="_id", direction=pymongo.DESCENDING
        ):
            del entry["_id"]
            if entry.get("assistant"):
                messages.append({"role": "assistant", "content": entry["message"]})
            else:
                messages.append({"role": "user", "content": entry["message"]})
            counter -= 1
            if counter == 0:
                break
        logging.info(
            f"Amount of messages - {len(messages)} was collected as context for {user_id} conversation."
        )
        return messages

    async def delete_data_from_db_by_user_id(self, user_id: str):
        db = self.client[self.database_name]
        collection = db[self.collection_messages]
        requests = [DeleteMany({"user_id": user_id})]
        result = await collection.bulk_write(requests)
        logging.info(f"Deleted {result.deleted_count} entries.")

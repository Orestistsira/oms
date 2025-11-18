from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

class DBHandler:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client["omsdb"]
        self.col = self.db["stock"]

    async def get_items(self, item_ids: list):
        result = await self.col.find({"_id": {"$in": item_ids}}).to_list(length=len(item_ids))
        return result

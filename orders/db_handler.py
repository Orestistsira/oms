from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

class DBHandler:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client["omsdb"]
        self.col = self.db["orders"]

    async def create_order(self, doc: dict):
        result = await self.col.insert_one(doc)
        return str(result.inserted_id)

    async def get_order(self, order_id: str, customer_id: str):
        doc = await self.col.find_one({"_id": order_id, "customer_id": customer_id})
        return doc
    
    async def update_order(self, order_id: str, update_fields: dict):
        result = await self.col.update_one(
            {"_id": order_id},
            {"$set": update_fields}
        )
        return result.modified_count

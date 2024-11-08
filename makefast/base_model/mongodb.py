from typing import List, Dict, Any, Mapping
from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoDBBase:
    collection_name: str = ""
    _database: AsyncIOMotorDatabase = None

    @classmethod
    def set_database(cls, database: AsyncIOMotorDatabase):
        cls._database = database

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        if cls._database is None:
            raise HTTPException(status_code=500, detail="MongoDB connection not initialized")
        return cls._database

    @classmethod
    def get_collection(cls):
        database = cls.get_database()
        try:
            return database[cls.collection_name]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error accessing collection: {str(e)}")

    @classmethod
    async def create(cls, **kwargs) -> Dict[str, Any]:
        collection = cls.get_collection()
        result = await collection.insert_one(kwargs)
        return {**kwargs, "_id": str(result.inserted_id)}

    @classmethod
    async def find(cls, id: str) -> Mapping[str, Any]:
        collection = cls.get_collection()
        result = await collection.find_one({"_id": ObjectId(id)})
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found")
        result["_id"] = str(result["_id"])
        return result

    @classmethod
    async def all(cls) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        cursor = collection.find()
        results = await cursor.to_list(length=None)
        for result in results:
            result["_id"] = str(result["_id"])
        return results

    @classmethod
    async def update(cls, id: str, **kwargs) -> Mapping[str, Any]:
        collection = cls.get_collection()
        result = await collection.update_one({"_id": ObjectId(id)}, {"$set": kwargs})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return await cls.find(id)

    @classmethod
    async def delete(cls, id: str) -> Dict[str, bool]:
        collection = cls.get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"success": True}

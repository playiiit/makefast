from typing import List, Dict, Any, Mapping, Optional
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
    async def find(cls, data: Any) -> Dict[str, Any] | None:
        collection = cls.get_collection()
        result = await collection.find_one(data)
        if result is None:
            return None
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
    async def get(
            cls, query: Any, limit: Optional[int] = None, fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        collection = cls.get_collection()

        pipeline = [
            {"$match": query},
            {"$limit": limit} if limit else {},
            {"$project": {field: 1 for field in fields} | {"_id": 1}} if fields else {},
            {"$addFields": {"_id": {"$toString": "$_id"}}}
        ]
        pipeline = [stage for stage in pipeline if stage]

        cursor = collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    @classmethod
    async def update(cls, id: str, data: dict) -> Dict[str, Any] | int:
        collection = cls.get_collection()
        result = await collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.matched_count == 0:
            return 0
        return await cls.find({"_id": ObjectId(id)})

    @classmethod
    async def delete(cls, id: str) -> Dict[str, bool] | 0:
        collection = cls.get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        if result.deleted_count == 0:
            return 0
        return {"success": True}

    @classmethod
    async def delete_all(cls, query: Any) -> Dict[str, bool] | 0:
        collection = cls.get_collection()
        result = await collection.delete_many(query)
        if result.deleted_count == 0:
            return 0
        return {"success": True}

    @classmethod
    async def aggregate(cls, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        collection = cls.get_collection()
        try:
            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Aggregation error: {str(e)}")

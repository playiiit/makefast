from typing import List, Dict, Any, Optional, Union
from fastapi import HTTPException
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime
import re


class MongoDBBase:
    collection_name: str = ""
    fillable: List[str] = []
    guarded: List[str] = ['_id']
    timestamps: bool = True
    primary_key: str = "_id"
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
    def _prepare_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for database operations"""
        if cls.fillable:
            data = {k: v for k, v in data.items() if k in cls.fillable}
        
        # Remove guarded fields
        for field in cls.guarded:
            data.pop(field, None)
        
        # Add timestamps
        if cls.timestamps:
            now = datetime.utcnow()
            if 'created_at' not in data:
                data['created_at'] = now
            data['updated_at'] = now
        
        return data

    @classmethod
    def _format_result(cls, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format result with string _id"""
        if result and "_id" in result:
            result["_id"] = str(result["_id"])
        return result

    @classmethod
    def _format_results(cls, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format multiple results with string _id"""
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
        return results

    @classmethod
    def _to_object_id(cls, id_value: Union[str, ObjectId]) -> ObjectId:
        """Convert string ID to ObjectId"""
        if isinstance(id_value, str):
            try:
                return ObjectId(id_value)
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        return id_value

    # Basic CRUD Operations
    @classmethod
    async def create(cls, **kwargs) -> Dict[str, Any]:
        """Create a new document"""
        try:
            collection = cls.get_collection()
            data = cls._prepare_data(kwargs)
            result = await collection.insert_one(data)
            return {**data, "_id": str(result.inserted_id)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Create error: {str(e)}")

    @classmethod
    async def find(cls, id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Find a document by ID"""
        try:
            collection = cls.get_collection()
            object_id = cls._to_object_id(id)
            result = await collection.find_one({"_id": object_id})
            if result is None:
                raise HTTPException(status_code=404, detail="Document not found")
            return cls._format_result(result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Find error: {str(e)}")

    @classmethod
    async def find_or_fail(cls, id: Union[str, ObjectId]) -> Dict[str, Any]:
        """Find a document by ID or raise exception"""
        return await cls.find(id)

    @classmethod
    async def first(cls, query: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Get the first document"""
        try:
            collection = cls.get_collection()
            result = await collection.find_one(query or {})
            return cls._format_result(result) if result else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"First error: {str(e)}")

    @classmethod
    async def first_or_fail(cls, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get the first document or raise exception"""
        result = await cls.first(query)
        if result is None:
            raise HTTPException(status_code=404, detail="No documents found")
        return result

    @classmethod
    async def all(cls) -> List[Dict[str, Any]]:
        """Get all documents"""
        try:
            collection = cls.get_collection()
            cursor = collection.find()
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"All error: {str(e)}")

    @classmethod
    async def get(cls, query: Dict[str, Any] = None, limit: Optional[int] = None, 
                  fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get documents with query, limit, and field selection"""
        try:
            collection = cls.get_collection()
            pipeline = []
            
            if query:
                pipeline.append({"$match": query})
            
            if fields:
                projection = {field: 1 for field in fields}
                projection["_id"] = 1
                pipeline.append({"$project": projection})
            
            if limit:
                pipeline.append({"$limit": limit})
            
            pipeline.append({"$addFields": {"_id": {"$toString": "$_id"}}})
            
            cursor = collection.aggregate(pipeline)
            return await cursor.to_list(length=limit)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Get error: {str(e)}")

    @classmethod
    async def update(cls, id: Union[str, ObjectId], **kwargs) -> Dict[str, Any]:
        """Update a document"""
        try:
            collection = cls.get_collection()
            object_id = cls._to_object_id(id)
            data = cls._prepare_data(kwargs)
            
            result = await collection.update_one(
                {"_id": object_id}, 
                {"$set": data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return await cls.find(object_id)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update error: {str(e)}")

    @classmethod
    async def delete(cls, id: Union[str, ObjectId]) -> Dict[str, bool]:
        """Delete a document"""
        try:
            collection = cls.get_collection()
            object_id = cls._to_object_id(id)
            result = await collection.delete_one({"_id": object_id})
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Document not found")
            
            return {"success": True}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete error: {str(e)}")

    # Query Builder Methods
    @classmethod
    async def where(cls, field: str, operator: str = "=", value: Any = None) -> List[Dict[str, Any]]:
        """Filter documents by a condition"""
        try:
            collection = cls.get_collection()
            
            if value is None:
                value = operator
                operator = "="
            
            # Build MongoDB query based on operator
            if operator == "=":
                query = {field: value}
            elif operator == "!=":
                query = {field: {"$ne": value}}
            elif operator == ">":
                query = {field: {"$gt": value}}
            elif operator == ">=":
                query = {field: {"$gte": value}}
            elif operator == "<":
                query = {field: {"$lt": value}}
            elif operator == "<=":
                query = {field: {"$lte": value}}
            elif operator == "like":
                query = {field: {"$regex": value, "$options": "i"}}
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported operator: {operator}")
            
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where error: {str(e)}")

    @classmethod
    async def where_in(cls, field: str, values: List[Any]) -> List[Dict[str, Any]]:
        """Filter documents where field is in values list"""
        try:
            collection = cls.get_collection()
            query = {field: {"$in": values}}
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where in error: {str(e)}")

    @classmethod
    async def where_not_in(cls, field: str, values: List[Any]) -> List[Dict[str, Any]]:
        """Filter documents where field is not in values list"""
        try:
            collection = cls.get_collection()
            query = {field: {"$nin": values}}
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where not in error: {str(e)}")

    @classmethod
    async def where_null(cls, field: str) -> List[Dict[str, Any]]:
        """Filter documents where field is null or doesn't exist"""
        try:
            collection = cls.get_collection()
            query = {field: {"$in": [None, "$exists"]}}
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where null error: {str(e)}")

    @classmethod
    async def where_not_null(cls, field: str) -> List[Dict[str, Any]]:
        """Filter documents where field is not null and exists"""
        try:
            collection = cls.get_collection()
            query = {field: {"$ne": None, "$exists": True}}
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where not null error: {str(e)}")

    @classmethod
    async def where_multiple(cls, **kwargs) -> List[Dict[str, Any]]:
        """Filter by multiple conditions (AND)"""
        try:
            collection = cls.get_collection()
            cursor = collection.find(kwargs)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where multiple error: {str(e)}")

    @classmethod
    async def where_regex(cls, field: str, pattern: str, options: str = "i") -> List[Dict[str, Any]]:
        """Filter documents using regex pattern"""
        try:
            collection = cls.get_collection()
            query = {field: {"$regex": pattern, "$options": options}}
            cursor = collection.find(query)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Where regex error: {str(e)}")

    @classmethod
    async def order_by(cls, field: str, direction: int = 1) -> List[Dict[str, Any]]:
        """Order documents by a field (1 for ASC, -1 for DESC)"""
        try:
            collection = cls.get_collection()
            cursor = collection.find().sort(field, direction)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Order by error: {str(e)}")

    @classmethod
    async def limit(cls, count: int, skip: int = 0) -> List[Dict[str, Any]]:
        """Limit the number of documents with optional skip"""
        try:
            collection = cls.get_collection()
            cursor = collection.find().skip(skip).limit(count)
            results = await cursor.to_list(length=count)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Limit error: {str(e)}")

    @classmethod
    async def paginate(cls, page: int = 1, per_page: int = 15, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Paginate documents"""
        try:
            collection = cls.get_collection()
            skip = (page - 1) * per_page
            search_query = query or {}
            
            # Get total count
            total = await collection.count_documents(search_query)
            
            # Get paginated data
            cursor = collection.find(search_query).skip(skip).limit(per_page)
            data = await cursor.to_list(length=per_page)
            data = cls._format_results(data)
            
            return {
                'data': data,
                'total': total,
                'per_page': per_page,
                'current_page': page,
                'last_page': (total + per_page - 1) // per_page if total > 0 else 1,
                'from': skip + 1 if data else 0,
                'to': skip + len(data) if data else 0
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Paginate error: {str(e)}")

    # Aggregate Methods
    @classmethod
    async def count(cls, query: Dict[str, Any] = None) -> int:
        """Count documents"""
        try:
            collection = cls.get_collection()
            return await collection.count_documents(query or {})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Count error: {str(e)}")

    @classmethod
    async def sum(cls, field: str, query: Dict[str, Any] = None) -> float:
        """Sum values of a field"""
        try:
            collection = cls.get_collection()
            pipeline = []
            
            if query:
                pipeline.append({"$match": query})
            
            pipeline.extend([
                {"$group": {"_id": None, "total": {"$sum": f"${field}"}}},
                {"$project": {"_id": 0, "total": 1}}
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            return result[0]["total"] if result else 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Sum error: {str(e)}")

    @classmethod
    async def avg(cls, field: str, query: Dict[str, Any] = None) -> float:
        """Average values of a field"""
        try:
            collection = cls.get_collection()
            pipeline = []
            
            if query:
                pipeline.append({"$match": query})
            
            pipeline.extend([
                {"$group": {"_id": None, "average": {"$avg": f"${field}"}}},
                {"$project": {"_id": 0, "average": 1}}
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            return result[0]["average"] if result else 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Average error: {str(e)}")

    @classmethod
    async def max(cls, field: str, query: Dict[str, Any] = None) -> Any:
        """Get maximum value of a field"""
        try:
            collection = cls.get_collection()
            pipeline = []
            
            if query:
                pipeline.append({"$match": query})
            
            pipeline.extend([
                {"$group": {"_id": None, "max_value": {"$max": f"${field}"}}},
                {"$project": {"_id": 0, "max_value": 1}}
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            return result[0]["max_value"] if result else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Max error: {str(e)}")

    @classmethod
    async def min(cls, field: str, query: Dict[str, Any] = None) -> Any:
        """Get minimum value of a field"""
        try:
            collection = cls.get_collection()
            pipeline = []
            
            if query:
                pipeline.append({"$match": query})
            
            pipeline.extend([
                {"$group": {"_id": None, "min_value": {"$min": f"${field}"}}},
                {"$project": {"_id": 0, "min_value": 1}}
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=1)
            return result[0]["min_value"] if result else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Min error: {str(e)}")

    # Utility Methods
    @classmethod
    async def exists(cls, id: Union[str, ObjectId]) -> bool:
        """Check if a document exists"""
        try:
            collection = cls.get_collection()
            object_id = cls._to_object_id(id)
            count = await collection.count_documents({"_id": object_id})
            return count > 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Exists error: {str(e)}")

    @classmethod
    async def get_or_create(cls, query: Dict[str, Any], defaults: Dict[str, Any] = None) -> tuple[Dict[str, Any], bool]:
        """Get existing document or create new one"""
        try:
            # Try to find existing document
            existing = await cls.first(query)
            if existing:
                return existing, False
            
            # Create new document
            create_data = {**query}
            if defaults:
                create_data.update(defaults)
            
            new_doc = await cls.create(**create_data)
            return new_doc, True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Get or create error: {str(e)}")

    @classmethod
    async def update_or_create(cls, query: Dict[str, Any], defaults: Dict[str, Any] = None) -> tuple[Dict[str, Any], bool]:
        """Update existing document or create new one"""
        try:
            existing = await cls.first(query)
            if existing:
                # Update existing document
                update_data = defaults or {}
                updated_doc = await cls.update(existing["_id"], **update_data)
                return updated_doc, False
            else:
                # Create new document
                create_data = {**query}
                if defaults:
                    create_data.update(defaults)
                
                new_doc = await cls.create(**create_data)
                return new_doc, True
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update or create error: {str(e)}")

    @classmethod
    async def bulk_create(cls, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create multiple documents in bulk"""
        try:
            collection = cls.get_collection()
            prepared_data = [cls._prepare_data(data) for data in data_list]
            result = await collection.insert_many(prepared_data)
            
            # Return created documents with string IDs
            created_docs = []
            for i, inserted_id in enumerate(result.inserted_ids):
                doc = {**prepared_data[i], "_id": str(inserted_id)}
                created_docs.append(doc)
            
            return created_docs
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bulk create error: {str(e)}")

    @classmethod
    async def update_many(cls, query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update multiple documents"""
        try:
            collection = cls.get_collection()
            data = cls._prepare_data(update_data)
            result = await collection.update_many(query, {"$set": data})
            return result.modified_count
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update many error: {str(e)}")

    @classmethod
    async def delete_many(cls, query: Dict[str, Any]) -> int:
        """Delete multiple documents"""
        try:
            collection = cls.get_collection()
            result = await collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Delete many error: {str(e)}")

    @classmethod
    async def aggregate(cls, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline"""
        try:
            collection = cls.get_collection()
            cursor = collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return cls._format_results(results)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Aggregation error: {str(e)}")

    @classmethod
    async def distinct(cls, field: str, query: Dict[str, Any] = None) -> List[Any]:
        """Get distinct values for a field"""
        try:
            collection = cls.get_collection()
            return await collection.distinct(field, query or {})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Distinct error: {str(e)}")

    @classmethod
    async def create_index(cls, fields: Union[str, List[tuple]], **kwargs) -> str:
        """Create an index on the collection"""
        try:
            collection = cls.get_collection()
            if isinstance(fields, str):
                fields = [(fields, 1)]
            return await collection.create_index(fields, **kwargs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Create index error: {str(e)}")

    @classmethod
    async def drop_index(cls, index_name: str) -> None:
        """Drop an index from the collection"""
        try:
            collection = cls.get_collection()
            await collection.drop_index(index_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Drop index error: {str(e)}")

    @classmethod
    async def list_indexes(cls) -> List[Dict[str, Any]]:
        """List all indexes on the collection"""
        try:
            collection = cls.get_collection()
            return await collection.list_indexes().to_list(length=None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"List indexes error: {str(e)}")
    
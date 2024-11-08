import os
from dotenv import load_dotenv
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from makefast.base_model.mongodb import MongoDBBase

load_dotenv()


class MongoDBDatabaseInit:
    @staticmethod
    def init(app: FastAPI):
        @app.on_event("startup")
        async def startup_db_client():
            mongodb_client = AsyncIOMotorClient(
                f"mongodb+srv://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_CLUSTER')}.xudfnwp.mongodb.net/"
            )
            database = mongodb_client[os.getenv("DB_DATABASE")]
            MongoDBBase.set_database(database)

        @app.on_event("shutdown")
        async def shutdown_db_client():
            mongodb_client = MongoDBBase.get_database().client
            mongodb_client.close()

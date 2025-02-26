import os
from dotenv import load_dotenv
from .mongodb import MongoDBMigration

load_dotenv()


class Migration:
    @classmethod
    async def create(cls, name, data=None):
        database_type = os.getenv("DB_CONNECTION")

        # If the database type mongodb
        if database_type == "mongodb":
            await MongoDBMigration.create_collections(name, data)

        # If the database type mysql
        if database_type == "mysql":
            await MongoDBMigration.create_collections(name, data)

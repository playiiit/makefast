from makefast.database import MongoDBDatabaseInit
from motor.motor_asyncio import AsyncIOMotorDatabase


class MongoDBMigration:
    _database: AsyncIOMotorDatabase = None

    @classmethod
    def init_database(cls):
        if cls._database is None:
            cls._database = MongoDBDatabaseInit.get_database_connection()

    @classmethod
    async def create_collections(cls, name, data):
        """
        Creates a new collection in the database if it does not already exist.

        Args:
            name (str): The name of the collection to create.
            data (Any): Collection object data

        Returns:
            None
        """
        try:
            if cls._database is None:
                cls.init_database()

            # Get list of collections using the to_list() method
            collections = await cls._database.list_collection_names()
            if f"{name}" not in collections:
                # Create the collection
                await cls._database.create_collection(f"{name}")

                # Insert the collection data
                if data is not None:
                    await cls._insert_data(name, data)

                print(f"Created {name} collection")
        except Exception as e:
            print(e)
            raise

    @classmethod
    async def _insert_data(cls, name, data):
        """
        Insert sample data into collections.

        Args:
            name (str): The name of the collection
            data (Any): Collection object data

        Returns:
            None
        """
        try:
            await cls._database[name].insert_one(data)
        except Exception as e:
            print(e)
            raise

import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

uri = f"mongodb+srv://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_CLUSTER")}.xudfnwp.mongodb.net/?retryWrites=true&w=majority&appName={os.getenv("DB_CLUSTER")}"


def get_database():
    try:
        cluster = AsyncIOMotorClient(uri)
        db = cluster[os.getenv("DB_DATABASE")]
        return db
    except Exception as e:
        print(e)


mongodb_connection = get_database()

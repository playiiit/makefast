import os
import pymongo
from dotenv import load_dotenv

load_dotenv()


def mongodb_connection_test():
    uri = f"mongodb+srv://{os.getenv("MONGODB_USERNAME")}:{os.getenv("MONGODB_PASSWORD")}@{os.getenv("MONGODB_CLUSTER")}.xudfnwp.mongodb.net/?retryWrites=true&w=majority&appName={os.getenv("MONGODB_CLUSTER")}"
    client = pymongo.MongoClient(uri)
    # Your code here
    print(client.admin.command("ping"))


if __name__ == "__main__":
    mongodb_connection_test()

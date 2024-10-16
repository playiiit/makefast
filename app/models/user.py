from makefast.base_model.mongodb import MongoDBBase


class User(MongoDBBase):
    collection_name = "users"


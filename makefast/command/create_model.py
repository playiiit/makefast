import os
import click
from makefast.utils import update_init_file, table_name_generator
from dotenv import load_dotenv

load_dotenv()


class CreateModel:
    @classmethod
    def execute(cls, name, table="", collection=""):
        # If table name not exists
        if table is None:
            table = f'"{table_name_generator(name.lower())}"'
        # If collection name not exists
        if collection is None:
            collection = f'"{table_name_generator(name.lower())}"'
        # Get the model template
        model_template = cls.get_template(name, table, collection)
        # Create the model file
        with open(f"app/models/{name.lower()}.py", "w") as f:
            f.write(model_template)

        init_file_path = "app/models/__init__.py"
        import_statement = f"from .{name.lower()} import {name.capitalize()}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{name.capitalize()} model created successfully.")

    @classmethod
    def get_template(cls, name, table, collection):
        match os.getenv("DB_CONNECTION"):
            case "mysql":
                return cls.get_mysql_template(name=name, table=table)
            case "mongodb":
                return cls.get_mongodb_template(name=name, collection=collection)
            case _:
                return cls.get_mysql_template(name=name, table=table)

    @staticmethod
    def get_mongodb_template(name, collection) -> str:
        return f"""from makefast.base_model.mongodb import MongoDBBase


class {name.capitalize()}(MongoDBBase):
    collection_name = {collection}

"""

    @staticmethod
    def get_mysql_template(name, table) -> str:
        return f"""from makefast.base_model.mysql import MySQLBase


class {name.capitalize()}(MySQLBase):
    table_name = {table}
    columns = []

"""

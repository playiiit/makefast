import os
import click
from makefast.utils import update_init_file, table_name_generator, convert_to_snake_case, generate_class_name
from dotenv import load_dotenv

load_dotenv()


class CreateModel:
    @classmethod
    def execute(cls, name, table="", collection=""):
        # Support path-style names like "v1/User" or "Admin/Post"
        parts = name.replace("\\", "/").split("/")
        path_prefix = "/".join(parts[:-1])  # e.g. "v1" or ""
        raw_name = parts[-1]               # e.g. "User"

        # Build the target directory, honouring any path prefix
        if path_prefix:
            models_dir = os.path.join("app", "models", *path_prefix.split("/"))
        else:
            models_dir = "app/models"

        if not os.path.exists(models_dir):
            os.makedirs(models_dir, exist_ok=True)

        # Ensure every directory in the chain has an __init__.py
        chain = os.path.join("app", "models")
        if not os.path.exists(chain):
            os.makedirs(chain, exist_ok=True)
        if not os.path.exists(os.path.join(chain, "__init__.py")):
            open(os.path.join(chain, "__init__.py"), "w").close()
        for part in (path_prefix.split("/") if path_prefix else []):
            chain = os.path.join(chain, part)
            init_in_chain = os.path.join(chain, "__init__.py")
            if not os.path.exists(init_in_chain):
                open(init_in_chain, "w").close()

        # If table name not exists
        if table == "" or table is None:
            table = f'"{table_name_generator(convert_to_snake_case(raw_name.lower()))}"'
        # If collection name not exists
        if collection == "" or collection is None:
            collection = f'"{table_name_generator(convert_to_snake_case(raw_name.lower()))}"'
        # Get the model template
        model_template = cls.get_template(raw_name, table, collection)
        # Create the model file
        file_name = convert_to_snake_case(raw_name.lower())
        with open(os.path.join(models_dir, f"{file_name}.py"), "w") as f:
            f.write(model_template)

        init_file_path = os.path.join(models_dir, "__init__.py")
        import_statement = f"from .{file_name} import {generate_class_name(raw_name.capitalize())}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{raw_name.capitalize()} model created successfully.")

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


class {generate_class_name(name.capitalize())}(MongoDBBase):
    collection_name = {collection}
"""

    @staticmethod
    def get_mysql_template(name, table) -> str:
        return f"""from makefast.base_model.mysql import MySQLBase


class {generate_class_name(name.capitalize())}(MySQLBase):
    table_name = {table}
    columns = []
"""

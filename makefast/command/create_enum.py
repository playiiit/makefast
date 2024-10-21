import os
import click
from makefast.utils import update_init_file


class CreateEnum:
    @classmethod
    def execute(cls, name, enum_type):
        if enum_type is None:
            enum_type = "str"
        # Ensure enum directory exists
        if not os.path.exists("app/enums"):
            os.makedirs("app/enums")

        enum_template = cls.get_template(name, enum_type)
        with open(f"app/enums/{name.lower()}.py", "w") as f:
            f.write(enum_template)

        init_file_path = "app/enums/__init__.py"
        import_statement = f"from .{name.lower()} import {name.capitalize()}Enum\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{name.capitalize()} enum created successfully.")

    @staticmethod
    def get_template(name, type) -> str:
        return f"""from enum import Enum


class {name.capitalize()}Enum({type}, Enum):
    pass

"""

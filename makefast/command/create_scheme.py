import os
import click
from makefast.utils import update_init_file, convert_to_snake_case


class CreateSchema:
    @classmethod
    def execute(cls, name):
        # Ensure scheme directory exists
        if not os.path.exists("app/schemas"):
            os.makedirs("app/schemas")

        scheme_template = cls.get_template(name)
        with open(f"app/schemas/{convert_to_snake_case(name)}.py", "w") as f:
            f.write(scheme_template)

        init_file_path = "app/schemas/__init__.py"
        import_statement = f"from .{convert_to_snake_case(name)} import {name}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{name} schema created successfully.")

    @staticmethod
    def get_template(name) -> str:
        return f"""from pydantic import BaseModel


class {name}(BaseModel):
    id: int
"""

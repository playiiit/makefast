import os
import click
from makefast.utils import update_init_file


class CreateScheme:
    @classmethod
    def execute(cls, name):
        # Ensure scheme directory exists
        if not os.path.exists("app/schemes"):
            os.makedirs("app/schemes")

        scheme_template = cls.get_template(name)
        with open(f"app/schemes/{name.lower()}.py", "w") as f:
            f.write(scheme_template)

        init_file_path = "app/schemes/__init__.py"
        import_statement = f"from .{name.lower()} import {name.capitalize()}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{name.capitalize()} scheme created successfully.")

    @staticmethod
    def get_template(name) -> str:
        return f"""from pydantic import BaseModel


class {name.capitalize()}(BaseModel):
    id: int

"""

import os
import click
from makefast.utils import update_init_file, convert_to_snake_case, generate_class_name


class CreateScheme:
    @classmethod
    def execute(cls, name):
        # Ensure scheme directory exists
        if not os.path.exists("app/schemes"):
            os.makedirs("app/schemes")

        scheme_template = cls.get_template(name)
        with open(f"app/schemes/{convert_to_snake_case(name.lower())}.py", "w") as f:
            f.write(scheme_template)

        init_file_path = "app/schemes/__init__.py"
        import_statement = f"from .{convert_to_snake_case(name.lower())} import {generate_class_name(name.capitalize())}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{generate_class_name(name.capitalize())} scheme created successfully.")

    @staticmethod
    def get_template(name) -> str:
        return f"""from pydantic import BaseModel


class {generate_class_name(name.capitalize())}(BaseModel):
    id: int
"""

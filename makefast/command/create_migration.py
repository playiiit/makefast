import os
import datetime
import click
from makefast.utils import convert_to_snake_case
from makefast.utils import generate_class_name, update_init_file

# TODO:: Update the README file with how to add the env for database

class CreateMigration:
    @classmethod
    def execute(cls, name):
        # Ensure migrations directory exists
        if not os.path.exists("app/migrations"):
            os.makedirs("app/migrations")

        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Create filename
        filename = f"_{timestamp}_{convert_to_snake_case(name)}"

        # Migration file template
        template = cls._get_mongodb_template(name)

        # Write the migration file
        with open(f"app/migrations/{filename}.py", "w") as f:
            f.write(template)

        # Add the class to the init file
        init_file_path = "app/migrations/__init__.py"
        import_statement = f"from .{filename} import {generate_class_name(name.capitalize())}\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"{filename} migration created successfully.")

    @staticmethod
    def _get_mongodb_template(name) -> str:
        return f"""from makefast.migration import Migration


class {generate_class_name(name.capitalize())}:
    
    @classmethod
    async def run(cls):
        try:
            await Migration.create("{name}", {{}})
        except Exception as e:
            print(e)

"""

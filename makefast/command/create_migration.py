import os
import datetime
import click
from makefast.utils import convert_to_snake_case


class CreateMigration:
    @classmethod
    def execute(cls, name):
        # Ensure migrations directory exists
        if not os.path.exists("app/migrations"):
            os.makedirs("app/migrations")

        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Create filename
        filename = f"{timestamp}_{convert_to_snake_case(name)}.py"

        # Migration file template
        template = cls.get_template()

        # Write the migration file
        with open(f"app/migrations/{filename}", "w") as f:
            f.write(template)

        click.echo(f"{filename} migration created successfully.")

    @staticmethod
    def get_template() -> str:
        return f"""
# Migration Code Here        
"""

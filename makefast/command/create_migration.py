import os
import datetime
import click


class CreateMigration:
    @classmethod
    def execute(cls, name):
        # Ensure migrations directory exists
        if not os.path.exists("app/migrations"):
            os.makedirs("app/migrations")

        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        # Create filename
        filename = f"{timestamp}_{name}.py"

        # Migration file template
        template = cls.get_template()

        # Write the migration file
        with open(f"app/migrations/{filename}", "w") as f:
            f.write(template)

        click.echo(f"{name.capitalize()} migration created successfully.")

    @staticmethod
    def get_template() -> str:
        return f"""from pymongo import MongoClient


def upgrade(db):
    # Implement your upgrade logic here
    # For example:
    # db.your_collection.create_index('field_name')
    pass


def downgrade(db):
    # Implement your downgrade logic here
    # For example:
    # db.your_collection.drop_index('field_name')
    pass


# This allows you to run the migration manually
if __name__ == '__main__':
    client = MongoClient('your_mongodb_uri')
    db = client.your_database_name
    upgrade(db)
    # To run downgrade, comment out the line above and uncomment the line below
    # downgrade(db)
"""

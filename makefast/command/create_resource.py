import os
import click
from makefast.utils import update_init_file, convert_to_snake_case, generate_class_name


class CreateResource:
    """CLI command handler: makefast create_resource <Name> [--collection]"""

    @classmethod
    def execute(cls, name: str, collection: bool = False) -> None:
        # Support path-style names like "v1/UserResource" or "Admin/PostResource"
        parts = name.replace("\\", "/").split("/")
        path_prefix = "/".join(parts[:-1])  # e.g. "v1" or ""
        raw_name = parts[-1]               # e.g. "UserResource"

        # Build the target directory, honouring any path prefix
        if path_prefix:
            resources_dir = os.path.join("app", "resources", *path_prefix.split("/"))
        else:
            resources_dir = "app/resources"

        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)

        # Ensure every directory in the chain has an __init__.py
        chain = os.path.join("app", "resources")
        if not os.path.exists(chain):
            os.makedirs(chain, exist_ok=True)
        if not os.path.exists(os.path.join(chain, "__init__.py")):
            open(os.path.join(chain, "__init__.py"), "w").close()
        for part in (path_prefix.split("/") if path_prefix else []):
            chain = os.path.join(chain, part)
            init_in_chain = os.path.join(chain, "__init__.py")
            if not os.path.exists(init_in_chain):
                open(init_in_chain, "w").close()

        if collection:
            cls._create_collection(raw_name, resources_dir)
        else:
            cls._create_resource(raw_name, resources_dir)

    # ------------------------------------------------------------------
    # Single Resource
    # ------------------------------------------------------------------
    @classmethod
    def _create_resource(cls, name: str, resources_dir: str) -> None:
        class_name = generate_class_name(name.capitalize())
        file_name = convert_to_snake_case(name)

        template = cls.get_resource_template(class_name)
        file_path = f"{resources_dir}/{file_name}.py"

        with open(file_path, "w") as f:
            f.write(template)

        init_file_path = f"{resources_dir}/__init__.py"
        import_statement = f"from .{file_name} import {class_name}\n"
        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"✅  {class_name} resource created at {file_path}")

    # ------------------------------------------------------------------
    # Collection Resource
    # ------------------------------------------------------------------
    @classmethod
    def _create_collection(cls, name: str, resources_dir: str) -> None:
        # e.g. "user" → UserResource + UserCollection
        resource_class_name = generate_class_name(name.capitalize()) + "Resource"
        collection_class_name = generate_class_name(name.capitalize()) + "Collection"
        resource_file_name = convert_to_snake_case(name)
        collection_file_name = resource_file_name + "_collection"

        # Always scaffold the base Resource too (so the import in the collection works)
        resource_file_path = f"{resources_dir}/{resource_file_name}.py"
        if not os.path.exists(resource_file_path):
            cls._create_resource(name, resources_dir)

        # Now scaffold the Collection
        template = cls.get_collection_template(resource_class_name, collection_class_name, name)
        file_path = f"{resources_dir}/{collection_file_name}.py"

        with open(file_path, "w") as f:
            f.write(template)

        init_file_path = f"{resources_dir}/__init__.py"
        import_statement = f"from .{collection_file_name} import {collection_class_name}\n"
        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"✅  {collection_class_name} resource collection created at {file_path}")

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------
    @staticmethod
    def get_resource_template(class_name: str) -> str:
        return f"""from typing import Any, Dict
from makefast.http import Resource


class {class_name}(Resource):
    \"\"\"
    API Resource: {class_name}

    Transform a single model record into a JSON-friendly dict.
    Access raw data via self.data["field"] or self.get("field", default).
    \"\"\"

    def to_dict(self) -> Dict[str, Any]:
        return {{
            "id": self.data.get("id"),
            # Add more fields here ...
        }}
"""

    @staticmethod
    def get_collection_template(
        resource_class_name: str,
        collection_class_name: str,
        name: str,
    ) -> str:
        resource_file = convert_to_snake_case(name)
        return f"""from typing import Any, Dict, List
from makefast.http import ResourceCollection
from app.resources.{resource_file} import {resource_class_name}


class {collection_class_name}(ResourceCollection):
    \"\"\"
    Resource Collection: {collection_class_name}

    Transforms a list of model records using {resource_class_name}.
    Supports pagination via .with_pagination(paginate_result).

    Usage:
        items = await MyModel.all()
        return {collection_class_name}(items).response()

        # With pagination:
        page = await MyModel.paginate(page=1, per_page=15)
        return {collection_class_name}(page["data"]).with_pagination(page).response()
    \"\"\"

    resource_class = {resource_class_name}
"""


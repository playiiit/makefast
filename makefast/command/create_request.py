import os
import click
from makefast.utils import update_init_file, convert_to_snake_case, generate_class_name


class CreateRequest:
    """CLI command handler: makefast create_request <Name>"""

    @classmethod
    def execute(cls, name: str) -> None:
        # Support path-style names like "v1/StoreRequest" or "Auth/LoginRequest"
        parts = name.replace("\\", "/").split("/")
        path_prefix = "/".join(parts[:-1])  # e.g. "v1" or ""
        raw_name = parts[-1]               # e.g. "StoreRequest"

        # Build the target directory, honouring any path prefix
        if path_prefix:
            requests_dir = os.path.join("app", "requests", *path_prefix.split("/"))
        else:
            requests_dir = "app/requests"

        if not os.path.exists(requests_dir):
            os.makedirs(requests_dir)

        # Ensure every directory in the chain has an __init__.py
        chain = os.path.join("app", "requests")
        if not os.path.exists(chain):
            os.makedirs(chain, exist_ok=True)
        if not os.path.exists(os.path.join(chain, "__init__.py")):
            open(os.path.join(chain, "__init__.py"), "w").close()
        for part in (path_prefix.split("/") if path_prefix else []):
            chain = os.path.join(chain, part)
            init_in_chain = os.path.join(chain, "__init__.py")
            if not os.path.exists(init_in_chain):
                open(init_in_chain, "w").close()

        class_name = generate_class_name(raw_name.capitalize())
        file_name = convert_to_snake_case(raw_name)

        template = cls.get_template(class_name)
        file_path = os.path.join(requests_dir, f"{file_name}.py")

        with open(file_path, "w") as f:
            f.write(template)

        init_file_path = os.path.join(requests_dir, "__init__.py")
        import_statement = f"from .{file_name} import {class_name}\n"
        update_init_file(file_path=init_file_path, statement=import_statement)

        click.echo(f"✅  {class_name} request class created at {file_path}")

    @staticmethod
    def get_template(class_name: str) -> str:
        return f"""from typing import Any, Dict
from makefast.http import FormRequest


class {class_name}(FormRequest):
    \"\"\"
    Form Request: {class_name}

    Define validation rules in rules(), custom messages in messages(),
    and authorization logic in authorize().
    \"\"\"

    def authorize(self) -> bool:
        # Return False to reject unauthorized requests (raises 403)
        return True

    def rules(self) -> Dict[str, Any]:
        return {{
            # "field": ["required", "string", "max:255"],
        }}

    def messages(self) -> Dict[str, str]:
        return {{
            # "field.required": "The field is required.",
        }}
"""

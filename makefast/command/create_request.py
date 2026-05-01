import os
import click
from makefast.utils import update_init_file, convert_to_snake_case, generate_class_name


class CreateRequest:
    """CLI command handler: makefast create_request <Name>"""

    @classmethod
    def execute(cls, name: str) -> None:
        # Ensure requests directory exists
        requests_dir = "app/requests"
        if not os.path.exists(requests_dir):
            os.makedirs(requests_dir)

        class_name = generate_class_name(name.capitalize())
        file_name = convert_to_snake_case(name)

        template = cls.get_template(class_name)
        file_path = f"{requests_dir}/{file_name}.py"

        with open(file_path, "w") as f:
            f.write(template)

        init_file_path = f"{requests_dir}/__init__.py"
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

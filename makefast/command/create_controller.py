import click
import os
from makefast.utils import update_init_file, generate_class_name, convert_to_snake_case, convert_to_hyphen
from .create_model import CreateModel
from .create_scheme import CreateSchema


class CreateController:
    @staticmethod
    def execute(name, model, request_scheme, response_scheme):
        if name.lower().endswith("controller"):
            base_name = name[:-10]
        else:
            base_name = name

        class_name = f"{generate_class_name(base_name.capitalize())}Controller"
        file_name = f"{convert_to_snake_case(base_name)}_controller"
        route_path = f"/{convert_to_hyphen(base_name.lower())}"
        # Create scheme only once if request and response schemas are the same
        if request_scheme == response_scheme and request_scheme is not None:
            CreateSchema.execute(request_scheme)
        else:
            # Create request scheme if exists
            if request_scheme is not None:
                CreateSchema.execute(request_scheme)

            # Create response scheme if exists
            if response_scheme is not None:
                CreateSchema.execute(response_scheme)

        controller_template = CreateController.get_template(class_name)
        
        controller_dir = "app/controllers"
        if not os.path.exists(controller_dir):
            os.makedirs(controller_dir, exist_ok=True)
            with open(os.path.join(controller_dir, "__init__.py"), "w") as f:
                f.write("")

        with open(f"{controller_dir}/{file_name}.py", "w") as f:
            f.write(controller_template)

        init_file_path = f"{controller_dir}/__init__.py"
        import_statement = f"from .{file_name} import {class_name}\n"
        update_init_file(file_path=init_file_path, statement=import_statement)

        # Update the api.py routes file
        api_file_path = "app/routes/api.py"
        if os.path.exists(api_file_path):
            with open(api_file_path, "r") as f:
                content = f.read()

            import_stmt = f"from app.controllers.{file_name} import {class_name}\n"
            if import_stmt not in content:
                lines = content.split('\n')
                last_import_idx = -1
                for i, line in enumerate(lines):
                    if line.startswith("from ") or line.startswith("import "):
                        last_import_idx = i
                
                if last_import_idx != -1:
                    lines.insert(last_import_idx + 1, import_stmt.strip())
                else:
                    lines.insert(0, import_stmt.strip())
                
                route_method = "POST" if request_scheme else "GET"
                route_stmt = f'\nrouter.add_api_route(\n    path="{route_path}", \n    endpoint={class_name}.index, \n    methods=["{route_method}"]\n)\n'
                
                content = '\n'.join(lines) + route_stmt
                with open(api_file_path, "w") as f:
                    f.write(content)

        # Create the model if exists
        if model is not None:
            CreateModel.execute(model)

        click.echo(f"{class_name} created successfully.")

    @staticmethod
    def get_template(class_name: str, request_scheme: str = None, response_scheme: str = None) -> str:
        imports = set()
        if request_scheme:
            imports.add(f"from app.schemas import {generate_class_name(request_scheme.capitalize())}")
        if response_scheme and response_scheme != request_scheme:
            imports.add(f"from app.schemas import {generate_class_name(response_scheme.capitalize())}")

        imports_str = "\n".join(sorted(imports))

        request_param = f"{convert_to_snake_case(request_scheme)}: {generate_class_name(request_scheme.capitalize())}, " if request_scheme else ""

        default_response_import = ""
        if not response_scheme:
            default_response_import = "from typing import Dict, Any"

        return f"""{default_response_import}
from fastapi import Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
{imports_str}

class {class_name}:
    @staticmethod
    async def index({request_param}response_handler: ResponseHandler = Depends(get_response_handler)):
        return response_handler.send_success_response(message="This is the index method of {class_name}")
"""

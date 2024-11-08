import click
from makefast.utils import update_init_file, generate_class_name, convert_to_snake_case, convert_to_hyphen
from .create_model import CreateModel
from .create_scheme import CreateScheme


class CreateRoute:
    @staticmethod
    def execute(name, model, request_scheme, response_scheme):
        # Create scheme only once if request and response schemes are the same
        if request_scheme == response_scheme and request_scheme is not None:
            CreateScheme.execute(request_scheme)
        else:
            # Create request scheme if exists
            if request_scheme is not None:
                CreateScheme.execute(request_scheme)

            # Create response scheme if exists
            if response_scheme is not None:
                CreateScheme.execute(response_scheme)

        route_template = CreateRoute.get_template(name, request_scheme, response_scheme)
        with open(f"app/routes/{convert_to_snake_case(name.lower())}.py", "w") as f:
            f.write(route_template)

        init_file_path = "app/routes/__init__.py"
        import_statement = f"from .{convert_to_snake_case(name.lower())} import {generate_class_name(name.capitalize())}Route\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        # Create the model if exists
        if model is not None:
            CreateModel.execute(model)

        click.echo(f"{generate_class_name(name.capitalize())} route created successfully.")

    @staticmethod
    def get_template(name: str, request_scheme: str, response_scheme: str) -> str:
        # Handle imports more efficiently when schemes are the same
        imports = set() # Using a set to avoid duplicate imports
        if request_scheme:
            imports.add(f"from app.schemes import {generate_class_name(request_scheme.capitalize())}")
        if response_scheme and response_scheme != request_scheme:
            imports.add(f"from app.schemes import {generate_class_name(response_scheme.capitalize())}")

        imports_str = "\n".join(sorted(imports))  # Sort imports for consistency

        request_param = f"{convert_to_snake_case(request_scheme.lower())}: {generate_class_name(request_scheme.capitalize())}, " if request_scheme else ""

        route_decorator = "@router.get"
        if request_scheme:
            route_decorator = "@router.post"

        default_response_import = ""
        if not response_scheme:
            default_response_import = "from typing import Dict, Any"

        return f"""{default_response_import}
from fastapi import APIRouter, Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
{imports_str}

router = APIRouter()


class {generate_class_name(name.capitalize())}Route:
    @staticmethod
    {route_decorator}("/{convert_to_hyphen (name.lower())}", response_model={generate_class_name(response_scheme.capitalize()) if response_scheme else 'Dict[str, Any]'})
    async def index({request_param}response_handler: ResponseHandler = Depends(get_response_handler)):
        return response_handler.send_success_response(message="This is the index method of {generate_class_name(name.capitalize())}Route")
"""

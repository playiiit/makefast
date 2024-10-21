import click
from makefast.utils import update_init_file
from .create_model import CreateModel
from .create_scheme import CreateScheme


class CreateRoute:
    @staticmethod
    def execute(name, model, request_scheme, response_scheme):
        # Create request scheme if exists
        if request_scheme is None:
            request_scheme = name
        CreateScheme.execute(request_scheme)

        # Create response scheme if exists
        if response_scheme is not None:
            CreateScheme.execute(response_scheme)
        else:
            request_scheme = name

        route_template = CreateRoute.get_template(name, request_scheme, response_scheme)
        with open(f"app/routes/{name.lower()}.py", "w") as f:
            f.write(route_template)

        init_file_path = "app/routes/__init__.py"
        import_statement = f"from .{name.lower()} import {name.capitalize()}Route\n"

        update_init_file(file_path=init_file_path, statement=import_statement)

        # Create the model if exists
        if model is not None:
            CreateModel.execute(model)

        click.echo(f"{name.capitalize()} route created successfully.")

    @staticmethod
    def get_template(name: str, request_scheme: str, response_scheme: str) -> str:
        imports = []
        if request_scheme:
            imports.append(f"from app.schemes import {request_scheme.capitalize()}")
        if response_scheme:
            imports.append(f"from app.schemes import {response_scheme.capitalize()}")

        imports_str = "\n".join(imports)

        return f"""from fastapi import APIRouter, Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
{imports_str}

router = APIRouter()


class {name.capitalize()}Route:
    @staticmethod
    @router.get("/{name.lower()}", response_model={response_scheme.capitalize() if response_scheme else 'Dict[str, Any]'})
    async def index(
        {f'data: {request_scheme.capitalize()},' if request_scheme else ''}
        response_handler: ResponseHandler = Depends(get_response_handler)
    ):
        return response_handler.send_success_response(message="This is the index method of {name.capitalize()}Route")
"""

import click
from makefast.utils import update_init_file
from .create_model import CreateModel


class CreateRoute:
    @staticmethod
    def execute(name, model):
        route_template = CreateRoute.get_template(name)
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
    def get_template(name) -> str:
        return f"""from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.dependencies.response_handler import ResponseHandler, get_response_handler
    
router = APIRouter()
    
    
class {name.capitalize()}Route:
    @staticmethod
    @router.get("/{name.lower()}", response_model=Dict[str, Any])
    def index(response_handler: ResponseHandler = Depends(get_response_handler)):
        return response_handler.send_success_response(message="This is the index method of {name.capitalize()}Route")
"""

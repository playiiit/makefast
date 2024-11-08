import os
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from makefast.database import MySQLDatabaseInit

app = FastAPI()

MySQLDatabaseInit.init(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[""],  # Origins if needed
    allow_credentials=True,  # Allow cookies if needed
    allow_methods=["*"],  # Adjust as needed
    allow_headers=["*"],  # Adjust as needed
)


def register_routes():
    """
    Dynamically register API routes from routes modules.

    This function scans the 'app/routes' directory for Python files.
    It imports each module and, if the module
    has a 'router' attribute, includes that router in the main FastAPI app
    with the '/api' prefix.

    The function assumes:
    - All controller files are in the 'app/routes' directory
    - Controller files end with '_route.py'
    - routes define their routes using a 'router' object

    Side effects:
    - Modifies the global 'app' object by including routers
    """
    routes_dir = "makefast/app/routes"
    for filename in os.listdir(routes_dir):
        if filename.endswith(".py"):
            module_name = f"app.routes.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, 'router'):
                app.include_router(module.router, prefix="/api")


register_routes()

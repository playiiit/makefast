from pathlib import Path
import shutil
import pkg_resources
import os


class ProjectInit:
    @classmethod
    def execute(cls):
        """
        Initialize a new project by copying the entire app folder structure
        and creating necessary files.
        """
        # Get the current working directory (where user runs the command)
        destination = Path.cwd()

        # Get the package's app directory path
        try:
            app_template_dir = pkg_resources.resource_filename('makefast', 'app')
        except Exception as e:
            raise Exception(f"Could not find app template directory: {e}")

        if not os.path.exists(app_template_dir):
            raise Exception("App template directory not found in package")

        print("Initializing new project...")

        # Create the app directory structure
        try:
            target_app_dir = destination / 'app'

            if target_app_dir.exists():
                print("Warning: 'app' directory already exists!")
                response = input("Do you want to overwrite? (y/N): ").lower()
                if response != 'y':
                    print("Initialization cancelled.")
                    return
                shutil.rmtree(target_app_dir)

            # Copy the entire app directory structure
            shutil.copytree(app_template_dir, target_app_dir)
            print("\nProject structure created successfully!")

            # Create main.py and requirements.txt
            cls.create_main_file(destination)
            cls.create_requirements_file(destination)
            cls.create_env_file(destination)

            # Create .env file
            env_file = destination / '.env'
            env_file.touch()
            print("Created .env file")

            # Print the created structure
            print("\nCreated project structure:")
            for root, dirs, files in os.walk(target_app_dir):
                level = root.replace(str(destination), '').count(os.sep)
                indent = '  ' * (level + 1)
                if os.path.basename(root) != 'app':
                    print(f"{indent} {os.path.basename(root)}/")
                subindent = '  ' * (level + 2)
                for f in files:
                    print(f"{subindent} {f}")

        except Exception as e:
            print(f"Error during initialization: {e}")

    @classmethod
    def create_env_file(cls, destination):
        """
        Create the .env file with database configuration settings
        """
        env_content = '''DB_CONNECTION=mysql
DB_HOST=localhost
DB_PORT=3306
DB_DATABASE=
DB_USERNAME=
DB_PASSWORD=
DB_CLUSTER=
'''
        env_file = destination / '.env'
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("Created .env file with database configuration")

    @classmethod
    def create_main_file(cls, destination):
        """
        Create the main.py file with the FastAPI application setup
        """
        main_content = '''import os
import importlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
    """
    routes_dir = "app/routes"
    for filename in os.listdir(routes_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"app.routes.{filename[:-3]}"
            module = importlib.import_module(module_name)
            if hasattr(module, "router"):
                app.include_router(module.router, prefix="/api")

register_routes()
'''

        main_file = destination / 'main.py'
        with open(main_file, 'w') as f:
            f.write(main_content)
        print("Created main.py")

    @classmethod
    def create_requirements_file(cls, destination):
        """
        Create a requirements.txt file with necessary dependencies
        """
        requirements = """fastapi
uvicorn[standard]>=0.32.0
typer
motor
pytest
pymongo
pydantic
python-dotenv
mysql-connector-python
starlette
makefast
"""
        req_file = destination / 'requirements.txt'
        with open(req_file, 'w') as f:
            f.write(requirements)
        print("Created requirements.txt")

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='makefast',
    version='2.1.5',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'assets': ['app/**/*'],
    },
    install_requires=[
        'typer~=0.12.5',
        'setuptools~=73.0.1',
        'click~=8.1.7',
        'motor~=3.6.0',
        'pytest~=8.3.3',
        'pymongo~=4.9.2',
        'pydantic~=2.8.2',
        'python-dotenv~=1.0.1',
        'mysql-connector-python~=9.0.0',
        'starlette~=0.38.2',
    ],
    entry_points={
        'console_scripts': [
            'makefast=makefast.cli:cli',
        ],
    },
    long_description=long_description,
    description="FastAPI CLI Library",
    long_description_content_type="text/markdown"
)

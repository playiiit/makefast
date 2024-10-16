from setuptools import setup, find_packages

setup(
    name='makefast',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'fastapi',
        'uvicorn',
        'sqlalchemy',
    ],
    entry_points='''
        [console_scripts]
        makefast=makefast.cli:cli
    ''',
)

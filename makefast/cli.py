import click
from makefast.command import CreateRoute, CreateModel, CreateMigration, CreateScheme, CreateEnum


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.option('--model', '-m')
@click.option('--request_scheme', '-rqs')
@click.option('--response_scheme', '-rss')
def create_route(name, model, request_scheme, response_scheme):
    CreateRoute.execute(name, model, request_scheme, response_scheme)


@cli.command()
@click.argument('name')
@click.option('--table', '-t')
@click.option('--collection', '-c')
def create_model(name, table, collection):
    CreateModel.execute(name, table, collection)


@cli.command()
@click.argument('name')
def create_migration(name):
    CreateMigration.execute(name)


@cli.command()
@click.argument('name')
def create_scheme(name):
    CreateScheme.execute(name)


@cli.command()
@click.argument('name')
@click.option('--type', '-t')
def create_enum(name, type):
    CreateEnum.execute(name, type)

import click
import asyncio
from click import Context
from makefast.command import CreateRoute, CreateModel, CreateMigration, CreateSchema, CreateEnum, ProjectInit, ExecuteMigrations

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
def create_schema(name):
    CreateSchema.execute(name)


@cli.command()
@click.argument('name')
@click.option('--type', '-t')
def create_enum(name, type):
    CreateEnum.execute(name, type)


@cli.command()
@click.pass_context
def migrate(ctx: Context):
    migration = ExecuteMigrations()
    asyncio.run(migration.run_migrations())


@cli.command()
def init():
    ProjectInit.execute()

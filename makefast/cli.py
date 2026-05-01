import click
import asyncio
from click import Context
from makefast.command import (
    CreateRoute,
    CreateModel,
    CreateMigration,
    CreateSchema,
    CreateEnum,
    ProjectInit,
    ExecuteMigrations,
    CreateRequest,
    CreateResource,
)


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


# ── New Laravel-style commands ─────────────────────────────────────────────

@cli.command('create_request')
@click.argument('name')
def create_request(name):
    """Scaffold a new FormRequest validation class.

    \b
    Example:
        makefast create_request StoreUserRequest
    """
    CreateRequest.execute(name)


@cli.command('create_resource')
@click.argument('name')
@click.option(
    '--collection', '-c',
    is_flag=True,
    default=False,
    help='Also generate a ResourceCollection for this resource.',
)
def create_resource(name, collection):
    """Scaffold a new API Resource (and optionally a ResourceCollection).

    \b
    Examples:
        makefast create_resource User
        makefast create_resource User --collection
    """
    CreateResource.execute(name, collection=collection)

import click
from makefast.command import CreateRoute, CreateModel


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name')
@click.option('--model', '-m')
def create_route(name, model):
    CreateRoute.execute(name, model)


@cli.command()
@click.argument('name')
@click.option('--table', '-t')
@click.option('--collection', '-c')
def create_model(name, table, collection):
    CreateModel.execute(name, table, collection)

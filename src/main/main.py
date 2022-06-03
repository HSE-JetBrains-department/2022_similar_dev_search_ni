import click
import os

CLI_START_COLOR = 'red'


@click.command()
@click.option('-url', '-u', default=None, type=click.Path(), help='The URL of observed git repository.')
@click.option('-output-path', '-o', default='output', type=click.Path(), help='The path to file to save changes info.')
def cli(url: str, output_path: str) -> None:
    """
    CLI starter.
    """

    click.echo(f'Working with the {click.style(url, fg=CLI_START_COLOR)} repository.'
               f' Output will be saved into {click.style(f"{output_path}.json", fg=CLI_START_COLOR)} file.')
    pass


if __name__ == '__main__':
    cli()

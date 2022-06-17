import os

import click

from repo_processing.extractor.extract import process_repo, parse_repos_list, \
    save_file
from repo_processing.lang_parser.enry_parser import process_list
from repo_processing.code_parser.tree_sitter_parser import apply_parsing
from repo_processing.helper_funcs import reformat_commits_info
from repo_processing.stargazers.github_api import process_stargazers

CLI_COLOR = "red"
OUT_JSONS = "outjsons"


@click.group()
def cli() -> None:
    """
    CLI starter.
    """
    pass


@cli.command()
@click.option("-output-path", "-o", default="output", type=click.Path(),
              help="The path to file to save changes info.")
def parse_repos(output_path: str) -> None:
    """
    Function starts pipeline of parsing list of repositories.
    The result saved in file by a give output_path.
    :param output_path: Path to save parsed result.
    """

    if not os.path.exists(OUT_JSONS):
        os.makedirs(OUT_JSONS)

    click.echo(
        f"Output will be saved into "
        f"{click.style(f'{output_path}.json', fg=CLI_COLOR)} file.")
    click.echo(
        f"Separate output of every repo will be saved into"
        f" {click.style(f'{OUT_JSONS}/%reponame%.json', fg=CLI_COLOR)} "
        f"file.")
    click.echo("Start parsing.")
    list_repos = parse_repos_list()
    for el in list_repos:
        click.echo(
            f"\t{click.style('Parse {0}.'.format(el['url']), fg=CLI_COLOR)}\n")
        mapped_repos_list = process_repo(el["url"])  # dulwich
        mapped_repos_list = list({v["commit_id"]: v for v in
                                  mapped_repos_list}.values())  # unique by
        # commit_id
        mapped_repos_list = process_list(mapped_repos_list)  # enry
        mapped_repos_list = apply_parsing(mapped_repos_list)  # tree-sitter

        dict_by_author = reformat_commits_info(mapped_repos_list)

        # Saving to file named as current repo.
        path = el["url"]
        output_name = path[path.rfind("/") + 1:]
        save_file(mapped_repos_list, f"{OUT_JSONS}/{output_name}.json")
        # Saving to global file.
        save_file(mapped_repos_list, f"{output_path}.json")
        click.echo(
            f"\t{click.style('End {0}.'.format(el['url']), fg=CLI_COLOR)}\n")

    click.echo("Parsing completed. Saving to file...")

    click.echo(
        f"Parsing result saved into"
        f" {click.style(f'{output_path}.json', fg=CLI_COLOR)} file.")


@cli.command()
@click.option("-url", "-u", required=True, type=str,
              help="The URL of observed git repository.")
@click.option("-apikey", "-k", required=True, type=str,
              help="The API key for GitHub to deal with GitHub API.")
@click.option("-output-path", "-o", default="output_stars", type=click.Path(),
              help="The path to file to save an observed info.")
def stargazers(url: str, apikey: str, output_path: str) -> None:
    click.echo(
        f"Output will be saved into"
        f" {click.style(f'{output_path}.json', fg=CLI_COLOR)} file.")

    splitted = url.lower().replace("https://", "").split("/")
    if "github.com" in splitted and len(splitted) != 3:  # github.com/user/repo
        click.echo(
            "Wrong url format. Should be github.com/user/repo or user/repo. "
            "Try again.")
        return
    elif "github.com" in splitted and len(splitted) == 3:
        counter = process_stargazers(github_token=apikey,
                                     current_repo_name=f"{splitted[1]}/"
                                                       f"{splitted[2]}")
        print(counter)
        save_file(counter, f"{output_path}.json")

    if "github.com" not in splitted and len(splitted) != 2:  # user/repo
        click.echo(
            "Wrong url format. Should be github.com/user/repo or user/repo. "
            "Try again.")
        return
    elif "github.com" not in splitted and len(splitted) == 2:
        counter = process_stargazers(github_token=apikey,
                                     current_repo_name=f"{splitted[0]}/"
                                                       f"{splitted[1]}")
        print(counter)
        save_file(counter, f"{output_path}.json")


if __name__ == '__main__':
    cli()

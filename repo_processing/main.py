import os

import click

from code_parser.tree_sitter_parser import collect_names_imports
from extractor.extract import parse_repos_list, process_repo, save_file
from helper_funcs import reformat_commits_info
from lang_parser.enry_parser import classify_languages
from stargazers.github_api import process_stargazers

CLI_COLOR = "red"


@click.group()
def cli() -> None:
    """
    CLI starter.
    """
    pass


@cli.command()
@click.option("-output-path", "-o", default="resfolder", type=click.Path(),
              help="The path to directory to save changes info.")
@click.option("-result-output", "-r", default="output", type=click.Path(),
              help="The file name to directory to save info for all repos.")
@click.option("-url", "-u", required=True, type=str,
              help="The URL to list of repositories")
def parse_repos(output_path: str, result_output: str, url: str) -> None:
    """
    Function starts pipeline of parsing list of repositories.
    The result saved in file by a give output_path.
    :param output_path: Path to save parsed result.
    :param result_output: Name of file to save parsed result for all repos.
    :param url: The URL to list of repositories.
    """

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    click.echo(
        f"Output will be saved into "
        f"{click.style(f'{result_output}.json', fg=CLI_COLOR)} file.")
    click.echo(
        f"Separate output of every repo will be saved into"
        f" {click.style(f'{output_path}/%reponame%.json', fg=CLI_COLOR)} "
        f"file.")
    click.echo("Start parsing.")
    list_repos = parse_repos_list(url)
    for el in list_repos:
        click.echo(
            f"\t{click.style('Parse {0}.'.format(el['url']), fg=CLI_COLOR)}\n")
        mapped_repos_list = process_repo(el["url"])  # dulwich
        mapped_repos_list = list({v["commit_id"]: v for v in
                                  mapped_repos_list}.values())  # unique by
        # commit_id
        mapped_repos_list = classify_languages(mapped_repos_list)
        mapped_repos_list = collect_names_imports(mapped_repos_list)

        reformat_commits_info(mapped_repos_list)  # to simdevsearch

        # Saving to file named as current repo.
        path = el["url"].split("/")
        output_name = f"{path[3]}_{path[4]}"  # path[path.rfind("/") + 1:]
        save_file(mapped_repos_list, f"{output_path}/{output_name}.json")
        # Saving to global file.
        save_file(mapped_repos_list, f"{result_output}.json")
        click.echo(
            f"\t{click.style('End {0}.'.format(el['url']), fg=CLI_COLOR)}\n")

    click.echo("Parsing completed. Saving to file...")

    click.echo(
        f"Parsing result saved into"
        f" {click.style(f'{result_output}.json', fg=CLI_COLOR)} file.")


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

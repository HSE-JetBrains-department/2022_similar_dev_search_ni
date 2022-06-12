import click
import os

from extractor.extract import process_repo, parse_repos_list, save_file
from lang_parser.enry_parser import process_list
from code_parser.tree_sitter_parser import parse_file, setup_tree_sitter_parser
from stargazers.github_api import process_stargazers

CLI_START_COLOR = "red"


@click.group()
# @click.command()
# @click.option('-url', '-u', default=None, type=click.Path(), help="The URL of observed git repository.")
# @click.option('-output-path', '-o', default='output',type=click.Path(), help="The path to file to save changes info.")
def cli() -> None:  # url: str, output_path: str
    """
    CLI starter.
    """
    #
    # click.echo(f"Working with the {click.style(url, fg=CLI_START_COLOR)} repository."
    #            f" Output will be saved into {click.style(f'{output_path}.json', fg=CLI_START_COLOR)} file.")
    pass


@cli.command()
@click.option("-output-path", "-o", default="output", type=click.Path(), help="The path to file to save changes info.")
def parse_repos(output_path: str) -> None:
    """
    Function starts pipeline of parsing list of repositories. The result saved in file by a give output_path.
    :param output_path: Path to save parsed result.
    """

    whole_result_file = "result_file"
    click.echo(f"Output will be saved into {click.style(f'{output_path}.json', fg=CLI_START_COLOR)} file.")
    click.echo("Start parsing.")
    list_repos = parse_repos_list()
    for el in list_repos:
        click.echo(f"\t{click.style('Parse {0}.'.format(el['url']), fg=CLI_START_COLOR)}\n")
        mapped_repos_list = process_repo(el["url"])  # dulwich
        mapped_repos_list = list({v["commit_id"]: v for v in mapped_repos_list}.values())  # unique by commit_id
        mapped_repos_list = process_list(mapped_repos_list)  # enry
        for x in mapped_repos_list:  # tree-sitter
            try:
                if ("Python" in x["lang"]) or "JavaScript" in x["lang"] or "Java" in x["lang"]:
                    setup_tree_sitter_parser()
                    parsed_d = parse_file(x["lang"], x["path"])
                    x["tree_parse"] = parsed_d
            except FileNotFoundError as e:  # deleted files.
                pass
        path = el["url"]
        output_name = path[path.rfind("/") + 1:]
        save_file(mapped_repos_list, f"{output_name }.json")
        save_file(mapped_repos_list, f"{whole_result_file}.json")
        click.echo(f"\t{click.style('End {0}.'.format(el['url']), fg=CLI_START_COLOR)}\n")

    click.echo("Parsing completed. Saving to file...")

    click.echo(f"Parsing result saved into {click.style(f'{output_path}.json', fg=CLI_START_COLOR)} file. ")


@cli.command()
@click.option("-url", "-u", required=True, type=str, help="The URL of observed git repository.")
@click.option("-apikey", "-k", required=True, type=str, help="The API key for GitHub to deal with GitHub API.")
def stargazers(url: str, apikey: str):
    splitted = url.lower().replace("https://", "").split("/")
    if "github.com" in splitted and len(splitted) != 3:  # github.com/user/repo
        click.echo("Wrong url format. Should be github.com/user/repo or user/repo. Try again.")
        return
    elif "github.com" in splitted and len(splitted) == 3:
        counter = process_stargazers(github_token=apikey, current_repo_name=f"{splitted[1]}/{splitted[2]}")
        print(counter)
        save_file(counter, f"oct.json")
    if "github.com" not in splitted and len(splitted) != 2:
        click.echo("Wrong url format. Should be github.com/user/repo or user/repo. Try again.")
        return
    elif "github.com" not in splitted and len(splitted) == 2:
        counter = process_stargazers(github_token=apikey, current_repo_name=f"{splitted[0]}/{splitted[1]}")
        print(counter)
        save_file(counter, f"oct.json")


if __name__ == '__main__':
    cli()

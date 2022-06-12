import os
import shutil
from typing import List, Dict

from dulwich.errors import NotGitRepository
from dulwich.repo import Repo

import pytest

from repo_processing.extractor import repo_clones_dir
from repo_processing.extractor.extract import parse_repos_list, save_file, clone_or_instantiate


@pytest.mark.parametrize("expected_len", [150])
def test_parse_repos_list_len(expected_len: int):
    """
    Test checks parse_repos_list returns not empty list with data.
    """

    assert len(parse_repos_list()) == expected_len


@pytest.mark.parametrize("expected_params", [(["url", "invitation", "stars", "language"])])
def test_parse_repos_list_params(expected_params: List[str]):
    """
    Test checks parse_repos_list has right list params.
    """
    assert list(parse_repos_list()[-1].keys()) == expected_params


@pytest.mark.parametrize("json, json_string", [([{"imports": 5}, {3: "tmp"}], '[{"imports": 5}, {"3": "tmp"}]')])
def test_save_file(json: List[Dict], json_string: str) -> None:
    """
    Test checks save_file function saves file with a provided List[Dict] object.
    """
    save_file(json, "testfile.json")
    result = ""
    with open("testfile.json", "r") as fp:
        result = fp.read()

    os.remove("testfile.json")
    assert result == json_string


@pytest.mark.parametrize("repo_url", ["https://github.com/EdwardNee/PositLib"])
def test_clone_or_instantiate(repo_url: str) -> None:
    """
    Test checks clone_or_instantiate works correctly that repo is really cloned.
    """
    clone_or_instantiate(repo_url)
    is_thrown = False
    repo_name = repo_url[repo_url.rfind("/") + 1:]

    repo = None
    try:
        repo = Repo(f"{repo_clones_dir}/{repo_name}")
    except NotGitRepository as e:
        is_thrown = True
    shutil.rmtree(f"{repo_clones_dir}/{repo_name}")
    #os.removedirs(f"{repo_clones_dir}/{repo_name}")
    assert (not is_thrown) and (repo is not None)

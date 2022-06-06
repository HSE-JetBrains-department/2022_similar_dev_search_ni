import json
import os
import requests

from difflib import unified_diff
from dulwich.diff_tree import TreeChange
from dulwich.objects import Blob
from dulwich.porcelain import clone
from dulwich.repo import Repo
from typing import Dict, List, Tuple

from repo_processing import repo_clones_dir


def count_diff(blob_old: Blob, blob_new: Blob) -> Tuple[int, int]:
    """
    Function compares two blobs and returns the Tuple of changes:
    added and removed lines count.

    :param blob_old: Old version blob
    :param blob_new: New version blob

    :return: Returns tuple of ints representing how much lines were added and deleted respectively.
    """
    diffs = list(unified_diff(blob_old.data.decode().splitlines(), blob_new.data.decode().splitlines()))
    add, delete = 0, 0
    for diff in diffs:
        if diff[0] == '+':
            add += 1
        elif diff[0] == '-':
            delete += 1
    return add, delete


def process_change_diff(change: TreeChange, commit_dict: Dict, repo: Repo, path: str) -> Dict:
    """
    Function processes given change and fills the dictionary.

    :param repo: Current repo instance
    :param change: change to process.
    :param commit_dict: Dictionary with information about commit.
    :param path: Root path to repository: github.com/user/reponame/

    :return: Returns filled dictionary for one repository change.
    """
    # Added, deleted, modified
    try:
        if change.old.sha is None:
            commit_dict['add'] = len(repo[change.new.sha].data.decode())
            commit_dict['blob_id'] = change.new.sha.decode()
            commit_dict['path'] = path + "/" + change.new.path.decode()
        elif change.new.sha is None:
            commit_dict['delete'] = len(repo[change.old.sha].data.decode())
            commit_dict['blob_id'] = change.old.sha.decode()
            commit_dict['path'] = path + "/" + change.old.path.decode()
        else:
            commit_dict['add'], commit_dict['delete'] = count_diff(repo[change.old.sha], repo[change.new.sha])
            commit_dict['blob_id'] = change.new.sha.decode()
            commit_dict['path'] = path + "/" + change.new.path.decode()
    except (UnicodeDecodeError, KeyError) as e:
        pass
    return commit_dict


def process_walker(repo: Repo) -> List[Dict]:
    """
    Function processes WalkEntries mapping the changes info into list of dictionaries of:
    List of: {author, commit_id, path, blob_id, change: add, delete}

    :param repo: Repository instance.

    :return: Returns list of mapped commits info.
    """
    walker = repo.get_walker()
    multiple_commits = list()
    for entry in walker:
        commit_dict = {'author': entry.commit.author.decode(), 'commit_id': entry.commit.id.decode()}
        for change in entry.changes():
            if type(change) is not TreeChange:  # modify
                for ch in change:
                    commit_dict = process_change_diff(ch, commit_dict, repo, repo.path)
                    multiple_commits.append(commit_dict)
                continue
            commit_dict = process_change_diff(change, commit_dict, repo, repo.path)
            multiple_commits.append(commit_dict)
    return multiple_commits


def clone_or_instantiate(path: str) -> Repo:
    """
    Function cloned repo, if it is not existed, otherwise instantiate the existing one.
    :param: The path in local directory or url to GitHub repository.

    :return: Repository instance.
    """
    repo_name = path[path.rfind('/') + 1:]
    pth = f"{repo_clones_dir}/{repo_name}"
    return Repo(pth) if os.path.exists(pth) else clone(pth)


def process_repo(path: str) -> List[Dict]:
    """
    Function starts to process repository by a given path.
    :param path: The path in local directory or url to GitHub repository.

    :return: Returns list of mapped commits info.
    """
    repo = clone_or_instantiate(path)
    return process_walker(repo)


def parse_repos_list(url_file: str = "https://gist.githubusercontent.com/EgorBu/823d01e7f12cb18495891fb752398037/raw"
                                     "/8b793d61498b76759a552f8f259c61661dc427ff/repos.txt") -> List[Dict]:
    """
    Function downloads .txt file that contains info about processing repositories.
    :param url_file: URL to the file.

    :return: Returns list of dictionaries with values: url, invitation, stars, language.
    """
    r = requests.get(url_file)
    lines = r.text.replace('\t', '').split('\n')[1:]
    list_repos = list()
    for i in range(0, len(lines), 4):
        d = {
            "url": "https://" + lines[i] if "https://" not in lines[i] else lines[i],
            "invitation": lines[i + 1],
            "stars": lines[i + 2],
            "language": lines[i + 3]
        }
        list_repos.append(d)

    return list_repos


def save_file(multiple_commits: List[Dict], output_path: str = '') -> bool:
    """
    The function to save the data into file in output_path.
    Returns True if the info was successfully appended to file, False if the error occurred.

    :param multiple_commits: The list of dicts containing each change info.
    :param output_path: The path to file to save info.

    :return: Returns True if the info was successfully appended to file, False if the error occurred.
    """
    json_str = json.dumps(multiple_commits)
    try:
        with open(output_path, 'a') as output_file:
            output_file.write(json_str)
    except IOError as e:
        print(f'Failed to write to file {output_path}. {e}')
        return False

    return True

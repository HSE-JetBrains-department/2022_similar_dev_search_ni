from typing import List, Dict, Tuple
from dulwich.diff_tree import TreeChange
from dulwich.objects import Blob

import json
import os

from dulwich.repo import Repo
from dulwich.porcelain import clone

# from dulwich.patch import unified_diff
from difflib import unified_diff

TEMPLATE_PATH = "PositLib.git/"


def count_diff(blob_old: Blob, blob_new: Blob) -> Tuple[int, int]:
    """
    Function compares two blobs and returns the Tuple of changes:
    added and removed lines count.

    :param blob_old: Old version blob
    :param blob_new: New version blob
    """
    diffs = list(unified_diff(blob_old.data.decode().splitlines(), blob_new.data.decode().splitlines()))
    add, delete = 0, 0
    for diff in diffs:
        if diff[0] == '+':
            add += 1
        elif diff[0] == '-':
            delete += 1
    return add, delete


def process_change_diff(change: TreeChange, commit_dict: Dict, repo: Repo) -> Dict:
    """
    Function processes given change and fills the dictionary.

    :param repo: Current repo instance
    :param change: change to process.
    :param commit_dict: Dictionary with information about commit.
    """
    # Added, deleted, modified
    try:
        if change.old.sha is None:
            commit_dict['add'] = len(repo[change.new.sha].data.decode())
            commit_dict['blob_id'] = change.new.sha.decode()
            commit_dict['path'] = TEMPLATE_PATH + change.new.path.decode()
        elif change.new.sha is None:
            commit_dict['delete'] = len(repo[change.old.sha].data.decode())
            commit_dict['blob_id'] = change.old.sha.decode()
            commit_dict['path'] = TEMPLATE_PATH + change.old.path.decode()
        else:
            commit_dict['add'], commit_dict['delete'] = count_diff(repo[change.old.sha], repo[change.new.sha])
            commit_dict['blob_id'] = change.new.sha.decode()
            commit_dict['path'] = TEMPLATE_PATH + change.new.path.decode()
    except UnicodeDecodeError as e:
        pass
    return commit_dict


def process_walker(repo: Repo) -> List[Dict]:
    """
    Function processes WalkEntries mapping the changes info into list of dictionaries of:
    List of: {author, commit_id, path, blob_id, change: add, delete}

    :return: Returns list of mapped commits info.
    """
    walker = repo.get_walker()
    multiple_commits = list()
    for entry in walker:
        commit_dict = {'author': entry.commit.author.decode(), 'commit_id': entry.commit.id.decode()}
        for change in entry.changes():
            commit_dict = process_change_diff(change, commit_dict, repo)
            multiple_commits.append(commit_dict)
    return multiple_commits


def clone_repo(url: str):
    return clone(url)


def process_repo(path: str) -> List[Dict]:
    """
    Function starts to process repository by a given path.
    :param path: The path in local directory or url to GitHub repository. If there is not cloned repo,
    the method will clone and process with it, otherwise use the existing one.

    :return: Returns list of mapped commits info.
    """
    repo = Repo(path) if os.path.exists(path) else clone_repo(path)
    return process_walker(repo)


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

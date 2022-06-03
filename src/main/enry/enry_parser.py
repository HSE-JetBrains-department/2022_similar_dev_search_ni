from enry import get_languages, get_language_by_extension
from typing import List, Dict
import os


def get_content(path: str) -> str:
    """
    Method reads the file by the given path.

    :param path: Path to blob.
    """

    with open(path, 'r') as fp:
        return fp.read()


def get_languages_method(path: str) -> List[str]:
    """
    Reads the content from the path and analyzes the file by its extension and
    content returning the list of languages.

    :param path: Path to blob.
    """

    if os.path.isfile(path):
        content = get_content(path)
        result = get_languages(path, content.encode())
    else:
        result = [get_language_by_extension(path).language]

    return result


def process_list(list_commits: List[Dict]) -> List[Dict]:
    """
    Sets to each element in list_commits list of languages.

    :param list_commits: List of mapped commits info.
    """

    for change in list_commits:
        change['lang'] = get_languages_method(change['path'])
    return list_commits

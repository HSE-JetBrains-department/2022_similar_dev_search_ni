import os
from typing import List, Dict

from enry import get_languages, get_language_by_extension


def get_content(path: str) -> str:
    """
    Method reads the file by the given path.

    :param path: Path to blob.

    :return: Returns read lines.
    """

    with open(path, 'r') as fp:
        return fp.read()


def get_languages_method(path: str) -> List[str]:
    """
    Reads the content from the path and analyzes the file by its extension and
    content returning the list of languages.

    :param path: Path to blob.

    :return: Returns list of languages for given file.
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

    :return:  List of dictionaries that adds to given dicts a key with languages.
    """

    for change in list_commits:
        change["lang"] = get_languages_method(change["path"]) if "path" in change.keys() else []
    return list_commits

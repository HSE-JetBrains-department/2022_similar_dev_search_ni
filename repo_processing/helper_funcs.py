from typing import Dict, List


def reformat_commits_info(mapped_repos_list: List[Dict]) -> Dict:
    """
    Reformats given mapped_repos_list into dictionary with the key 'author'.

    :param mapped_repos_list: List of mapped commits info.

    "return: Reformatted dictionary.
    """
    formatted_dict = dict()
    for el in mapped_repos_list:
        if el["author"] not in formatted_dict:
            formatted_dict[el["author"]] = [el]
        else:
            formatted_dict[el["author"]].append(el)

    return formatted_dict

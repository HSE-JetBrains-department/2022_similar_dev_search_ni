from typing import Dict

import calendar
from collections import Counter
import time

from github import Github, GithubException, RateLimitExceededException

global_counter = Counter()


def rate_limit_sleep(github_instance: Github) -> None:
    """
    Function starts sleeping when the RateLimitExceededException occurred
    and search_rate_limit reached.

    :param github_instance: GitHub
    """

    search_rate_limit = github_instance.get_rate_limit().search
    print("search remaining: {}".format(search_rate_limit.remaining))
    reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
    # time.sleep(sleep_time)
    time.sleep(max(0, reset_timestamp - calendar.timegm(time.gmtime())))


def process_stargazers(github_token: str, current_repo_name: str,
                       stars_limit: int = 100,
                       per_page: int = 100,
                       top_common: int = 100) -> Dict:
    """
    Function processes all the stargazers of the current_repo_name repository.
    Memorizes starred repos for each stargazer to Counter.

    :param github_token: GitHub API token.
    :param per_page: per_page param.
    :param current_repo_name: repository name in GitHub.
    :param stars_limit: filtering parameter to process stargazers that starred
    :param top_common: The number of most popular repos.
    less than stars_limit repos.

    :return: Counter (Dict) of names of repositories.
    """

    github_instance = Github(login_or_token=github_token, per_page=per_page)
    global global_counter
    global_counter = Counter()

    git_repo = github_instance.get_repo(current_repo_name)
    global_counter[current_repo_name] = git_repo.stargazers_count

    stargazers = git_repo.get_stargazers()
    for stargazer in stargazers:
        starred_cntr = 1
        try:
            starred = stargazer.get_starred()
            for repo_starred in starred:  # GithubException
                if starred_cntr >= stars_limit:
                    break
                if repo_starred.full_name == current_repo_name:
                    continue
                global_counter[repo_starred.full_name] += 1
                starred_cntr += 1
        except RateLimitExceededException:
            rate_limit_sleep(github_instance)
        except GithubException:
            continue

    return dict(global_counter.most_common(top_common))

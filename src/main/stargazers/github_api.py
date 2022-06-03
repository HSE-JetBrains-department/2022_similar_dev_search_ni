from github import Github, RateLimitExceededException
import calendar
import time
from collections import Counter

global_counter = Counter()


def rate_limit_sleep(g: Github) -> None:
    """
    Function starts sleeping when the RateLimitExceededException occurred and search_rate_limit reached.

    :param g: GitHub
    """

    search_rate_limit = g.get_rate_limit().search
    print('search remaining: {}'.format(search_rate_limit.remaining))
    reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
    # add 10 seconds to be sure the rate limit has been reset
    sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
    time.sleep(sleep_time)


# 'vk-education/FancyWork'
def process_stargazers(github_token: str, current_repo_name: str, stars_limit: int = 30, per_page: int = 100) -> Counter:
    """
    Function processes all the stargazers of the current_repo_name repository.
    Memorizes starred repos for each stargazer to Counter.

    :param github_token: GitHub API token.
    :param per_page: per_page param.
    :param current_repo_name: repository name in GitHub.
    :param stars_limit: filtering parameter to process stargazers that starred less than stars_limit repos.
    """

    g = Github(login_or_token=github_token, per_page=per_page)
    users = list()

    git_repo = g.get_repo(current_repo_name)
    global_counter[current_repo_name] = git_repo.stargazers_count

    try:
        for stargazer in git_repo.get_stargazers():
            starred = stargazer.get_starred()
            if starred.totalCount <= stars_limit:  # limit stargazers by starred
                users.append(stargazer)
        for user in users:
            for user_reps in user.get_starred():
                if user_reps.full_name != current_repo_name:
                    global_counter[user_reps.full_name] += 1
    except RateLimitExceededException as e:
        rate_limit_sleep(g)

    return global_counter

import os

from repo_processing import repo_clones_dir


if not os.path.exists(repo_clones_dir):
    os.makedirs(repo_clones_dir)

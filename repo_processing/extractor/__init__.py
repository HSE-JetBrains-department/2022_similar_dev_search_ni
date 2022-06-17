import os


REPO_CLONES_DIR = "clonedrepos"

if not os.path.exists(REPO_CLONES_DIR):
    os.makedirs(REPO_CLONES_DIR)

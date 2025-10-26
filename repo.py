import contextlib
import tempfile
import os

import git

from settings import settings

@contextlib.contextmanager
def clone_repo(repo_owner: str, repo_name: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_auth_url = f'https://{settings.github_token}@github.com/{repo_owner}/{repo_name}.git'
        repo = git.Repo.clone_from(repo_auth_url, temp_dir)
        print(os.listdir(repo.working_tree_dir))
        yield repo

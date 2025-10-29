from typing import Protocol
from contextlib import contextmanager
import tempfile
import git
from app.domain.value_objects import GitDirectory

class GitClient(Protocol):
    def generate_url(self, owner: str, repo_name: str, token: str, **kwargs) -> str:
        ...

    @contextmanager
    def temporary_clone(self, owner: str, repo_name: str, token: str) -> GitDirectory:
        with tempfile.TemporaryDirectory() as temp_dir:
            url = self.generate_url(owner, repo_name, token)
            repo = git.Repo.clone_from(url, temp_dir)
            repo_dir = repo.working_tree_dir
            yield GitDirectory(path=repo_dir, repo_owner=owner, repo_name=repo_name)
from typing import Protocol
from contextlib import contextmanager
import tempfile
import git

class GitClient(Protocol):
    def generate_url(self, owner: str, repo_name: str, token: str, **kwargs) -> str:
        ...

    @contextmanager
    def temporary_clone(self, owner: str, repo_name: str, token: str) -> git.Repo:
        with tempfile.TemporaryDirectory() as temp_dir:
            url = self.generate_url(owner, repo_name, token)
            repo = git.Repo.clone_from(url, temp_dir)
            yield repo
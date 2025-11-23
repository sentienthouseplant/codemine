import tempfile
from contextlib import contextmanager
from typing import Protocol

import git
import structlog

from codemine.domain.value_objects import GitDirectory

logger = structlog.get_logger()


class GitClient(Protocol):
    def generate_url(self, owner: str, repo_name: str, *args, **kwargs) -> str: ...

    @contextmanager
    def temporary_clone(
        self, owner: str, repo_name: str, *args, **kwargs
    ) -> GitDirectory:
        with tempfile.TemporaryDirectory() as temp_dir:
            url = self.generate_url(owner, repo_name, *args, **kwargs)
            repo = git.Repo.clone_from(url, temp_dir)
            repo_dir = repo.working_tree_dir
            logger.bind(repo_dir=repo_dir, owner=owner, repo_name=repo_name).info(
                "Cloned repository"
            )
            yield GitDirectory(path=repo_dir, repo_owner=owner, repo_name=repo_name)

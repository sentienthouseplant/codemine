import pydantic
from contextlib import contextmanager
import git
import tempfile

class GitRepo(pydantic.BaseModel):
    owner: str
    repo_name: str

    @contextmanager
    def clone(self, url: str):
        with tempfile.TemporaryDirectory() as temp_dir:
            repo = git.Repo.clone_from(url, temp_dir)
            yield repo
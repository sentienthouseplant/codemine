from app.domain.ports.git_client import GitClient
from app.domain.model.git_repo import GitRepo

class GithubGitClient(GitClient):
    def generate_url(self, owner: str, repo_name: str, token: str, **kwargs) -> str:
        return f"https://{token}@github.com/{owner}/{repo_name}.git"

from app.domain.ports.git_client import GitClient
from app.infrastructure.settings import Settings

class GithubGitClient(GitClient):
    def generate_url(self, owner: str, repo_name: str, settings: Settings, **kwargs) -> str:
        return f"https://{settings.github_token}@github.com/{owner}/{repo_name}.git"

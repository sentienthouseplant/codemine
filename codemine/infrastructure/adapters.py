from codemine.domain.ports.embedding_client import EmbeddingClient
from codemine.domain.ports.git_client import GitClient
from codemine.domain.value_objects import EmbeddedRecord, GenericRecord


class GithubGitClient(GitClient):
    def __init__(self, token: str):
        self.token = token

    def generate_url(self, owner: str, repo_name: str, *args, **kwargs) -> str:
        return f"https://{self.token}@github.com/{owner}/{repo_name}.git"


class ConstantEmbeddingClient(EmbeddingClient):
    def embed_generic_record(
        self, record: GenericRecord, *args, **kwargs
    ) -> EmbeddedRecord:
        return EmbeddedRecord(
            id=record.id,
            unembedded_content=record.unembedded_content,
            embedded_content=[0.5] * 1024,
            metadata=record.metadata,
        )

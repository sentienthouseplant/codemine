from codemine.infrastructure.settings import Settings
from openai import OpenAI
from codemine.domain.ports.git_client import GitClient
from codemine.infrastructure.adapters import GithubGitClient
from codemine.domain.repositories.vector_store_repo import VectorIndexRepo
from codemine.infrastructure.pinecone_vector_store import PineconeVectorStore
from codemine.domain.services.code_chunking_service import CodeChunkingService
from codemine.domain.services.context_enrichment_service import ContextEnrichmentService
from codemine.application.use_cases.embed_git_repo import EmbedGitRepoUseCase

def get_settings() -> Settings:
    return Settings()

def get_openai_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
    )

def get_git_client() -> GitClient:
    settings = get_settings()
    return GithubGitClient(
        token=settings.github_token,
    )

def get_vector_store() -> VectorIndexRepo:
    settings = get_settings()
    return PineconeVectorStore(
        index_name="code-chunks",
        settings=settings,
    )

def get_code_chunking_service() -> CodeChunkingService:
    return CodeChunkingService()

def get_context_enrichment_service() -> ContextEnrichmentService:
    return ContextEnrichmentService()

def get_embed_git_repo_use_case() -> EmbedGitRepoUseCase:
    return EmbedGitRepoUseCase(
        git_client=get_git_client(),
        code_chunking_service=get_code_chunking_service(),
        context_enrichment_service=get_context_enrichment_service(),
        vector_store=get_vector_store(),
        openai_client=get_openai_client(),
    )
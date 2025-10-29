from app.infrastructure.adapters import GithubGitClient
from app.domain.services.code_chunking_service import CodeChunkingService
from app.infrastructure.settings import Settings
from openai import OpenAI
from app.domain.services.context_enrichment_service import ContextEnrichmentService


settings = Settings()

openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

github_client = GithubGitClient()

chunking_service = CodeChunkingService()

with github_client.temporary_clone("sentienthouseplant", "purplepipes", settings) as repo:
    for document in chunking_service.walk_directory(repo):
        chunked_document = chunking_service.chunk_document(document)
        context_enrichment_service = ContextEnrichmentService()
        enriched_document = context_enrichment_service.enrich_document(openai_client, chunked_document)
        print(enriched_document.model_dump_json(indent=2))
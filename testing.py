from app.infrastructure.adapters import GithubGitClient
from app.domain.services.code_chunking_service import CodeChunkingService
from app.infrastructure.settings import Settings
from openai import OpenAI
from app.domain.services.context_enrichment_service import ContextEnrichmentService
from app.infrastructure.pinecone_vector_store import PineconeVectorStore
from app.infrastructure.adapters import ConstantEmbeddingClient


settings = Settings()

openai_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

github_client = GithubGitClient()

chunking_service = CodeChunkingService()

enriched_documents = []
with github_client.temporary_clone("sentienthouseplant", "purplepipes", settings) as repo:
    for document in chunking_service.walk_directory(repo):
        chunked_document = chunking_service.chunk_document(document)
        context_enrichment_service = ContextEnrichmentService()
        enriched_document = context_enrichment_service.enrich_document(openai_client, chunked_document)
        enriched_documents.append(enriched_document)


pinecone_vector_store = PineconeVectorStore(index_name="code-chunks-test-2", settings=settings)
pinecone_vector_store.create_index_if_not_exists()


for enriched_document in enriched_documents:    
    pinecone_vector_store.embed_and_insert_records([chunk.generic_record for chunk in enriched_document.chunks])
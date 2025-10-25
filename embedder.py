from pinecone import Pinecone
from settings import settings

pc = Pinecone(api_key=settings.pinecone_api_key)

namespace = "codebase-embedding"

# Create a dense index with integrated embedding
index_name = "codebase-dense"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "code_with_context"}
        }
    )


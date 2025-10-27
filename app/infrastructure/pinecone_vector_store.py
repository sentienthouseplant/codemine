from app.domain.repositories.vector_store_repo import VectorStoreRepo
from app.domain.model.code_chunk import CodeChunk
from app.infrastructure.settings import settings
from pinecone import Pinecone

class PineconeVectorStore(VectorStoreRepo):
    def __init__(self, index_name: str):
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.index_name = index_name

    def add_chunks(self, chunks: list[CodeChunk]):
        pass

    def get_current_files_embedded(self, repo_owner: str, repo_name: str) -> list[str]:
        pass

    def remove_chunks_by_file_path(self, file_path: str, repo_owner: str, repo_name: str) -> bool:
        pass
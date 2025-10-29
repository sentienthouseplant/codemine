from abc import ABC, abstractmethod

from app.domain.model.code_chunk import CodeChunk

class VectorStoreRepo(ABC):
    @abstractmethod
    def add_chunks(self, chunks: list[CodeChunk]):
        pass

    @abstractmethod
    def get_current_files_embedded(self, repo_owner: str, repo_name: str) -> list[str]:
        pass

    @abstractmethod
    def remove_chunks_by_file_path(self, file_path: str, repo_owner: str, repo_name: str) -> bool:
        pass

    @abstractmethod
    def search_chunks(self, query: str) -> list[CodeChunk]:
        pass

    @abstractmethod
    def embed_and_add_chunks(self, chunks: list[CodeChunk]):
        pass

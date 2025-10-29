from abc import ABC, abstractmethod

from app.domain.model.code_chunk import CodeChunk
from app.domain.value_objects import EmbeddedRecord, GenericRecord
from app.infrastructure.settings import Settings

class VectorIndexRepo(ABC):

    def __init__(self, index_name: str, settings: Settings):
        self.index_name = index_name
        self.settings = settings

    @abstractmethod
    def create_index_if_not_exists(self):
        pass

    @property
    @abstractmethod
    def index(self) -> str:
        pass

    @abstractmethod
    def insert_vectors(self, records: list[EmbeddedRecord]):
        pass

    @abstractmethod
    def get_current_files_embedded(self, repo_owner: str, repo_name: str) -> list[str]:
        pass

    @abstractmethod
    def remove_vectors_by_file_path(self, file_path: str, repo_owner: str, repo_name: str) -> bool:
        pass

    @abstractmethod
    def search_vectors(self, query: str) -> list[EmbeddedRecord]:
        pass

    def embed_and_insert_records(self, records: list[GenericRecord]):
        raise NotImplementedError(f"This Vector Store : {self.__class__.__name__} does not implement the embed_and_add_chunks method. It may not be possible to embed content directly into the vector store.")

    def remove_outdated_vectors(self, repo_owner: str, repo_name: str, new_files: list[str]):
        for file_path in self.get_current_files_embedded(repo_owner, repo_name):
            if file_path not in new_files:
                self.remove_vectors_by_file_path(file_path, repo_owner, repo_name)

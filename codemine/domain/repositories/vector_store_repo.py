from abc import ABC, abstractmethod

from codemine.domain.model.code_chunk import CodeChunk
from codemine.domain.value_objects import EmbeddedRecord, GenericRecord
from codemine.infrastructure.settings import Settings

import structlog

logger = structlog.get_logger()

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
    def search_vectors(self, query: str) -> list[GenericRecord]:
        pass

    def embed_and_insert_records(self, records: list[GenericRecord]):
        raise NotImplementedError(f"This Vector Store : {self.__class__.__name__} does not implement the embed_and_add_chunks method. It may not be possible to embed content directly into the vector store.")

    def remove_outdated_vectors(self, repo_owner: str, repo_name: str, new_files: list[str]):
        outdated_vectors_count = 0
        for file_path in self.get_current_files_embedded(repo_owner, repo_name):
            if file_path not in new_files:
                logger.bind(file_path=file_path).info("Removing outdated vectors with file path")
                self.remove_vectors_by_file_path(file_path, repo_owner, repo_name)
                outdated_vectors_count += 1
        if outdated_vectors_count > 0:
            logger.bind(repo_owner=repo_owner, repo_name=repo_name, outdated_vectors_count=outdated_vectors_count).info("Removed outdated vectors")
        else:
            logger.bind(repo_owner=repo_owner, repo_name=repo_name, outdated_vectors_count=outdated_vectors_count).info("No outdated vectors found")
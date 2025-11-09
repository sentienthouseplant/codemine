from typing import Iterable

from openai import OpenAI

import structlog

from codemine.application.commands import ProcessRepoCommand
from codemine.domain.model.code_document import ChunkedDocument
from codemine.domain.ports.git_client import GitClient
from codemine.domain.repositories.vector_store_repo import VectorIndexRepo
from codemine.domain.services.code_chunking_service import CodeChunkingService
from codemine.domain.services.context_enrichment_service import ContextEnrichmentService
from codemine.domain.value_objects import GenericRecord, GitDirectory

logger = structlog.get_logger()

class EmbedGitRepoUseCase:
    """Coordinates the workflow to embed an entire Git repository."""

    def __init__(
        self,
        git_client: GitClient,
        code_chunking_service: CodeChunkingService,
        context_enrichment_service: ContextEnrichmentService,
        vector_store: VectorIndexRepo,
        openai_client: OpenAI,
        git_client_token: str | None = None,
    ) -> None:
        self.git_client = git_client
        self.code_chunking_service = code_chunking_service
        self.context_enrichment_service = context_enrichment_service
        self.vector_store = vector_store
        self.openai_client = openai_client

    def execute(self, command: ProcessRepoCommand) -> dict:
        """Run the embed workflow for the repository defined by the command."""
        logger.bind(repo_owner=command.repo_owner, repo_name=command.repo_name).info("Starting embed workflow")
        logger.info("Cloning repository")
        with self.git_client.temporary_clone(
            owner=command.repo_owner,
            repo_name=command.repo_name,
        ) as git_directory:
            logger.info("Chunking repository")
            chunked_documents = self._chunk_repository(git_directory)
            logger.info("Enriching documents")
            enriched_documents = []
            for document in chunked_documents:
                logger.bind(document=document.file_path).info("Enriching document")
                enriched_document = self.context_enrichment_service.enrich_document(self.openai_client, document)
                enriched_documents.append(enriched_document)

        logger.info("Building records")
        records = self._build_records(enriched_documents)
        logger.info("Embedding records")
        self.vector_store.embed_and_insert_records(records)

        if command.remove_outdated_chunks:
            self._remove_outdated_vectors(command, enriched_documents)

        return {
            "chunked_files": len(enriched_documents),
            "total_chunks": len(records),
            "index_name": self.vector_store.index_name,
        }

    def _chunk_repository(self, git_directory: GitDirectory) -> Iterable[ChunkedDocument]:
        for document in self.code_chunking_service.walk_directory(git_directory):
            yield self.code_chunking_service.chunk_document(document)

    def _build_records(self, documents: Iterable[ChunkedDocument]) -> list[GenericRecord]:
        records: list[GenericRecord] = []
        for document in documents:
            for chunk in document.chunks:
                records.append(chunk.generic_record)
        return records

    def _remove_outdated_vectors(
        self,
        command: ProcessRepoCommand,
        documents: Iterable[ChunkedDocument],
    ) -> None:
        logger.bind(repo_owner=command.repo_owner, repo_name=command.repo_name).info("Searching for outdated vectors")
        new_files = [document.file_path for document in documents]
        self.vector_store.remove_outdated_vectors(
            repo_owner=command.repo_owner,
            repo_name=command.repo_name,
            new_files=new_files,
        )

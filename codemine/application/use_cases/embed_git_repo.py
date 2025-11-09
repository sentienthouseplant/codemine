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
ENRICHMENT_BATCH_CHUNK_LIMIT = 50
EMBEDDING_RECORD_BATCH_SIZE = 50

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
        enriched_documents: list[ChunkedDocument] = []
        total_chunks = 0
        if command.create_index:
            self.vector_store.create_index_if_not_exists()
        with self.git_client.temporary_clone(
            owner=command.repo_owner,
            repo_name=command.repo_name,
        ) as git_directory:
            logger.info("Chunking repository")
            chunked_documents = self._chunk_repository(git_directory, command.ignore_globs)
            logger.info("Enriching documents")
            for enriched_batch in self._enrich_documents_in_batches(
                chunked_documents,
                ENRICHMENT_BATCH_CHUNK_LIMIT,
            ):
                enriched_documents.extend(enriched_batch)
                total_chunks += self._embed_documents_batch(enriched_batch)

        if command.remove_outdated_chunks:
            self._remove_outdated_vectors(command, enriched_documents)

        return {
            "chunked_files": len(enriched_documents),
            "total_chunks": total_chunks,
            "index_name": self.vector_store.index_name,
        }

    def _chunk_repository(self, git_directory: GitDirectory, ignore_globs: list[str] = []) -> Iterable[ChunkedDocument]:
        for document in self.code_chunking_service.walk_directory(git_directory, ignore_globs):
            yield self.code_chunking_service.chunk_document(document)

    def _enrich_documents_in_batches(
        self,
        documents: Iterable[ChunkedDocument],
        chunk_limit: int,
    ) -> Iterable[list[ChunkedDocument]]:
        batch: list[ChunkedDocument] = []
        chunk_count = 0
        for document in documents:
            logger.bind(document=document.file_path).info("Enriching document")
            enriched_document = self.context_enrichment_service.enrich_document(self.openai_client, document)
            batch.append(enriched_document)
            chunk_count += len(enriched_document.chunks)
            if chunk_count >= chunk_limit:
                yield batch
                batch = []
                chunk_count = 0
        if batch:
            yield batch

    def _embed_documents_batch(self, documents: list[ChunkedDocument]) -> int:
        if not documents:
            return 0
        logger.bind(batch_size=len(documents)).info("Building records for batch")
        records = self._build_records(documents)
        logger.bind(record_count=len(records)).info("Embedding records batch")
        for start_index in range(0, len(records), EMBEDDING_RECORD_BATCH_SIZE):
            record_batch = records[start_index : start_index + EMBEDDING_RECORD_BATCH_SIZE]
            logger.bind(record_batch_size=len(record_batch)).info("Embedding record sub-batch")
            self.vector_store.embed_and_insert_records(record_batch)
        return len(records)

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

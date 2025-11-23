from functools import cached_property

import structlog
from pinecone import Pinecone

from codemine.domain.repositories.vector_store_repo import VectorIndexRepo
from codemine.domain.value_objects import EmbeddedRecord, GenericRecord
from codemine.infrastructure.settings import Settings

logger = structlog.get_logger()


class PineconeVectorStore(VectorIndexRepo):
    def __init__(
        self,
        index_name: str,
        settings: Settings,
        embed_model: str = "llama-text-embed-v2",
        namespace: str = "default",
    ):
        super().__init__(index_name, settings)
        self.pc = Pinecone(api_key=self.settings.pinecone_api_key)
        self.embed_model = embed_model
        self.namespace = namespace
        self._has_index = self.pc.has_index(self.index_name)

    def create_index_if_not_exists(self):
        """Create Pinecone index if it doesn't exist (from embedder.py lines 16-27)"""
        if not self._has_index:
            logger.bind(index_name=self.index_name).info("Creating Pinecone index")
            self.pc.create_index_for_model(
                name=self.index_name,
                cloud="aws",
                region="us-east-1",
                embed={
                    "model": self.embed_model,
                    "field_map": {"text": "code_with_context"},
                },
            )
            self._has_index = True

    @property
    def index_host(self) -> str:
        """Get the host of the index."""
        describe_index_response = self.pc.describe_index(name=self.index_name)
        if describe_index_response.get("host") is not None:
            return describe_index_response["host"]
        else:
            self.create_index_if_not_exists()
            return self.index_host

    @cached_property
    def index(self) -> str:
        """Lazy-load index, creating if necessary."""
        index_host = self.index_host
        return self.pc.Index(host=index_host)

    def insert_vectors(self, records: list[EmbeddedRecord]):
        """Insert already-embedded vectors into Pinecone"""
        # Convert EmbeddedRecord to Pinecone format
        pinecone_records = self.convert_embedded_records_to_pinecone_vectors(records)
        if len(pinecone_records) == 0:
            logger.info("No pinecone records to insert")
            return
        self.index.upsert(namespace=self.namespace, vectors=pinecone_records)

    def embed_and_insert_records(self, records: list[GenericRecord]):
        """
        Pinecone can embed content directly using its inference API
        """

        # Convert GenericRecord to Pinecone format for upsert_records
        pinecone_records = self.convert_generic_records_to_pinecone_records(records)

        if len(pinecone_records) == 0:
            logger.info("No pinecone records to insert")
            return

        logger.bind(pinecone_records=len(pinecone_records)).info(
            "Inserting pinecone records"
        )
        # Pinecone will automatically embed using the configured model
        self.index.upsert_records(namespace=self.namespace, records=pinecone_records)

    def get_current_files_embedded(self, repo_owner: str, repo_name: str) -> list[str]:
        """
        Get list of all file paths currently embedded for this repo
        """
        current_files = []
        chunks = []

        # List all chunk IDs for this repo
        current_repo_chunk_ids = self.index.list(
            prefix=f"{repo_owner}#{repo_name}#", namespace=self.namespace
        )

        # Collect all chunk IDs from paginated results
        for chunk_id_page in current_repo_chunk_ids:
            chunks.extend(chunk_id_page)

        # Extract unique file paths from chunk IDs
        # ID format: owner#repo#file_path#index
        for chunk_id in chunks:
            file_path = chunk_id.split("#")[-2]
            if file_path not in current_files:
                current_files.append(file_path)

        return current_files

    def remove_vectors_by_file_path(
        self, file_path: str, repo_owner: str, repo_name: str
    ) -> bool:
        """
        Remove all chunks for a specific file
        """
        try:
            self.index.delete(
                namespace=self.namespace,
                filter={
                    "file_path": {"$eq": file_path},
                    "repo_owner": {"$eq": repo_owner},
                    "repo_name": {"$eq": repo_name},
                },
            )
            return True
        except Exception as e:
            print(f"Error removing chunks for {file_path}: {e}")
            return False

    def search_vectors(self, query: str, top_k: int = 10) -> list[GenericRecord]:
        """Search for relevant code chunks"""
        # Query the index with Pinecone's inference API using the new format
        results = self.index.search(
            namespace=self.namespace,
            query={"inputs": {"text": query}, "top_k": top_k},
            fields=["code_with_context", "repo_owner", "repo_name"],
        )

        # Convert Pinecone search results to GenericRecord format
        hits = results.get("result", {}).get("hits", [])
        generic_records = self.convert_pinecone_search_results_to_generic_records(hits)

        return generic_records

    def convert_embedded_records_to_pinecone_vectors(
        self, records: list[EmbeddedRecord]
    ) -> list[dict]:
        return [
            {
                "id": record.id,
                "metadata": record.metadata,
                "values": record.embedded_content,
            }
            for record in records
        ]

    def convert_embedded_records_to_generic_records(
        self, records: list[EmbeddedRecord]
    ) -> list[GenericRecord]:
        return [
            GenericRecord(
                id=record.id,
                unembedded_content=record.unembedded_content,
                metadata=record.metadata,
            )
            for record in records
        ]

    def convert_pinecone_search_results_to_generic_records(
        self, results: list[dict]
    ) -> list[GenericRecord]:
        """Convert Pinecone search results to GenericRecord format"""
        generic_records = []
        for hit in results:
            # Extract fields from Pinecone search result
            # Hit format: {"_id": "...", "_score": ..., "fields": {...}}
            fields = hit.get("fields", {})

            # Extract content from fields
            unembedded_content = fields.get("code_with_context", "")

            # Build metadata from fields and score
            record_metadata = {
                "repo_owner": fields.get("repo_owner", ""),
                "repo_name": fields.get("repo_name", ""),
                "file_path": fields.get("file_path", ""),
                "index": fields.get("index", ""),
            }

            # Include score if available
            if "_score" in hit:
                record_metadata["score"] = hit.get("_score")

            generic_records.append(
                GenericRecord(
                    id=hit.get("_id", ""),
                    unembedded_content=unembedded_content,
                    metadata=record_metadata,
                )
            )

        return generic_records

    def convert_generic_records_to_pinecone_records(
        self, records: list[GenericRecord]
    ) -> list[dict]:
        return [
            {
                "id": record.id,
                **record.metadata,
                "code_with_context": record.unembedded_content,
            }
            for record in records
        ]

from pinecone import Pinecone
from settings import settings
import pydantic
from data_classes import PineconeConfig, AnnotatedChunk

class RepoEmbedding():

    def __init__(self, config: PineconeConfig):
        self.config = config
        self.pc = Pinecone(api_key=settings.pinecone_api_key)
        self.has_index = self.pc.has_index(self.config.index_name)
        self.index_namespace = "default"

    def _create_index(self):
        if not self.has_index:
            self.pc.create_index_for_model(
                name=self.config.index_name,
                cloud="aws",
                region="us-east-1",
                embed={"model": self.config.embed_model, "field_map": {"text": self.config.code_chunk_location}}
            )
            self.has_index = True

    @property
    def index(self):
        if not self.has_index:
            self._create_index()
        return self.pc.Index(self.config.index_name)
    
    def validate_chunk(self, chunk: AnnotatedChunk):
        none_check = all(getattr(chunk, field) is not None for field in self.config.metadata_fields)
        if not none_check:
            raise ValueError(f"Missing metadata fields: {self.config.metadata_fields}")
        return chunk


    def embed_chunks(self, chunks: list[AnnotatedChunk]):
        for chunk in chunks:
            self.validate_chunk(chunk)
        self.index.upsert_records(
            self.index_namespace,
            records=[chunk.pinecone_record() for chunk in chunks]
        )

    def get_current_files(self, repo_owner, repo_name):
        current_files = []
        chunks = []
        current_repo_chunk_ids = self.index.list(prefix=f"{repo_owner}#{repo_name}#", namespace=self.index_namespace)
        for chunk_id_page in current_repo_chunk_ids:
            chunks.extend(chunk_id_page)
        for chunk in chunks:
            current_files.append(chunk.split("#")[-2])
        return current_files

    def remove_outdated_chunks(self, chunks: list[AnnotatedChunk], repo_owner, repo_name):
        current_files = self.get_current_files(repo_owner, repo_name)
        incoming_files = [chunk.file_name for chunk in chunks]
        for file in current_files:
            if file not in incoming_files:
                print(f"Removing outdated chunks with file name: {file}")
                self.index.delete(namespace=self.index_namespace, filter={"file_name": {"$eq": file}})

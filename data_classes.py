import pydantic


class Chunk(pydantic.BaseModel):
    index: int
    text: str


class FileChunks(pydantic.BaseModel):
    document: str
    chunks: list[Chunk]
    file_name: str
    repo_name: str
    repo_owner: str


class AnnotatedChunk(pydantic.BaseModel):
    index: int
    code_with_context: str
    file_name: str
    repo_name: str
    repo_owner: str

    def create_id(self):
        return f"{self.repo_owner}#{self.repo_name}#{self.file_name}#{self.index}"

    def pinecone_record(self):
        return {"id": self.create_id(), **self.model_dump()}


class PineconeConfig(pydantic.BaseModel):
    index_name: str
    metadata_fields: list[str] = ["repo_owner", "repo_name", "file_name"]
    code_chunk_location: str = "code_with_context"
    embed_model: str = "llama-text-embed-v2"

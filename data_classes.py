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
    text: str
    context: str
    file_name: str
    repo_name: str
    repo_owner: str

    def create_id(self):
        return f"{self.repo_owner}/{self.repo_name}/{self.file_name}/{self.index}"

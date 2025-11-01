import pydantic

from app.domain.value_objects import GenericRecord
class CodeChunk(pydantic.BaseModel):
    content: str
    context: str | None = None
    index: int
    repo_owner: str
    repo_name: str
    file_path: str

    @property
    def id(self):
        return f"{self.repo_owner}#{self.repo_name}#{self.file_path}#{self.index}"

    @property
    def metadata(self):
        return {
            "repo_owner": self.repo_owner,
            "repo_name": self.repo_name,
            "file_path": self.file_path,
            "index": self.index,
        }

    @property
    def full_content(self):
        if self.context:
            return f"""
            <context>
            {self.context}
            </context>
            <chunk>
            {self.content}
            </chunk>
            """
        return self.content

    @property
    def generic_record(self) -> GenericRecord:
        return GenericRecord(
            id=self.id,
            unembedded_content=self.full_content,
            metadata=self.metadata,
        )
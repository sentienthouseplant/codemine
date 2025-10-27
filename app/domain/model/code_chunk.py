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
    def content_with_context(self):
        return f"""
        <context>
        {self.context}
        </context>
        <chunk>
        {self.content}
        </chunk>
        """

    @property
    def generic_record(self) -> GenericRecord:
        return GenericRecord(
            id=self.id,
            unembedded_content=self.content_with_context,
            metadata=self.metadata,
        )
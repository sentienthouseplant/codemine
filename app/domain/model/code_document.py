import pydantic

from app.domain.value_objects import CodeDocumentContent
from app.domain.model.code_chunk import CodeChunk


class CodeDocument(pydantic.BaseModel):
    content: CodeDocumentContent
    file_path: str
    repo_owner: str
    repo_name: str
    file_type: str
    chunks: list[CodeChunk]

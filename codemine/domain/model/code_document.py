import pydantic

from codemine.domain.value_objects import CodeDocumentContent
from codemine.domain.model.code_chunk import CodeChunk


class CodeDocument(pydantic.BaseModel):
    content: CodeDocumentContent
    file_path: str
    repo_owner: str
    repo_name: str
    file_type: str

class ChunkedDocument(CodeDocument):
    chunks: list[CodeChunk]

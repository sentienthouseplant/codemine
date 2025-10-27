from typing import Annotated
import pydantic

ChunkContent = Annotated[str, "The content of a code chunk"]
ChunkContext = Annotated[str | None, "The context of a code chunk"]
CodeDocumentContent = Annotated[str, "The content of a code document"]

ContextualizedContent = Annotated[str, "The content of a code chunk with context"]

class GenericRecord(pydantic.BaseModel):
    id: str
    unembedded_content: ContextualizedContent
    metadata: dict
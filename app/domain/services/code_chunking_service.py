import tree_sitter_python
import tree_sitter_hcl
import tree_sitter_typescript
import tree_sitter_javascript
from app.domain.model.code_document import ChunkedDocument, CodeDocument
from semantic_text_splitter import CodeSplitter, TextSplitter
import os
from typing import Generator, Literal
from app.domain.value_objects import GitDirectory
from app.domain.model.code_chunk import CodeChunk


class CodeChunkingService:

    _langauge_registry = {
        "py": tree_sitter_python.language(),
        "tf": tree_sitter_hcl.language(),
        "tsx": tree_sitter_typescript.language_tsx(),
        "ts": tree_sitter_typescript.language_typescript(),
        "js": tree_sitter_javascript.language(),
        "jsx": tree_sitter_javascript.language(),
    }

    def __init__(self, splitter: Literal["code", "text"] = "code"):
        if splitter == "code":
            self.splitter = CodeSplitter
        else:
            self.splitter = TextSplitter

    def walk_directory(self, git_directory: GitDirectory) -> Generator[CodeDocument, None, None]:
        for root, _, files in os.walk(git_directory.path):
            for file in files:
                if file.endswith(tuple(self._langauge_registry.keys())):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, git_directory.path)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        file_extension = file.split(".")[-1]
                        yield CodeDocument(
                            content=code,
                            file_path=relative_path,
                            file_type=file_extension,
                            repo_owner=git_directory.repo_owner,
                            repo_name=git_directory.repo_name,
                        )

    def chunk_document(self, document: CodeDocument) -> ChunkedDocument:
        splitter = CodeSplitter(self._langauge_registry[document.file_type], 500)
        chunks = splitter.chunk_indices(document.content)
        chunks = [
            CodeChunk(index=index, content=text, file_path=document.file_path, repo_owner=document.repo_owner, repo_name=document.repo_name) for index, text in chunks
        ]
        return ChunkedDocument(
            content=document.content,
            file_path=document.file_path,
            repo_owner=document.repo_owner,
            repo_name=document.repo_name,
            file_type=document.file_type,
            chunks=chunks,
        )

    def chunk_repository(self, repository_path: str) -> list[ChunkedDocument]:
        for document in self.walk_directory(repository_path):
            yield self.chunk_document(document)

import fnmatch
import os
from collections.abc import Generator
from typing import Literal

import tree_sitter_hcl
import tree_sitter_javascript
import tree_sitter_markdown
import tree_sitter_python
import tree_sitter_rust
import tree_sitter_typescript
import tree_sitter_yaml
from semantic_text_splitter import CodeSplitter, TextSplitter
from structlog import get_logger

from codemine.domain.model.code_chunk import CodeChunk
from codemine.domain.model.code_document import ChunkedDocument, CodeDocument
from codemine.domain.value_objects import GitDirectory

logger = get_logger()

CHUNK_SIZE_RANGE = (500, 5000)


class CodeChunkingService:
    _langauge_registry = {
        "py": tree_sitter_python.language(),
        "tf": tree_sitter_hcl.language(),
        "tsx": tree_sitter_typescript.language_tsx(),
        "ts": tree_sitter_typescript.language_typescript(),
        "js": tree_sitter_javascript.language(),
        "jsx": tree_sitter_javascript.language(),
        "md": tree_sitter_markdown.language(),
        "rs": tree_sitter_rust.language(),
        "yml": tree_sitter_yaml.language(),
        "yaml": tree_sitter_yaml.language(),
    }

    def __init__(self, splitter: Literal["code", "text"] = "code"):
        if splitter == "code":
            self.splitter = CodeSplitter
        else:
            self.splitter = TextSplitter

    def walk_directory(
        self,
        git_directory: GitDirectory,
        ignore_globs: list[str] | None = None,
    ) -> Generator[CodeDocument, None, None]:
        ignore_globs = ignore_globs or []
        for root, _, files in os.walk(git_directory.path):
            for file in files:
                file_path = os.path.join(root, file)
                if any(
                    fnmatch.fnmatch(file_path, ignore_glob)
                    for ignore_glob in ignore_globs
                ):
                    logger.bind(file=file).info("File is ignored by glob pattern")
                    continue
                logger.bind(file=file).info("Checking file")
                if file.split(".")[-1] in self._langauge_registry:
                    logger.bind(file=file).info("File is a code file")
                    relative_path = os.path.relpath(file_path, git_directory.path)
                    with open(file_path, encoding="utf-8") as f:
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
        splitter = CodeSplitter(
            self._langauge_registry[document.file_type], CHUNK_SIZE_RANGE
        )
        chunks = splitter.chunk_indices(document.content)
        chunks = [
            CodeChunk(
                index=index,
                content=text,
                file_path=document.file_path,
                repo_owner=document.repo_owner,
                repo_name=document.repo_name,
            )
            for index, text in chunks
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

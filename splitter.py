import os
from semantic_text_splitter import CodeSplitter
import tree_sitter_python

from repo import clone_repo
from data_classes import FileChunks, Chunk

# Using character-based splitting with a capacity of 500 characters
splitter = CodeSplitter(tree_sitter_python.language(), 500)

def chunk_repository(repo_owner: str, repo_name: str) -> list[FileChunks]:
    repository_chunks = []
    with clone_repo(repo_owner, repo_name) as repo:
        for file in os.listdir(repo.working_tree_dir):
            if file.endswith(".py"):
                with open(os.path.join(repo.working_tree_dir, file), "r", encoding="utf-8") as f:
                    code = f.read()
                    chunks = splitter.chunk_indices(code)
                    chunks = [Chunk(index=index, text=text) for index, text in chunks]
                    file_chunks = FileChunks(document=code, chunks=chunks, file_name=file, repo_name=repo_name, repo_owner=repo_owner)

                    repository_chunks.append(file_chunks)
    return repository_chunks
import os
from semantic_text_splitter import CodeSplitter
import tree_sitter_python

from repo import clone_repo

# Using character-based splitting with a capacity of 500 characters
splitter = CodeSplitter(tree_sitter_python.language(), 500)

def chunk_repository(repo_owner: str, repo_name: str) -> list[dict[str, list[tuple[int, str]]]]:
    repository_chunks = []
    with clone_repo(repo_owner, repo_name) as repo:
        for file in os.listdir(repo.working_tree_dir):
            if file.endswith(".py"):
                with open(os.path.join(repo.working_tree_dir, file), "r", encoding="utf-8") as f:
                    code = f.read()
                    chunks = splitter.chunk_indices(code)
                    repository_chunks.append({"document": code, "chunks": chunks})
    return repository_chunks
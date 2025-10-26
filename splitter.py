import os
from semantic_text_splitter import CodeSplitter
import tree_sitter_python

from repo import clone_repo
from data_classes import FileChunks, Chunk

langauge_mapping = {
    "py": tree_sitter_python.language(),
}


def chunk_repository(repo_owner: str, repo_name: str) -> list[FileChunks]:
    repository_chunks = []
    with clone_repo(repo_owner, repo_name) as repo:
        for root, dirs, files in os.walk(repo.working_tree_dir):
            for file in files:
                if file.endswith(tuple(langauge_mapping.keys())):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo.working_tree_dir)
                    with open(file_path, "r", encoding="utf-8") as f:
                        code = f.read()
                        file_extension = file.split(".")[-1]
                        splitter = CodeSplitter(langauge_mapping[file_extension], 500)
                        chunks = splitter.chunk_indices(code)
                        chunks = [
                            Chunk(index=index, text=text) for index, text in chunks
                        ]
                        file_chunks = FileChunks(
                            document=code,
                            chunks=chunks,
                            file_name=relative_path,
                            repo_name=repo_name,
                            repo_owner=repo_owner,
                        )
                        repository_chunks.append(file_chunks)

    return repository_chunks

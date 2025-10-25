import code_splitter
import os

from repo import clone_repo

splitter = code_splitter.CharSplitter(code_splitter.Language.Python, max_size=500)

def chunk_repository(repo_owner: str, repo_name: str):
    repository_chunks = []
    with clone_repo(repo_owner, repo_name) as repo:
        for file in os.listdir(repo.working_tree_dir):
            if file.endswith(".py"):
                with open(os.path.join(repo.working_tree_dir, file), "rb") as f:
                    code = f.read()
                    chunks = splitter.split(code)
                    repository_chunks.append({"document": code, "chunks": chunks})
    return repository_chunks
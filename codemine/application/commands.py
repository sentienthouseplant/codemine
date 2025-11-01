import pydantic

class ProcessRepoCommand(pydantic.BaseModel):
    repo_owner: str
    repo_name: str
    remove_outdated_chunks: bool = True

class RemoveOutdatedChunksCommand(pydantic.BaseModel):
    repo_owner: str
    repo_name: str
    new_files: list[str]

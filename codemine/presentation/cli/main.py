from codemine.presentation.cli.containers import get_embed_git_repo_use_case, get_search_chunks_use_case
from codemine.application.commands import ProcessRepoCommand
from codemine.application.queries import SearchEmbeddingsQuery
import click
import structlog
from rich.console import Console
import logging


structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING)
)

@click.group()
def cli(): ...

@cli.command()
@click.option("--repo-owner", type=str, required=True)
@click.option("--repo-name", type=str, required=True)
@click.option("--remove-outdated-chunks", is_flag=True, default=False)
def embed_repo(repo_owner, repo_name, remove_outdated_chunks):
    use_case = get_embed_git_repo_use_case()
    console = Console()
    with console.status("Embedding repository...", spinner="squareCorners"):
        results = use_case.execute(ProcessRepoCommand(
            repo_owner=repo_owner, repo_name=repo_name, remove_outdated_chunks=remove_outdated_chunks,
        ))
        console.print(f"Repository {repo_owner}/{repo_name} embedded successfully")
        console.print(f"Total chunks: {results['total_chunks']}")
        console.print(f"Chunked files: {results['chunked_files']}")
        console.print(f"Index name: {results['index_name']}")

@cli.command()
@click.option("--query", type=str, required=True)
def search_chunks(query):
    console = Console()
    with console.status("Searching for chunks...", spinner='arc'):
        use_case = get_search_chunks_use_case()
        results =use_case.execute(SearchEmbeddingsQuery(
            query=query,
        ))
        for result in results:
            console.print(f"Found chunk: {result.id}")
from codemine.presentation.cli.containers import get_embed_git_repo_use_case, get_search_chunks_use_case
from codemine.application.commands import ProcessRepoCommand
from codemine.application.queries import SearchEmbeddingsQuery

import click

@click.group()
def cli(): ...

@cli.command()
@click.option("--repo-owner", type=str, required=True)
@click.option("--repo-name", type=str, required=True)
@click.option("--remove-outdated-chunks", is_flag=True, default=False)
def embed_repo(repo_owner, repo_name, remove_outdated_chunks):
    use_case = get_embed_git_repo_use_case()
    use_case.execute(ProcessRepoCommand(
        repo_owner=repo_owner, repo_name=repo_name, remove_outdated_chunks=remove_outdated_chunks,
    ))

@cli.command()
@click.option("--query", type=str, required=True)
def search_chunks(query):
    use_case = get_search_chunks_use_case()
    results =use_case.execute(SearchEmbeddingsQuery(
        query=query,
    ))
    for result in results:
        print(result.id)
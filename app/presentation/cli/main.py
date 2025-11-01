from app.presentation.cli.containers import get_embed_git_repo_use_case
from app.application.commands import ProcessRepoCommand

def main():
    use_case = get_embed_git_repo_use_case()
    use_case.execute(ProcessRepoCommand(
        repo_owner="sentienthouseplant",
        repo_name="purplepipes",
        remove_outdated_chunks=True,
    ))

if __name__ == "__main__":
    main()
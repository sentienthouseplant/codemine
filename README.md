# Codemine

A Python project to embed Git repositories into a Pinecone vector database for semantic search.

## Features
- Embeds code chunks from Git repositories.
- Supports incremental updates (remove outdated chunks).
- Uses Tree-sitter for language-aware code splitting.
- Search embedded code chunks using natural language queries.

## Prerequisites

- Python >= 3.12
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd codemine
    ```

2.  **Install dependencies:**

    Using `uv`:
    ```bash
    uv sync
    ```

    Using `pip`:
    ```bash
    pip install -e .
    ```

3.  **Configure Environment Variables:**

    Create a `.env` file in the root directory with the following variables:

    ```env
    PINECONE_API_KEY=your_pinecone_api_key
    GITHUB_TOKEN=your_github_token
    OPENAI_API_KEY=your_openai_api_key
    # Optional: Defaults to "https://openrouter.ai/api/v1"
    # OPENAI_BASE_URL=https://api.openai.com/v1
    ```

## Usage

The project installs a `codemine` CLI command.

### Embed a Repository

To embed a repository into the vector store:

```bash
codemine embed-repo \
  --repo-owner <owner> \
  --repo-name <repo> \
  [--create-index] \
  [--remove-outdated-chunks] \
  [--ignore-glob "**/tests/**"]
```

**Options:**
- `--repo-owner`: The owner of the GitHub repository (required).
- `--repo-name`: The name of the GitHub repository (required).
- `--create-index`: Create a new Pinecone index if it doesn't exist.
- `--remove-outdated-chunks`: Remove chunks that are no longer in the repository.
- `--ignore-glob`: Glob pattern to ignore files (can be used multiple times).

**Example:**
```bash
codemine embed-repo \
  --repo-owner jackharrington \
  --repo-name codebase-embedding \
  --create-index \
  --ignore-glob "**/__pycache__/**"
```

### Search Chunks

To search for code chunks:

```bash
codemine search-chunks --query "How does the embedding client work?"
```

**Options:**
- `--query`: The search query (required).

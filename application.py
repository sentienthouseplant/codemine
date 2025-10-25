from splitter import chunk_repository
from context_chunker import context_chunker

def generate_context_chunks(repo_owner: str, repo_name: str):
    context_chunks = []
    repository_chunks = chunk_repository(repo_owner, repo_name)
    for file_chunk in repository_chunks:
        document = file_chunk['document']
        chunks = file_chunk['chunks']
        for chunk in chunks:
            output = context_chunker(document, chunk.text)
            with open(f"outputs/{repo_owner}_{repo_name}_{chunk.start}_{chunk.end}.txt", "w") as f:
                context_chunks.append(output)
    return context_chunks

if __name__ == "__main__":
    context_chunks = generate_context_chunks("sentienthouseplant", "Millow")
    print(context_chunks)


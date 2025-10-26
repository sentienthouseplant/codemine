import pprint
from splitter import chunk_repository
from context_chunker import process_file_chunk
from data_classes import AnnotatedChunk, PineconeConfig
from embedder import RepoEmbedding


def generate_context_chunks(repo_owner: str, repo_name: str):
    context_chunks = []
    repository_chunks = chunk_repository(repo_owner, repo_name)
    for file_chunk in repository_chunks:
        for annotated_chunk in process_file_chunk(file_chunk):
            context_chunks.append(annotated_chunk)
    return context_chunks


if __name__ == "__main__":
    context_chunks = generate_context_chunks("sentienthouseplant", "purplepipes")
    PineconeConfig = PineconeConfig(index_name="codebase-dense")
    embedder = RepoEmbedding(config=PineconeConfig)
    embedder.embed_chunks(context_chunks)
    embedder.remove_outdated_chunks(context_chunks, "sentienthouseplant", "purplepipes")
    print(embedder.get_stats())

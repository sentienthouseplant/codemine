from splitter import chunk_repository
from context_chunker import context_chunker
from data_classes import AnnotatedChunk, PineconeConfig
from embedder import RepoEmbedding

def generate_context_chunks(repo_owner: str, repo_name: str):
    context_chunks = []
    repository_chunks = chunk_repository(repo_owner, repo_name)
    for file_chunk in repository_chunks:
        document = file_chunk.document
        chunks = file_chunk.chunks
        for chunk in chunks:
            chunk_index = chunk.index
            chunk_text = chunk.text
            chunk_with_context = context_chunker(document, chunk_text)
            context_chunks.append(AnnotatedChunk(index=chunk_index, code_with_context=chunk_with_context, file_name=file_chunk.file_name, repo_name=file_chunk.repo_name, repo_owner=file_chunk.repo_owner))
    return context_chunks

def generate_fake_context_chunks(repo_owner: str, repo_name: str):
    context_chunks = []
    for i in range(20):
        context_chunks.append(AnnotatedChunk(index=i, code_with_context=f"This is a fake context chunk {i}", file_name=f"fake_file_{i}.py", repo_name=repo_name, repo_owner=repo_owner))
    return context_chunks

if __name__ == "__main__":
    context_chunks = generate_context_chunks("sentienthouseplant", "purplepipes")
    PineconeConfig = PineconeConfig(index_name="codebase-dense")
    embedder = RepoEmbedding(config=PineconeConfig)
    embedder.embed_chunks(context_chunks)
    embedder.remove_outdated_chunks(context_chunks, "sentienthouseplant", "purplepipes")
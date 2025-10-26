from string import Template

from openai import OpenAI

from settings import settings

from data_classes import FileChunks
from data_classes import AnnotatedChunk

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.openrouter_api_key,
)

CONTEXT_PROMPT = Template("""
Here is the chunk we want to situate within the document given.
<chunk> 
$chunk
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else.
""")

DOCUMENT_PROMPT = Template("""
Here is the document the user will chunk. Use this document to generate the context for the chunk:
<document> 
$document
</document>
""")


def generate_chunk_with_context(document: str, chunk: str):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite-preview-09-2025",
        messages=[
            {
                "role": "system",
                "content": DOCUMENT_PROMPT.substitute(document=document),
                "cache_control": {"type": "ephemeral"},
            },
            {
                "role": "user",
                "content": CONTEXT_PROMPT.substitute(chunk=chunk),
                "cache_control": {"type": "ephemeral"},
            },
        ],
    )
    context = response.choices[0].message.content
    return f"""
    <context>
    {context}
    </context>
    <chunk>
    {chunk}
    </chunk>
    """

def process_file_chunk(file_chunk: FileChunks):
    for chunk in file_chunk.chunks:
        chunk_with_context = generate_chunk_with_context(file_chunk.document, chunk.text)
        yield AnnotatedChunk(
            index=chunk.index,
            code_with_context=chunk_with_context,
            file_name=file_chunk.file_name,
            repo_name=file_chunk.repo_name,
            repo_owner=file_chunk.repo_owner,
        )
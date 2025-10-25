from string import Template

from openai import OpenAI

from settings import settings

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=settings.openrouter_api_key,
)

CONTEXT_PROMPT = Template("""
<document> 
$document
</document> 
Here is the chunk we want to situate within the whole document 
<chunk> 
$chunk
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else. 
""")

def context_chunker(document: str, chunk: str):
    response = client.chat.completions.create(
        model="google/gemini-2.5-flash-lite-preview-09-2025",
        messages=[{"role": "user", "content": CONTEXT_PROMPT.substitute(document=document, chunk=chunk)}],
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



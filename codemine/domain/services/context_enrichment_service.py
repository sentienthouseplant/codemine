from string import Template

import structlog
from openai import OpenAI

from codemine.domain.model.code_document import ChunkedDocument

logger = structlog.get_logger()
CONTEXT_PROMPT = Template(
    
        "Here is the chunk we want to situate within the document given.\n"
        "<chunk>\n"
        "$chunk\n"
        "</chunk>\n"
        "Provide a short context to situate this chunk within the overall "
        "document to improve search retrieval of the chunk. Answer only with the "
        "succinct context and nothing else.\n"
    
)

DOCUMENT_PROMPT = Template(
    
        "Here is the document the user will chunk. "
        "Use this document to generate the context for the chunk:\n"
        "<document>\n"
        "$document\n"
        "</document>\n"
    
)


class ContextEnrichmentService:
    def enrich_document(
        self, client: OpenAI, document: ChunkedDocument
    ) -> ChunkedDocument:
        """
        Enriches each chunk with context from the LLM.
        Returns a new ChunkedDocument with new chunks that have context set.
        """
        logger.bind(document=document.file_path).info("Enriching document")
        enriched_chunks = []

        for chunk in document.chunks:
            logger.bind(chunk=chunk.file_path, index=chunk.index).info(
                "Enriching chunk"
            )
            response = client.chat.completions.create(
                model="google/gemini-2.5-flash-lite-preview-09-2025",
                messages=[
                    {
                        "role": "system",
                        "content": DOCUMENT_PROMPT.substitute(
                            document=document.content
                        ),
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "role": "user",
                        "content": CONTEXT_PROMPT.substitute(chunk=chunk.content),
                        "cache_control": {"type": "ephemeral"},
                    },
                ],
            )

            enriched_chunk = chunk.model_copy(
                update={"context": response.choices[0].message.content}
            )
            enriched_chunks.append(enriched_chunk)

        return document.model_copy(update={"chunks": enriched_chunks})

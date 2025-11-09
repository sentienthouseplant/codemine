from codemine.application.queries import SearchEmbeddingsQuery
from codemine.domain.repositories.vector_store_repo import VectorIndexRepo
from codemine.domain.value_objects import EmbeddedRecord

import structlog

logger = structlog.get_logger()

class SearchChunksUseCase:
    def __init__(self, vector_store: VectorIndexRepo):
        self.vector_store = vector_store

    def execute(self, query: SearchEmbeddingsQuery) -> list[EmbeddedRecord]:
        logger.bind(query=query.query).info("Searching for chunks")
        results = self.vector_store.search_vectors(query.query)
        logger.bind(results=len(results)).info("Found chunks")
        return results

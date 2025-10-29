from typing import Protocol

from app.domain.value_objects import GenericRecord, EmbeddedRecord

class EmbeddingClient(Protocol):
    def embed_generic_record(self, record: GenericRecord) -> EmbeddedRecord:
        ...
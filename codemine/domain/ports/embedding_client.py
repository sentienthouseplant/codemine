from typing import Protocol

from codemine.domain.value_objects import EmbeddedRecord, GenericRecord


class EmbeddingClient(Protocol):
    def embed_generic_record(
        self, record: GenericRecord, *args, **kwargs
    ) -> EmbeddedRecord: ...

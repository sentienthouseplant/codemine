import pydantic


class SearchEmbeddingsQuery(pydantic.BaseModel):
    query: str

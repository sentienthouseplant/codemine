from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pinecone_api_key: str
    github_token: str
    openai_api_key: str
    openai_base_url: str = "https://openrouter.ai/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

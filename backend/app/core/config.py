from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"
    # RAG
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    embedding_dim: int = 384
    # Celery / Redis
    redis_url: str = "redis://localhost:6379/0"
    # Authentification JWT
    jwt_secret_key: str = "change-me-in-production-with-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60.
    # Langfuse (observabilité) — optionnel
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_host: str = "https://cloud.langfuse.com"


settings = Settings()
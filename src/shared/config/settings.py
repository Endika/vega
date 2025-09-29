from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://vega_user:vega_password@localhost:5432/vega_ai"

    # OpenAI
    openai_api_key: str = "your-openai-api-key"
    openai_model: str = "gpt-4"
    embedding_model: str = "text-embedding-ada-002"

    # Application
    app_name: str = "Vega Customer Support System"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    # WebSocket
    ws_max_connections: int = 100
    ws_heartbeat_interval: int = 30

    # RAG
    knowledge_base_path: str = "./knowledge_base"
    vector_store_type: str = "chroma"

    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_max_connections: int = 100
    redis_retry_on_timeout: bool = True

    # Security
    secret_key: str = "change-me-in-production"  # noqa: S105
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False
        # Allow environment variables to override defaults
        env_prefix = ""


# Global settings instance
settings = Settings()

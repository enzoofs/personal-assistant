from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    tavily_api_key: str = ""
    google_credentials_path: str = "./credentials.json"
    google_token_path: str = "./token.json"
    vault_path: str = "./vault"
    chroma_db_path: str = "./chroma_db"
    memory_db_path: str = "./memory.db"
    atlas_api_key: str = "dev-key"
    timezone: str = "America/Sao_Paulo"
    openai_model: str = "gpt-4o-mini"
    session_expiry_hours: int = 24

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

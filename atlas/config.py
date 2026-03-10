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
    # ElevenLabs TTS
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "pNInz6obpgDQGcFmaJgB"  # "Adam" - deep, professional
    # Edge TTS (free fallback)
    edge_tts_voice: str = "pt-BR-AntonioNeural"  # Brazilian Portuguese male voice
    # Groq (free LLM fallback)
    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    # Response mode: "text" (no audio), "audio" (Edge TTS free), "audio_premium" (ElevenLabs)
    response_mode: str = "text"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

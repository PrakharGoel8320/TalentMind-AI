from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List
import json

class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "TalentMind AI Backend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # Auth
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    
    # AI Provider
    GEMMA_API_BASE: str = "http://localhost:11434/v1"
    GEMMA_MODEL_NAME: str = "gemma:7b"
    
    # Email / Communication
    EMAIL_MODE: str = "mock"
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: Optional[str] = None
    UPLOAD_MAX_PDF_MB: int = 5
    MAX_AGENT_STEPS: int = 8
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def cors_origins(self) -> List[str]:
        raw = (self.BACKEND_CORS_ORIGINS or "").strip()
        if not raw:
            return []

        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except Exception:
                pass

        return [origin.strip() for origin in raw.split(",") if origin.strip()]

settings = Settings()

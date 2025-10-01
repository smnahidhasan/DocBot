import os
from pydantic import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "DocBot API"
    VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Database settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "docbot")

    # Redis settings
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # Security settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Authentication settings
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    PASSWORD_MIN_LENGTH: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))

    # CORS settings (use raw string + split manually)
    CORS_ORIGINS_RAW: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
    CORS_CREDENTIALS: bool = os.getenv("CORS_CREDENTIALS", "True").lower() == "true"
    CORS_METHODS_RAW: str = os.getenv("CORS_METHODS", "GET,POST,PUT,DELETE,OPTIONS")
    CORS_HEADERS_RAW: str = os.getenv("CORS_HEADERS", "*")

    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Email settings
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@docbot.com")

    # Frontend URL
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # File upload settings (raw string, split manually)
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "50")) * 1024 * 1024  # MB → bytes
    ALLOWED_FILE_TYPES_RAW: str = os.getenv("ALLOWED_FILE_TYPES", "pdf,txt,docx")

    # RAG settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-ada-002")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

    # Vector store settings
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "chroma")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "app/api/rag/db/knowledge_base")

    class Config:
        env_file = ".env"
        case_sensitive = True

    # ---------- Properties for parsing ----------
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS_RAW.split(",") if origin.strip()]

    @property
    def CORS_METHODS(self) -> List[str]:
        return [method.strip() for method in self.CORS_METHODS_RAW.split(",") if method.strip()]

    @property
    def CORS_HEADERS(self) -> List[str]:
        return [header.strip() for header in self.CORS_HEADERS_RAW.split(",") if header.strip()]

    @property
    def ALLOWED_FILE_TYPES(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES_RAW.split(",") if ext.strip()]


# Create global settings instance
settings = Settings()


# Validation
def validate_settings():
    """Validate critical settings"""
    errors = []

    if settings.SECRET_KEY == "your-secret-key-here":
        errors.append("SECRET_KEY must be set to a secure value")

    if len(settings.SECRET_KEY) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")

    if not settings.MONGODB_URL:
        errors.append("MONGODB_URL must be set")

    if not settings.CORS_ORIGINS:
        errors.append("CORS_ORIGINS must not be empty")

    if not settings.ALLOWED_FILE_TYPES:
        errors.append("ALLOWED_FILE_TYPES must not be empty")

    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")


# Validate on import
validate_settings()

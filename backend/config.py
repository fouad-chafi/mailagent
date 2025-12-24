"""
Configuration centralisee pour l'application mailagent.
Utilise pydantic-settings pour la gestion des variables d'environnement.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Gmail API
    GMAIL_CREDENTIALS_PATH: str = "credentials/gmail_credentials.json"
    GMAIL_TOKEN_PATH: str = "credentials/token.pickle"

    # LM Studio
    LM_STUDIO_URL: str = "http://localhost:1234/v1/chat/completions"
    LM_STUDIO_MODEL: str = "qwen2.5-7b-instruct-1m"
    LM_STUDIO_TIMEOUT: int = 60
    LM_STUDIO_MAX_TOKENS_CLASSIFY: int = 50
    LM_STUDIO_MAX_TOKENS_RESPONSE: int = 1500

    # Database
    DATABASE_URL: str = "sqlite:///data/emails.db"

    # Application
    SYNC_INTERVAL_MINUTES: int = 15
    MAX_EMAILS_PER_SYNC: int = 50
    RESPONSE_VARIANTS: int = 3

    # Security
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Classification
    IMPORTANCE_LEVELS: List[str] = ["high", "medium", "low"]
    CATEGORIES: List[str] = [
        "professionnel",
        "personnel",
        "newsletter",
        "notification",
        "urgent",
        "commercial",
        "administratif",
    ]

    # Response tones
    RESPONSE_TONES: List[str] = ["formal", "casual", "neutral"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

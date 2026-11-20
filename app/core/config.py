from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str
    api_version: str
    app_description: str

    # Database
    mongodb_uri: str
    mongodb_database: str

    # AI Configuration
    ai_provider: Literal["openai", "gemini"]
    ai_model: str
    ai_prompt_path: str

    # API Keys
    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
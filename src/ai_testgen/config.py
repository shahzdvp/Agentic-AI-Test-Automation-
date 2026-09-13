from loguru import logger
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for AI TestGen."""
    google_api_key: SecretStr = Field(validation_alias="GOOGLE_API_KEY")
    model_name: str = Field(default='gemini-3.6-flash', validation_alias="AI_TESTGEN_MODEL")
    max_retries: int = Field(default=3, validation_alias="AI_TESTGEN_MAX_RETRIES")
    temperature: float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def get_settings() -> Settings:
    """Retrieve and validate settings."""
    try:
        return Settings()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please ensure GOOGLE_API_KEY is set in your environment or .env file.")
        raise

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Anthropic API
    anthropic_api_key: str

    # Resend Email API
    resend_api_key: str

    # User Configuration
    user_email: str

    # Database
    database_url: str = "sqlite:///./reddit_summarizer.db"

    # Digest Configuration
    digest_time: str = "06:00"
    posts_per_digest: int = 12

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

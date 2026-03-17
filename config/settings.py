"""Application settings loaded from environment variables."""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API and paths configuration. Set via env or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_url: str = "https://api.openai.com/v1"
    api_key: str = ""
    model_name: str = "gpt-5-nano"
    papers_path: Path = Path("papers")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.papers_path = Path(self.papers_path).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()

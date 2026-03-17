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
    model_name: str = "gpt-4o-mini"
    model_list: str = "gpt-4o-mini,gpt-4o,gpt-4-turbo,gpt-4,gpt-3.5-turbo"
    papers_path: Path = Path("papers")
    data_dir: Path = Path("data")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.papers_path = Path(self.papers_path).expanduser().resolve()
        self.data_dir = Path(self.data_dir).expanduser().resolve()

    @property
    def model_list_parsed(self) -> list[str]:
        return [m.strip() for m in self.model_list.split(",") if m.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="LAYA_DEMO_",
        env_ignore_empty=True,
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = Field(default=0, ge=0, le=65535)
    model_default: str = "multilingual"
    device: str | None = None
    preload: bool = False

    @field_validator("device", mode="before")
    @classmethod
    def auto_device_marker_means_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip().lower() in {"", "none"}:
            return None
        return value

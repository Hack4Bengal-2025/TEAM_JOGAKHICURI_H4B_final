import os
from typing import ClassVar
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

load_dotenv()


class Config(BaseSettings):
    # Annotate non‑field settings as ClassVar or provide Field()
    APP_NAME: ClassVar[str] = os.getenv(
        "APP_NAME", "Hack4Bengal"
    )  # resolves non-annotation error :contentReference[oaicite:1]{index=1}

    # Typed, validated settings
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str
    SQLALCHEMY_DATABASE_URI: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="allow"
    )


config = Config()

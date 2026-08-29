from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OptiTwinAI"
    environment: str = "development"
    database_url: str = "sqlite:///./optitwinai.db"
    jwt_secret: str = "change-this-secret-later"
    access_token_expire_minutes: int = 60
    demo_mode: bool = True
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()


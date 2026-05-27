from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TaskFlow"
    env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 120
    database_url: str = "postgresql+psycopg://taskflow:taskflow@localhost:5432/taskflow"
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl_seconds: int = 300
    frontend_origin: str = "http://localhost:5173"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_prefix="TASKFLOW_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_state() -> None:
    get_settings.cache_clear()

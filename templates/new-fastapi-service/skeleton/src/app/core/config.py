"""Settings from environment variables (12-factor), validated by pydantic."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    service_name: str = "${{ values.name }}"
    # From the CloudNativePG Secret in the cluster, docker-compose locally.
    database_url: str = "postgresql://app:app@localhost:5432/app"
    log_level: str = "info"
    db_pool_size: int = 5
    db_max_overflow: int = 5


@lru_cache
def get_settings() -> Settings:
    return Settings()

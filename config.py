from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    abuseipdb_api_key: str
    abuseipdb_base_url: str = "https://api.abuseipdb.com/api/v2/check"
    abuseipdb_max_age_days: int = 90
    risk_threshold: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
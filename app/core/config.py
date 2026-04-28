from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    project_name: str = "Vehicle Management API"
    database_url: str = "sqlite:///./app.db"
    jwt_secret_key: str = "local-development-jwt-secret-key-change-before-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    redis_url: str = "redis://localhost:6379/0"
    usd_cache_key: str = "usd_brl_rate"
    usd_cache_ttl_seconds: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()

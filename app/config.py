from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str
    
    JWT_SECRET_KEY = "change-me"
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = 14
    JWT_ISSUER = "test-study-api"
    JWT_AUDIENCE = "test-study-users"

    COOKIE_SECURE = False
    COOKIE_SAMESITE = "lax"


settings = Settings()


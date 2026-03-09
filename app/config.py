from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/shortener"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BASE_URL: str = "http://localhost:8000"
    DEFAULT_UNUSED_DAYS: int = 30

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
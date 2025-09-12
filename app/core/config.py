from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DATABASE_URL: str = "sqlite:///./dev.db"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]


settings = Settings()  # pyright: ignore[reportCallIssue]

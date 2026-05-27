from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    database_url: str = "sqlite:///./digipros.db"
    jwt_secret: str = "dev-only-change-me"
    session_secret: str = "dev-only-change-me-too"
    access_token_expire_minutes: int = 60 * 24 * 7

    frontend_url: str = "http://localhost:5173"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    google_client_id: str | None = None
    google_client_secret: str | None = None

    apple_client_id: str | None = None
    apple_team_id: str | None = None
    apple_key_id: str | None = None
    apple_private_key: str | None = None


settings = Settings()

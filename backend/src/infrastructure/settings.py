from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./db.sqlite3"

    jwt_secret: str
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30

    openai_api_key: str = "sk-..."
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

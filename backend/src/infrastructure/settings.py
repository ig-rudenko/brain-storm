from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: str = "sqlite+aiosqlite:///./db.sqlite3"

    jwt_secret: str = "secret"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30

    openai_api_key: str = "sk-..."
    openai_model_name: str = "gpt-4o-mini"


settings = Settings()

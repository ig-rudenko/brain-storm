from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    jwt_secret: str = "secret"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 30


settings = Settings()

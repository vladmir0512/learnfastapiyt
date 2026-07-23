from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sync_database_url: str
    async_database_url: str



settings = Settings()
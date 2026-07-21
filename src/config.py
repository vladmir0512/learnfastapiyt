from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    async_database_url: str
    sync_database_url: str


settings = Settings()

import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_client_id: str = os.getenv("ASTRA_DB_CLIENT_ID")
    db_client_secret: str = os.getenv("ASTRA_DB_CLIENT_SECRET")
    class Config:
        env_file = '.env'
        extra = 'ignore'

@lru_cache # Caches the result of the function
def get_settings():
    return Settings()

import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    db_client_id: str
    db_client_secret: str

def get_settings():
    return Settings()
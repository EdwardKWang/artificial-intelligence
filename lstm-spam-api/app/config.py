from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # pydantic-settings guide:
    # https://medium.com/@mahimamanik.22/environment-variables-using-pydantic-ff6ccb2b8976
    aws_access_key_id: str = None
    aws_secret_access_key: str = None
    db_client_id: str = Field(..., alias="ASTRA_DB_CLIENT_ID")
    db_client_secret: str = Field(..., alias="ASTRA_DB_CLIENT_SECRET")
    class Config:
        env_file = '.env'
        extra = 'ignore'

@lru_cache # Caches the result of the function
def get_settings():
    return Settings()

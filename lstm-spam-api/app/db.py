import pathlib
from . import config

BASE_DIR = pathlib.Path(__file__).resolve().parent
CLUSTER_BUNDLE = str(BASE_DIR / "ignored"/ "astradb_connect.zip")

settings = config.get_settings()

ASTRA_DB_CLIENT_ID = settings.db_client_id
ASTRA_DB_CLIENT_SECRET = settings.db_client_secret



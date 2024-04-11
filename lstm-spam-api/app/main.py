#This is the main module for the FastAPI application
# uvicorn app.main:app --reload

import pathlib
from typing import Optional
from fastapi import FastAPI

from . import (config, ml)

app = FastAPI()
settings = config.get_settings()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-metadata.json"

AI_MODEL = None

@app.on_event("startup")
def on_startup():
    """Startup event handler
    """
    global AI_MODEL
    AI_MODEL = ml.AIModel(
        model_path=MODEL_PATH,
        tokenizer_path=TOKENIZER_PATH,
        metadata_path=METADATA_PATH
    )

@app.get("/") # /?q=this is awesome
def read_index(q:Optional[str] = None):
    """_summary_

    :param q: _description_, defaults to None
    :type q: Optional[str], optional
    :return: _description_
    :rtype: _type_
    """
    global AI_MODEL
    query = q or "Hello World"
    preds_dict = AI_MODEL.predict_text(query)
    # NoSQL -> cassandra -> Datastax AstraDB
    return {"query": query, "results":preds_dict, "db_client_id": settings.db_client_id, "db_client_secret": settings.db_client_secret}
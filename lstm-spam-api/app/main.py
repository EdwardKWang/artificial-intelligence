# This is the main module for the FastAPI application
# uvicorn app.main:app --reload

import pathlib
from typing import Optional
from fastapi import FastAPI

from cassandra.cqlengine.management import sync_table

from . import (
    config,
    db,
    models,
    ml
)

app = FastAPI()
settings = config.get_settings()
SMSInference = models.SMSInference

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-metadata.json"

AI_MODEL = None
DB_SESSION = None

@app.on_event("startup")
def on_startup():
    """Startup event handler
    """
    global AI_MODEL, DB_SESSION
    AI_MODEL = ml.AIModel(
        model_path=MODEL_PATH,
        tokenizer_path=TOKENIZER_PATH,
        metadata_path=METADATA_PATH
    )
    DB_SESSION = db.get_session()
    sync_table(SMSInference)

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
    top = preds_dict["top"] # {label:, confidence}
    data = {"query": query, **top}
    obj = SMSInference.objects.create(**data)# NoSQL -> cassandra -> Datastax AstraDB
    return obj

@app.get("/inference/{my_uuid}")
def read_inference(my_uuid):
    obj = SMSInference.objects.get(uuid=my_uuid)
    return obj

# Paginate (a list of inferences) a Cassandra Model as a FastAPI streaming response
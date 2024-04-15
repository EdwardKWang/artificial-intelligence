# This is the main module for the FastAPI application
# uvicorn app.main:app --reload
# ngrok http 8000

import pathlib
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from cassandra.query import SimpleStatement
from cassandra.cqlengine.management import sync_table

from . import (
    config,
    db,
    models,
    ml,
    schema
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

@app.get("/")
def read_index(q:Optional[str] = None):
    return {"Hello": "World"}

@app.post("/")
def create_inference(query:schema.Query):
    """_summary_

    :param q: _description_, defaults to None
    :type q: Optional[str], optional
    :return: _description_
    :rtype: _type_
    """
    global AI_MODEL
    preds_dict = AI_MODEL.predict_text(query.q)
    top = preds_dict["top"] # {label:, confidence}
    data = {"query": query.q, **top}
    obj = SMSInference.objects.create(**data)# NoSQL -> cassandra -> Datastax AstraDB
    return obj

@app.get("/inference/{my_uuid}")
def read_inference(my_uuid):
    obj = SMSInference.objects.get(uuid=my_uuid)
    return obj

@app.get("/inferences")
def list_inferences():
    q = SMSInference.objects.all()
    #print(q)
    return list(q)

def fetch_rows(
        stmt:SimpleStatement, 
        fetch_size:int=25, 
        session=None):
    stmt.fetch_size = fetch_size
    result_set = session.execute(stmt)
    #has_pages = result_set.has_more_pages
    has_pages = True
    yield "uuid,label,confidence,query,version\n"
    while has_pages:
        for row in result_set.current_rows:
            yield f"{row['uuid']},{row['label']},{row['confidence']},{row['query']},{row['model_version']}\n"
        #result_set.fetch_next_page()
        has_pages = result_set.has_more_pages
        result_set = session.execute(stmt, paging_state=result_set.paging_state)

@app.get("/dataset")
def export_inferences():
    global DB_SESSION
    cql_query = "SELECT * FROM spam_inferences.smsinference LIMIT 10000"
    statement = SimpleStatement(cql_query)
    # rows = DB_SESSION.execute(cql_query)
    return StreamingResponse(fetch_rows(statement,25,DB_SESSION))
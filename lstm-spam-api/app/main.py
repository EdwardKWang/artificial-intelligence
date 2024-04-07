"""_summary_

:return: _description_
:rtype: _type_
"""

# uvicorn app.main:app --reload

import pathlib
from typing import Optional
from fastapi import FastAPI
from tensorflow.keras.models import load_model

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-metadata.json"

AI_MODEL = None

@app.on_event("startup")
def on_startup():
    global AI_MODEL
    if MODEL_PATH.exists():
        AI_MODEL = load_model(MODEL_PATH)

        print("Model loaded successfully")

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
    # predict(query)
    print(AI_MODEL)
    return {"query": query}

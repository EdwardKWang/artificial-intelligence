"""_summary_

:return: _description_
:rtype: _type_
"""

import pathlib
from typing import Optional
from fastapi import FastAPI

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-metadata.json"


@app.get("/") # /?q=this is awesome
def read_index(q:Optional[str] = None):
    """_summary_

    :param q: _description_, defaults to None
    :type q: Optional[str], optional
    :return: _description_
    :rtype: _type_
    """
    query = q or "Hello World"
    # predict(query)
    return {"query": query}

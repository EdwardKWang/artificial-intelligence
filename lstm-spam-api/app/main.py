"""_summary_

:return: _description_
:rtype: _type_
"""

# uvicorn app.main:app --reload

import pathlib
import json
import numpy as np
from typing import Optional
from fastapi import FastAPI
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

app = FastAPI()

BASE_DIR = pathlib.Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR.parent / "models"
SMS_SPAM_MODEL_DIR = MODEL_DIR / "spam-sms"
MODEL_PATH = SMS_SPAM_MODEL_DIR / "spam-model.h5"
TOKENIZER_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-tokenizer.json"
METADATA_PATH = SMS_SPAM_MODEL_DIR / "spam-classifier-metadata.json"

AI_MODEL = None
AI_TOKENIZER = None
MODEL_METADATA = {}
labels_legend_inverted = {}

class NumpyEncoder(json.JSONEncoder):
    """Encoder to handle integer, float and numpy array types

    :param json: object to encode
    :type json: json object
    """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

@app.on_event("startup")
def on_startup():
    """startup event handler
    """
    global AI_MODEL, AI_TOKENIZER, MODEL_METADATA, labels_legend_inverted
    # load model
    if MODEL_PATH.exists():
        AI_MODEL = load_model(MODEL_PATH)
    # load tokenizer
    if TOKENIZER_PATH.exists():
        with open(TOKENIZER_PATH, "r") as f:
            AI_TOKENIZER = tokenizer_from_json(f.read())
    # load metadata
    if METADATA_PATH.exists():
        with open(METADATA_PATH, "r") as f:
            MODEL_METADATA = json.load(f)
            labels_legend_inverted = MODEL_METADATA["labels_legend_inverted"]

def predict(query:str):
    sequences = AI_TOKENIZER.texts_to_sequences([query])
    maxlen = MODEL_METADATA.get("max_sequence") or 280
    x_input = pad_sequences(sequences, maxlen=maxlen)
    preds_array = AI_MODEL.predict(x_input)
    preds = preds_array[0]
    top_idx_val = np.argmax(preds)
    top_pred = {"label": labels_legend_inverted[str(top_idx_val)],
                "confidence": preds[top_idx_val]}
    labeled_preds = [{"label": labels_legend_inverted[str(i)],
                      "confidence": x} for i , x in enumerate(list(preds))]
    return json.loads(json.dumps({"top": top_pred, "predictions": labeled_preds}, cls=NumpyEncoder))

@app.get("/") # /?q=this is awesome
def read_index(q:Optional[str] = None):
    """_summary_

    :param q: _description_, defaults to None
    :type q: Optional[str], optional
    :return: _description_
    :rtype: _type_
    """
    global AI_MODEL, MODEL_METADATA, labels_legend_inverted
    query = q or "Hello World"
    preds_dict = predict(query)
    return {"query": query, "results":preds_dict}

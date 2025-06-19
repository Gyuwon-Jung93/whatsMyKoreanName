"""TFLite Dual Encoder 추론 유틸리티"""
import os, numpy as np, heapq
import tflite_runtime.interpreter as tflite
from .train_dual_encoder import pad, encode, en_charset, ko_charset, MAX_LEN_EN, MAX_LEN_KO
from sqlalchemy.orm import Session
from db import SessionLocal
from models import NameTrend

MODEL_PATH = os.getenv("MODEL_TFLITE", "models/dual_encoder.tflite")

interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

input_en_idx = interpreter.get_input_details()[0]["index"]
input_ko_idx = interpreter.get_input_details()[1]["index"]
output_idx = interpreter.get_output_details()[0]["index"]

# Preload korean embeddings
print("[INFO] caching korean embeddings...")
with SessionLocal() as db:
    all_kos = db.query(NameTrend).all()

ko_vecs = []
ko_entries = []
for row in all_kos:
    vec = pad(encode(row.korean_name, ko_charset, MAX_LEN_KO), MAX_LEN_KO)
    ko_vecs.append(vec)
    ko_entries.append(row)
ko_vecs = np.array(ko_vecs, dtype=np.int32)

# Encode korean names once
embeddings_ko = []
for vec in ko_vecs:
    interpreter.set_tensor(input_en_idx, np.zeros((1, MAX_LEN_EN), np.int32))
    interpreter.set_tensor(input_ko_idx, vec.reshape(1, -1))
    interpreter.invoke()
    embeddings_ko.append(interpreter.get_tensor(output_idx)[0])
embeddings_ko = np.vstack(embeddings_ko)


def recommend(english_name: str, k: int = 3):
    en_vec = np.array([pad(encode(english_name.lower(), en_charset, MAX_LEN_EN), MAX_LEN_EN)], dtype=np.int32)
    # compute english embedding
    interpreter.set_tensor(input_en_idx, en_vec)
    interpreter.set_tensor(input_ko_idx, np.zeros((1, MAX_LEN_KO), np.int32))
    interpreter.invoke()
    emb_en = interpreter.get_tensor(output_idx)[0]

    sims = embeddings_ko @ emb_en  # cosine since normalized
    top_idx = heapq.nlargest(k, range(len(sims)), sims.take)
    results = []
    for i in top_idx:
        row = ko_entries[i]
        results.append({
            "koreanName": row.korean_name,
            "meaning": row.meaning,
            "eraScore": round(float(row.trend_score), 2),
            "gender": row.gender,
        })
    return results 
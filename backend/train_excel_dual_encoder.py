"""Excel 폴더(KoreaData, UKData)의 boys/girls 하위 엑셀을 합쳐 Dual-Encoder 학습

폴더 구조 예시
KoreaData/
  boys/kor_boys.xlsx
  girls/kor_girls.xls
UKData/
  boys/uk_boys.xlsx
  girls/uk_girls.xlsx

각 파일은 열 이름에 상관없이  두 컬럼만 사용:
  영어이름 | 한국어이름
(추가 열이 있어도 무시)
"""
import os, glob, re
import pandas as pd
from train_dual_encoder import (
    build_charset, encode, pad, MAX_LEN_EN, MAX_LEN_KO, EMB_DIM, BATCH_SIZE, EPOCHS, MODEL_DIR
)  # 재사용
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
from sklearn.model_selection import train_test_split

BASE_DIRS = ["KoreaData", "UKData"]
PATTERN = re.compile(r"(Korea|UK).*?/(boys|girls)/", re.IGNORECASE)

def load_data():
    records = []
    for base in BASE_DIRS:
        for path in glob.glob(os.path.join(base, "**/*.xls*"), recursive=True):
            m = PATTERN.search(path)
            if not m:
                continue
            region = m.group(1).lower()
            gender = m.group(2).lower()
            df = pd.read_excel(path, engine="openpyxl" if path.endswith("x") else None)
            # 영어,한국어 컬럼 추정
            if df.shape[1] < 2:
                continue
            en_col, ko_col = df.columns[:2]
            for en, ko in zip(df[en_col], df[ko_col]):
                if pd.isna(en) or pd.isna(ko):
                    continue
                records.append({
                    "english_name": str(en).strip(),
                    "korean_name": str(ko).strip(),
                    "gender": gender,
                    "region": region,
                })
    return pd.DataFrame(records)

df = load_data()
print(f"[INFO] loaded {len(df)} name pairs")

# --- charset 생성 (재사용) ---
en_charset = build_charset(df["english_name"].str.lower())
ko_charset = build_charset(df["korean_name"])

PAD_ID, UNK_ID = 0, 1

en_vecs = np.array([pad(encode(n.lower(), en_charset, MAX_LEN_EN), MAX_LEN_EN) for n in df["english_name"]])
ko_vecs = np.array([pad(encode(n, ko_charset, MAX_LEN_KO), MAX_LEN_KO) for n in df["korean_name"]])

X_train_en, X_val_en, X_train_ko, X_val_ko = train_test_split(en_vecs, ko_vecs, test_size=0.1, random_state=42)
train_ds = tf.data.Dataset.from_tensor_slices((X_train_en, X_train_ko)).batch(BATCH_SIZE).prefetch(2)
val_ds = tf.data.Dataset.from_tensor_slices((X_val_en, X_val_ko)).batch(BATCH_SIZE).prefetch(2)

# --- 모델 정의 (dual encoder) ---

def build_encoder(vocab_size, max_len):
    inp = layers.Input(shape=(max_len,), dtype="int32")
    x = layers.Embedding(vocab_size, EMB_DIM, mask_zero=True)(inp)
    x = layers.Bidirectional(layers.GRU(128))(x)
    x = layers.Dense(EMB_DIM)(x)
    x = layers.Lambda(lambda t: tf.math.l2_normalize(t, axis=1))(x)
    return models.Model(inp, x)

enc_en = build_encoder(len(en_charset)+2, MAX_LEN_EN)
enc_ko = build_encoder(len(ko_charset)+2, MAX_LEN_KO)

in_en = layers.Input(shape=(MAX_LEN_EN,), dtype="int32")
in_ko = layers.Input(shape=(MAX_LEN_KO,), dtype="int32")
emb_en = enc_en(in_en)
emb_ko = enc_ko(in_ko)
cos = layers.Dot(axes=1, normalize=True)([emb_en, emb_ko])
model = models.Model([in_en, in_ko], cos)
margin = 0.2
model.compile(optimizer="adam", loss=lambda y_true, y_pred: tf.reduce_mean(tf.maximum(0.0, margin - y_pred)))

print("[INFO] training...")
model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, verbose=1)

os.makedirs(MODEL_DIR, exist_ok=True)
keras_path = os.path.join(MODEL_DIR, "dual_encoder_excel.keras")
model.save(keras_path)
print("[INFO] saved", keras_path)

# TFLite convert
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
open(os.path.join(MODEL_DIR, "dual_encoder_excel.tflite"), "wb").write(converter.convert())
print("[DONE] exported models/dual_encoder_excel.tflite") 
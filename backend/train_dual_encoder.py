"""Dual-Encoder 모델 학습 스크립트
데이터 CSV: data/names_dataset.csv (cols: english_name,korean_name,gender,year,meaning)
출력: models/dual_encoder.tflite
"""
import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras import layers, models

DATA_PATH = os.getenv("DATA_CSV", "data/names_dataset.csv")
MODEL_DIR = "models"
EMB_DIM = 64
MAX_LEN_EN = 15  # 영어 이름 최대 글자수
MAX_LEN_KO = 4   # 한글 이름 최대 글자수(2~3자 + 여분)
BATCH_SIZE = 256
EPOCHS = 15

os.makedirs(MODEL_DIR, exist_ok=True)

# -------------------------------------------------
# 1. 데이터 로드 & 전처리
# -------------------------------------------------
print("[INFO] loading data...")
df = pd.read_csv(DATA_PATH)

def build_charset(series):
    chars = set()
    for text in series:
        chars.update(list(str(text)))
    return {c: i + 2 for i, c in enumerate(sorted(chars))}  # 0: pad, 1: unk

en_charset = build_charset(df["english_name"].str.lower())
ko_charset = build_charset(df["korean_name"])

PAD_ID, UNK_ID = 0, 1

def encode(text, charset, max_len):
    return [charset.get(ch, UNK_ID) for ch in list(str(text))[:max_len]]

def pad(seq, max_len):
    return seq + [PAD_ID] * (max_len - len(seq))

en_vecs = np.array([pad(encode(name.lower(), en_charset, MAX_LEN_EN), MAX_LEN_EN) for name in df["english_name"]])
ko_vecs = np.array([pad(encode(name, ko_charset, MAX_LEN_KO), MAX_LEN_KO) for name in df["korean_name"]])

# -------------------------------------------------
# 2. 학습 / 검증 분리
# -------------------------------------------------
X_train_en, X_val_en, X_train_ko, X_val_ko = train_test_split(en_vecs, ko_vecs, test_size=0.1, random_state=42)

train_ds = tf.data.Dataset.from_tensor_slices((X_train_en, X_train_ko)).batch(BATCH_SIZE).prefetch(2)
val_ds = tf.data.Dataset.from_tensor_slices((X_val_en, X_val_ko)).batch(BATCH_SIZE).prefetch(2)

# -------------------------------------------------
# 3. Dual Encoder 모델 정의
# -------------------------------------------------
print("[INFO] building model...")

def build_encoder(vocab_size, max_len):
    inp = layers.Input(shape=(max_len,), dtype="int32")
    x = layers.Embedding(vocab_size, EMB_DIM, mask_zero=True)(inp)
    x = layers.Bidirectional(layers.GRU(128))(x)
    x = layers.Dense(EMB_DIM)(x)
    x = layers.Lambda(lambda t: tf.math.l2_normalize(t, axis=1))(x)
    return models.Model(inp, x)

en_vocab = len(en_charset) + 2
ko_vocab = len(ko_charset) + 2

enc_eng = build_encoder(en_vocab, MAX_LEN_EN)
enc_kor = build_encoder(ko_vocab, MAX_LEN_KO)

eng_in = layers.Input(shape=(MAX_LEN_EN,), dtype="int32")
kor_in = layers.Input(shape=(MAX_LEN_KO,), dtype="int32")

emb_en = enc_eng(eng_in)
emb_ko = enc_kor(kor_in)

# cosine similarity * -1 => 거리, 학습 시 margin contrastive loss 사용
sim = layers.Dot(axes=1, normalize=True)([emb_en, emb_ko])
model = models.Model([eng_in, kor_in], sim)

margin = 0.2

def contrastive_loss(y_true, y_pred):
    # y_true: 1 for positive pair, 0 for negative (we'll use 1 always and rely on in-batch negatives)
    y_true = tf.squeeze(y_true, axis=1)
    pos_loss = tf.maximum(0.0, margin - y_pred)
    return tf.reduce_mean(pos_loss)

model.compile(optimizer="adam", loss=contrastive_loss)

# -------------------------------------------------
# 4. 학습 (in-batch 긍/부정 샘플 방식)
# -------------------------------------------------
print("[INFO] training...")

def make_labels(batch):
    return tf.ones((batch, 1), dtype=tf.float32)

model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, steps_per_epoch=len(train_ds), verbose=1)

# -------------------------------------------------
# 5. 모델 저장 & TFLite 변환
# -------------------------------------------------
print("[INFO] saving keras model...")
keras_path = os.path.join(MODEL_DIR, "dual_encoder.keras")
model.save(keras_path)

print("[INFO] converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
open(os.path.join(MODEL_DIR, "dual_encoder.tflite"), "wb").write(tflite_model)

print("[DONE] model exported to models/dual_encoder.tflite") 
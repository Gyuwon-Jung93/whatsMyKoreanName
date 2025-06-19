from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sentry_sdk
from name_logic import recommend_korean_names
from models import NameHistory
from db import SessionLocal, Base, engine
import models  # noqa: F401  # 모델을 메타데이터에 등록하기 위함

# Sentry 초기화
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)

app = Flask(__name__)
CORS(app)

# DB 초기화 (before_first_request 대신 수동 호출)
def init_db():
    Base.metadata.create_all(bind=engine)

# 초기화 실행
init_db()

@app.route("/")
def health_check():
    return {"status": "ok"}, 200

@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    if not name:
        return {"error": "Name is required"}, 400

    candidates = recommend_korean_names(name, k=3)
    # /api/recommend 는 이전 호환성을 위해 첫 번째 후보만 반환
    return jsonify(candidates[0])

# 신규 API: 여러 후보 반환
@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json(force=True)
    english_name = data.get("englishName") or data.get("name")
    if not english_name or not english_name.strip():
        return {"error": "englishName is required"}, 400

    candidates = recommend_korean_names(english_name.strip(), k=3)
    return jsonify({"candidates": candidates})

# helper
def get_user_id(req):
    """간단한 방식: 헤더 X-User-Id 를 사용하고 없으면 None"""
    return req.headers.get("X-User-Id")

# 저장 API
@app.route("/api/history/save", methods=["POST"])
def save_name():
    data = request.get_json(force=True)
    english = data.get("englishName") or data.get("english_name")
    korean = data.get("koreanName") or data.get("korean_name")
    if not english or not korean:
        return {"error": "englishName and koreanName are required"}, 400

    user_id = get_user_id(request)
    with SessionLocal() as db:
        record = NameHistory(user_id=user_id, english_name=english.strip(), korean_name=korean.strip())
        db.add(record)
        db.commit()
        db.refresh(record)
        return jsonify({"id": record.id, "savedAt": record.saved_at.isoformat()})

# 조회 API
@app.route("/api/history", methods=["GET"])
def list_history():
    user_id = get_user_id(request)
    with SessionLocal() as db:
        q = db.query(NameHistory)
        if user_id:
            q = q.filter(NameHistory.user_id == user_id)
        records = q.order_by(NameHistory.saved_at.desc()).limit(100).all()
        return jsonify([
            {
                "id": r.id,
                "englishName": r.english_name,
                "koreanName": r.korean_name,
                "savedAt": r.saved_at.isoformat(),
            }
            for r in records
        ])

# 삭제 API
@app.route("/api/history/<int:hist_id>", methods=["DELETE"])
def delete_history(hist_id):
    user_id = get_user_id(request)
    with SessionLocal() as db:
        rec = db.query(NameHistory).filter(NameHistory.id == hist_id)
        if user_id:
            rec = rec.filter(NameHistory.user_id == user_id)
        obj = rec.first()
        if not obj:
            return {"error": "Not found"}, 404
        db.delete(obj)
        db.commit()
        return {"status": "deleted"}, 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="::", port=port)
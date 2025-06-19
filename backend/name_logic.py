"""간단한 규칙 기반 한국어 이름 추천 로직 (MVP)"""
import random
import hashlib
from typing import List, Dict

CANDIDATE_NAMES = [
    "하린",
    "지훈",
    "민준",
    "서연",
    "현우",
    "지민",
    "수민",
    "다은",
    "예준",
    "가은",
    "지아",
    "윤우",
    "시은",
]

CANDIDATE_MEANINGS = [
    "하늘같이 맑고 밝은",
    "지혜롭고 빛나는",
    "백성을 이끄는 지도자",
    "서로를 연모하는 마음",
    "현명하고 우아한",
    "지속되는 아름다움",
    "수려하고 민첩한",
    "모든 이에게 은혜로움",
    "예의 바르고 준수한",
]


def _hash_to_float(value: str) -> float:
    """영어 이름에 기반해 0~1 사이 값을 생성한다."""
    h = hashlib.sha256(value.encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def recommend_korean_names(english_name: str, k: int = 3) -> List[Dict]:
    """영어 이름을 기반으로 k개의 한국어 이름 후보를 반환한다."""
    if not english_name:
        raise ValueError("english_name is required")

    # 이름에 따라 결정적인 랜덤 시드 설정 -> 같은 입력이면 같은 결과
    seed = int(hashlib.sha256(english_name.lower().encode()).hexdigest(), 16)
    rnd = random.Random(seed)

    names = rnd.sample(CANDIDATE_NAMES, k)
    results = []
    for name in names:
        meaning = rnd.choice(CANDIDATE_MEANINGS)
        era_score = round(_hash_to_float(name + english_name), 2)
        results.append({
            "koreanName": name,
            "meaning": meaning,
            "eraScore": era_score,
        })
    return results 
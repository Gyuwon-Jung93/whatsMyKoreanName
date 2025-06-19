"""SQLAlchemy ORM 모델 정의"""
from sqlalchemy import Column, Integer, String, Float, Index, DateTime, func

from db import Base

class NameTrend(Base):
    __tablename__ = "name_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    english_name = Column(String(30), nullable=False)
    korean_name = Column(String(20), nullable=False)
    gender = Column(String(10))  # male, female, unknown
    pronunciation = Column(String(50))
    year = Column(Integer, nullable=False)
    trend_score = Column(Float, nullable=False)
    meaning = Column(String(255))

    __table_args__ = (
        Index("idx_english_name", "english_name"),
        Index("idx_year", "year"),
        Index("idx_english_year", "english_name", "year"),
    )

class NameHistory(Base):
    """사용자가 저장한 이름 히스토리"""

    __tablename__ = "name_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(128), nullable=True)  # 비로그인 시 null, 로그인 사용자는 식별자 저장(암호화 필요)
    english_name = Column(String(30), nullable=False)
    korean_name = Column(String(20), nullable=False)
    saved_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("idx_user_id", "user_id"),
    ) 
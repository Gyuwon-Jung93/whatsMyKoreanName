"""DB 엔진, 세션, Base 선언 모듈"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 기본값은 SQLite, 환경변수 DATABASE_URL 이 있으면 우선 사용
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./korean_name.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base() 
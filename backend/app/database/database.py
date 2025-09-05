"""데이터베이스 연결 및 설정 모듈

PostgreSQL 데이터베이스 연결을 관리하고 SQLAlchemy 세션을 제공합니다.
"""

import os
from typing import Generator
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 로깅 설정
logger = logging.getLogger(__name__)

# 환경변수에서 데이터베이스 설정 읽기
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:safe70%21%21@localhost:5432/skybootcore?client_encoding=utf8"
)

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 메타데이터 설정
metadata = MetaData(schema="skybootcore")
Base.metadata = metadata


def get_db() -> Generator[Session, None, None]:
    """데이터베이스 세션을 생성하고 반환합니다.
    
    FastAPI의 Depends와 함께 사용하여 의존성 주입을 통해
    데이터베이스 세션을 제공합니다.
    
    Yields:
        Session: SQLAlchemy 데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 오류: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_database():
    """데이터베이스 테이블을 생성합니다.
    
    database.sql 파일의 스키마를 기반으로 테이블을 생성합니다.
    """
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 테이블 생성 실패: {e}")
        raise


def drop_database():
    """모든 데이터베이스 테이블을 삭제합니다.
    
    주의: 이 함수는 모든 데이터를 삭제합니다.
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("데이터베이스 테이블이 성공적으로 삭제되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 테이블 삭제 실패: {e}")
        raise


def check_database_connection() -> bool:
    """데이터베이스 연결 상태를 확인합니다.
    
    Returns:
        bool: 연결 성공 시 True, 실패 시 False
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        logger.info("데이터베이스 연결이 성공적으로 확인되었습니다.")
        return True
    except Exception as e:
        logger.error(f"데이터베이스 연결 실패: {e}")
        return False
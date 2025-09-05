"""데이터베이스 마이그레이션 관리 모듈

Alembic을 사용한 데이터베이스 스키마 버전 관리를 담당합니다.
"""

import os
import logging
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect
from .database import engine, Base

# 로깅 설정
logger = logging.getLogger(__name__)


def get_alembic_config():
    """Alembic 설정을 반환합니다.
    
    Returns:
        Config: Alembic 설정 객체
    """
    # alembic.ini 파일 경로
    alembic_cfg_path = os.path.join(os.path.dirname(__file__), '..', '..', 'alembic.ini')
    
    if not os.path.exists(alembic_cfg_path):
        raise FileNotFoundError(f"Alembic 설정 파일을 찾을 수 없습니다: {alembic_cfg_path}")
    
    alembic_cfg = Config(alembic_cfg_path)
    return alembic_cfg


def init_alembic():
    """Alembic 초기화
    
    마이그레이션 환경을 초기화합니다.
    """
    try:
        alembic_cfg = get_alembic_config()
        command.init(alembic_cfg, "migrations")
        logger.info("Alembic이 성공적으로 초기화되었습니다.")
    except Exception as e:
        logger.error(f"Alembic 초기화 실패: {e}")
        raise


def create_migration(message: str):
    """새로운 마이그레이션 파일을 생성합니다.
    
    Args:
        message (str): 마이그레이션 메시지
    """
    try:
        alembic_cfg = get_alembic_config()
        command.revision(alembic_cfg, autogenerate=True, message=message)
        logger.info(f"마이그레이션 파일이 생성되었습니다: {message}")
    except Exception as e:
        logger.error(f"마이그레이션 파일 생성 실패: {e}")
        raise


def upgrade_database(revision: str = "head"):
    """데이터베이스를 지정된 리비전으로 업그레이드합니다.
    
    Args:
        revision (str): 업그레이드할 리비전 (기본값: "head")
    """
    try:
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, revision)
        logger.info(f"데이터베이스가 {revision} 리비전으로 업그레이드되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 업그레이드 실패: {e}")
        raise


def downgrade_database(revision: str):
    """데이터베이스를 지정된 리비전으로 다운그레이드합니다.
    
    Args:
        revision (str): 다운그레이드할 리비전
    """
    try:
        alembic_cfg = get_alembic_config()
        command.downgrade(alembic_cfg, revision)
        logger.info(f"데이터베이스가 {revision} 리비전으로 다운그레이드되었습니다.")
    except Exception as e:
        logger.error(f"데이터베이스 다운그레이드 실패: {e}")
        raise


def get_current_revision():
    """현재 데이터베이스의 리비전을 반환합니다.
    
    Returns:
        str: 현재 리비전
    """
    try:
        from alembic.runtime.migration import MigrationContext
        
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            return context.get_current_revision()
                
    except Exception as e:
        logger.error(f"현재 리비전 조회 실패: {e}")
        return None


def get_migration_history():
    """마이그레이션 히스토리를 반환합니다.
    
    Returns:
        list: 마이그레이션 히스토리
    """
    try:
        alembic_cfg = get_alembic_config()
        return command.history(alembic_cfg)
    except Exception as e:
        logger.error(f"마이그레이션 히스토리 조회 실패: {e}")
        raise


def check_database_schema():
    """데이터베이스 스키마 상태를 확인합니다.
    
    Returns:
        dict: 스키마 상태 정보
    """
    try:
        inspector = inspect(engine)
        
        # 스키마 존재 확인
        schemas = inspector.get_schema_names()
        skybootcore_exists = 'skybootcore' in schemas
        
        # 테이블 목록 조회
        tables = []
        if skybootcore_exists:
            tables = inspector.get_table_names(schema='skybootcore')
        
        schema_info = {
            'schema_exists': skybootcore_exists,
            'tables': tables,
            'table_count': len(tables)
        }
        
        logger.info(f"스키마 상태: {schema_info}")
        return schema_info
        
    except Exception as e:
        logger.error(f"스키마 상태 확인 실패: {e}")
        raise


def validate_migration():
    """마이그레이션 상태를 검증합니다.
    
    Returns:
        bool: 검증 성공 여부
    """
    try:
        # 현재 리비전 확인
        current_rev = get_current_revision()
        
        # 스키마 상태 확인
        schema_info = check_database_schema()
        
        # 모델과 실제 테이블 비교 (스키마명 제거)
        expected_tables = [table.split('.')[-1] for table in Base.metadata.tables.keys()]
        actual_tables = schema_info['tables']
        
        missing_tables = set(expected_tables) - set(actual_tables)
        extra_tables = set(actual_tables) - set(expected_tables)
        
        if missing_tables:
            logger.warning(f"누락된 테이블: {missing_tables}")
        
        if extra_tables:
            logger.warning(f"추가 테이블: {extra_tables}")
        
        is_valid = len(missing_tables) == 0
        
        logger.info(f"마이그레이션 검증 결과: {'성공' if is_valid else '실패'}")
        return is_valid
        
    except Exception as e:
        logger.error(f"마이그레이션 검증 실패: {e}")
        return False


if __name__ == "__main__":
    # 스키마 상태 확인
    check_database_schema()
    
    # 마이그레이션 검증
    validate_migration()
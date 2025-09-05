#!/usr/bin/env python3
"""데이터베이스 관리 스크립트

데이터베이스 초기화, 마이그레이션, 백업 등의 작업을 수행합니다.
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.append(str(Path(__file__).parent))

from app.database.database import (
    create_database, drop_database, check_database_connection,
    engine, get_db
)
from app.database.init_db import initialize_database
from app.database.migration import (
    init_alembic, create_migration, upgrade_database,
    downgrade_database, get_current_revision,
    check_database_schema, validate_migration
)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """데이터베이스 초기화"""
    try:
        logger.info("데이터베이스 연결 확인 중...")
        if not check_database_connection():
            logger.error("데이터베이스 연결 실패")
            return False
        
        logger.info("데이터베이스 초기화 시작...")
        initialize_database()
        logger.info("데이터베이스 초기화 완료")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        return False


def reset_database():
    """데이터베이스 리셋 (모든 테이블 삭제 후 재생성)"""
    try:
        logger.info("데이터베이스 리셋 시작...")
        
        # 모든 테이블 삭제
        logger.info("기존 테이블 삭제 중...")
        drop_database()
        
        # 테이블 재생성 및 초기 데이터 삽입
        logger.info("테이블 재생성 및 초기 데이터 삽입 중...")
        initialize_database()
        
        logger.info("데이터베이스 리셋 완료")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 리셋 실패: {e}")
        return False


def setup_migration():
    """마이그레이션 환경 설정"""
    try:
        logger.info("마이그레이션 환경 설정 시작...")
        init_alembic()
        logger.info("마이그레이션 환경 설정 완료")
        return True
        
    except Exception as e:
        logger.error(f"마이그레이션 환경 설정 실패: {e}")
        return False


def create_new_migration(message: str):
    """새로운 마이그레이션 생성"""
    try:
        logger.info(f"마이그레이션 생성 시작: {message}")
        create_migration(message)
        logger.info("마이그레이션 생성 완료")
        return True
        
    except Exception as e:
        logger.error(f"마이그레이션 생성 실패: {e}")
        return False


def upgrade_db(revision: str = "head"):
    """데이터베이스 업그레이드"""
    try:
        logger.info(f"데이터베이스 업그레이드 시작: {revision}")
        upgrade_database(revision)
        logger.info("데이터베이스 업그레이드 완료")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 업그레이드 실패: {e}")
        return False


def downgrade_db(revision: str):
    """데이터베이스 다운그레이드"""
    try:
        logger.info(f"데이터베이스 다운그레이드 시작: {revision}")
        downgrade_database(revision)
        logger.info("데이터베이스 다운그레이드 완료")
        return True
        
    except Exception as e:
        logger.error(f"데이터베이스 다운그레이드 실패: {e}")
        return False


def show_status():
    """데이터베이스 상태 표시"""
    try:
        logger.info("데이터베이스 상태 확인 중...")
        
        # 연결 상태 확인
        connection_ok = check_database_connection()
        print(f"데이터베이스 연결: {'성공' if connection_ok else '실패'}")
        
        if not connection_ok:
            return False
        
        # 스키마 상태 확인
        schema_info = check_database_schema()
        print(f"스키마 존재: {'예' if schema_info['schema_exists'] else '아니오'}")
        print(f"테이블 수: {schema_info['table_count']}")
        print(f"테이블 목록: {', '.join(schema_info['tables'])}")
        
        # 현재 마이그레이션 리비전
        try:
            current_rev = get_current_revision()
            print(f"현재 마이그레이션 리비전: {current_rev}")
        except:
            print("현재 마이그레이션 리비전: 없음 (마이그레이션 미설정)")
        
        # 마이그레이션 검증
        is_valid = validate_migration()
        print(f"마이그레이션 상태: {'정상' if is_valid else '비정상'}")
        
        return True
        
    except Exception as e:
        logger.error(f"상태 확인 실패: {e}")
        return False


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='데이터베이스 관리 스크립트')
    subparsers = parser.add_subparsers(dest='command', help='사용 가능한 명령어')
    
    # init 명령어
    subparsers.add_parser('init', help='데이터베이스 초기화')
    
    # reset 명령어
    subparsers.add_parser('reset', help='데이터베이스 리셋')
    
    # migration 관련 명령어
    migration_parser = subparsers.add_parser('migration', help='마이그레이션 관리')
    migration_subparsers = migration_parser.add_subparsers(dest='migration_command')
    
    migration_subparsers.add_parser('setup', help='마이그레이션 환경 설정')
    
    create_parser = migration_subparsers.add_parser('create', help='새 마이그레이션 생성')
    create_parser.add_argument('message', help='마이그레이션 메시지')
    
    upgrade_parser = migration_subparsers.add_parser('upgrade', help='데이터베이스 업그레이드')
    upgrade_parser.add_argument('--revision', default='head', help='업그레이드할 리비전')
    
    downgrade_parser = migration_subparsers.add_parser('downgrade', help='데이터베이스 다운그레이드')
    downgrade_parser.add_argument('revision', help='다운그레이드할 리비전')
    
    # status 명령어
    subparsers.add_parser('status', help='데이터베이스 상태 확인')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    success = False
    
    if args.command == 'init':
        success = init_database()
    elif args.command == 'reset':
        success = reset_database()
    elif args.command == 'migration':
        if args.migration_command == 'setup':
            success = setup_migration()
        elif args.migration_command == 'create':
            success = create_new_migration(args.message)
        elif args.migration_command == 'upgrade':
            success = upgrade_db(args.revision)
        elif args.migration_command == 'downgrade':
            success = downgrade_db(args.revision)
        else:
            migration_parser.print_help()
    elif args.command == 'status':
        success = show_status()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
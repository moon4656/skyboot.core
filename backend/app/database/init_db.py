"""데이터베이스 초기화 스크립트

데이터베이스 테이블 생성 및 초기 데이터 설정을 담당합니다.
"""

import os
import logging
from datetime import datetime
from sqlalchemy import text
from .database import engine, SessionLocal, Base, check_database_connection
from ..models import *  # 모든 모델 임포트

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_schema():
    """스키마 생성
    
    skybootcore 스키마가 존재하지 않으면 생성합니다.
    """
    try:
        with engine.connect() as connection:
            # 스키마 존재 확인
            result = connection.execute(
                text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'skybootcore'")
            )
            if not result.fetchone():
                # 스키마 생성
                connection.execute(text("CREATE SCHEMA skybootcore"))
                connection.commit()
                logger.info("skybootcore 스키마가 생성되었습니다.")
            else:
                logger.info("skybootcore 스키마가 이미 존재합니다.")
    except Exception as e:
        logger.error(f"스키마 생성 실패: {e}")
        raise


def create_sequences():
    """시퀀스 생성
    
    필요한 시퀀스들을 생성합니다.
    """
    sequences = [
        "CREATE SEQUENCE IF NOT EXISTS skybootcore.tb_bbsmaster_seq START 1;",
    ]
    
    try:
        with engine.connect() as connection:
            for seq_sql in sequences:
                connection.execute(text(seq_sql))
            connection.commit()
            logger.info("시퀀스가 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"시퀀스 생성 실패: {e}")
        raise


def create_tables():
    """테이블 생성
    
    SQLAlchemy 모델을 기반으로 모든 테이블을 생성합니다.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("모든 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"테이블 생성 실패: {e}")
        raise


def insert_initial_data():
    """초기 데이터 삽입
    
    시스템 운영에 필요한 기본 데이터를 삽입합니다.
    """
    db = SessionLocal()
    try:
        # 공통코드 그룹 초기 데이터
        common_groups = [
            CmmnGrpCode(
                code_id="BBSTYP",
                code_id_nm="게시판유형",
                code_id_dc="게시판의 유형을 구분하는 코드",
                use_yn="Y",
                cl_code="BBS",
                frst_register_id="SYSTEM"
            ),
            CmmnGrpCode(
                code_id="AUTHOR",
                code_id_nm="권한유형",
                code_id_dc="시스템 권한 유형을 구분하는 코드",
                use_yn="Y",
                cl_code="AUTH",
                frst_register_id="SYSTEM"
            ),
            CmmnGrpCode(
                code_id="CONMTH",
                code_id_nm="접속방식",
                code_id_dc="시스템 접속 방식을 구분하는 코드",
                use_yn="Y",
                cl_code="LOG",
                frst_register_id="SYSTEM"
            )
        ]
        
        for group in common_groups:
            existing = db.query(CmmnGrpCode).filter_by(code_id=group.code_id).first()
            if not existing:
                db.add(group)
        
        # 공통상세코드 초기 데이터
        common_codes = [
            # 게시판유형
            CmmnCode(code_id="BBSTYP", code="NOTICE", code_nm="공지사항", code_dc="공지사항 게시판", use_yn="Y", code_ordr=1, frst_register_id="SYSTEM"),
            CmmnCode(code_id="BBSTYP", code="FREE", code_nm="자유게시판", code_dc="자유 게시판", use_yn="Y", code_ordr=2, frst_register_id="SYSTEM"),
            CmmnCode(code_id="BBSTYP", code="QNA", code_nm="질문답변", code_dc="질문답변 게시판", use_yn="Y", code_ordr=3, frst_register_id="SYSTEM"),
            
            # 권한유형
            CmmnCode(code_id="AUTHOR", code="ADMIN", code_nm="관리자", code_dc="시스템 관리자 권한", use_yn="Y", code_ordr=1, frst_register_id="SYSTEM"),
            CmmnCode(code_id="AUTHOR", code="USER", code_nm="일반사용자", code_dc="일반 사용자 권한", use_yn="Y", code_ordr=2, frst_register_id="SYSTEM"),
            CmmnCode(code_id="AUTHOR", code="GUEST", code_nm="게스트", code_dc="게스트 권한", use_yn="Y", code_ordr=3, frst_register_id="SYSTEM"),
            
            # 접속방식
            CmmnCode(code_id="CONMTH", code="WEB", code_nm="웹", code_dc="웹 브라우저 접속", use_yn="Y", code_ordr=1, frst_register_id="SYSTEM"),
            CmmnCode(code_id="CONMTH", code="API", code_nm="API", code_dc="API 접속", use_yn="Y", code_ordr=2, frst_register_id="SYSTEM"),
            CmmnCode(code_id="CONMTH", code="MOBILE", code_nm="모바일", code_dc="모바일 앱 접속", use_yn="Y", code_ordr=3, frst_register_id="SYSTEM")
        ]
        
        for code in common_codes:
            existing = db.query(CmmnCode).filter_by(code_id=code.code_id, code=code.code).first()
            if not existing:
                db.add(code)
        
        # 기본 권한 정보
        auth_infos = [
            AuthorInfo(
                author_code="ADMIN",
                author_nm="시스템관리자",
                author_dc="시스템 전체 관리 권한",
                author_creat_de=datetime.now(),
                frst_register_id="SYSTEM"
            ),
            AuthorInfo(
                author_code="USER",
                author_nm="일반사용자",
                author_dc="일반 사용자 권한",
                author_creat_de=datetime.now(),
                frst_register_id="SYSTEM"
            )
        ]
        
        for auth in auth_infos:
            existing = db.query(AuthorInfo).filter_by(author_code=auth.author_code).first()
            if not existing:
                db.add(auth)
        
        # 기본 메뉴 정보
        menu_infos = [
            MenuInfo(
                menu_no="1000000",
                menu_nm="시스템관리",
                progrm_file_nm="",
                upper_menu_no=None,
                menu_ordr=1,
                menu_dc="시스템 관리 메뉴",
                display_yn="Y",
                use_tag_yn="N",
                frst_register_id="SYSTEM"
            ),
            MenuInfo(
                menu_no="1010000",
                menu_nm="사용자관리",
                progrm_file_nm="/admin/users",
                upper_menu_no="1000000",
                menu_ordr=1,
                menu_dc="사용자 관리",
                display_yn="Y",
                use_tag_yn="N",
                frst_register_id="SYSTEM"
            ),
            MenuInfo(
                menu_no="1020000",
                menu_nm="권한관리",
                progrm_file_nm="/admin/auth",
                upper_menu_no="1000000",
                menu_ordr=2,
                menu_dc="권한 관리",
                display_yn="Y",
                use_tag_yn="N",
                frst_register_id="SYSTEM"
            ),
            MenuInfo(
                menu_no="1030000",
                menu_nm="메뉴관리",
                progrm_file_nm="/admin/menus",
                upper_menu_no="1000000",
                menu_ordr=3,
                menu_dc="메뉴 관리",
                display_yn="Y",
                use_tag_yn="N",
                frst_register_id="SYSTEM"
            )
        ]
        
        for menu in menu_infos:
            existing = db.query(MenuInfo).filter_by(menu_no=menu.menu_no).first()
            if not existing:
                db.add(menu)
        
        db.commit()
        logger.info("초기 데이터가 성공적으로 삽입되었습니다.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"초기 데이터 삽입 실패: {e}")
        raise
    finally:
        db.close()


def initialize_database():
    """데이터베이스 전체 초기화
    
    스키마, 시퀀스, 테이블 생성 및 초기 데이터 삽입을 수행합니다.
    """
    logger.info("데이터베이스 초기화를 시작합니다...")
    
    # 데이터베이스 연결 확인
    if not check_database_connection():
        raise Exception("데이터베이스 연결에 실패했습니다.")
    
    try:
        # 1. 스키마 생성
        create_schema()
        
        # 2. 시퀀스 생성
        create_sequences()
        
        # 3. 테이블 생성
        create_tables()
        
        # 4. 초기 데이터 삽입
        insert_initial_data()
        
        logger.info("데이터베이스 초기화가 완료되었습니다.")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise


if __name__ == "__main__":
    initialize_database()
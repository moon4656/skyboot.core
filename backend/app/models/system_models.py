"""시스템 관련 모델

시스템로그, 웹로그, 프로그램목록 등 시스템 관련 테이블의 SQLAlchemy 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Numeric, DateTime, Text, Index
from sqlalchemy.sql import func
from ..database.database import Base


class SysLog(Base):
    """시스템로그 테이블 모델
    
    시스템의 처리 로그와 오류 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_syslog"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '시스템로그'
    }
    
    # 기본 필드
    requst_id = Column(String(20), primary_key=True, comment="요청ID")
    job_se_code = Column(String(3), nullable=True, comment="업무구분코드")
    instt_code = Column(String(7), nullable=True, comment="기관코드")
    occrrnc_de = Column(DateTime, nullable=False, default=func.current_timestamp(), comment="발생일")
    rqester_ip = Column(String(23), nullable=True, comment="요청자IP")
    rqester_id = Column(String(20), nullable=True, comment="요청자ID")
    rqester_nm = Column(String(100), nullable=True, comment="요청자명")
    trget_menu_nm = Column(String(255), nullable=True, comment="대상메뉴명")
    svc_nm = Column(String(255), nullable=True, comment="서비스명")
    method_nm = Column(String(60), nullable=True, comment="메서드명")
    process_se_code = Column(String(3), nullable=True, comment="처리구분코드")
    process_co = Column(Numeric(10), nullable=True, comment="처리수")
    process_time = Column(String(14), nullable=True, comment="처리시간")
    process_cn = Column(Text, nullable=True, comment="처리내용")
    rspns_code = Column(String(3), nullable=True, comment="응답코드")
    error_se = Column(String(1), nullable=True, comment="오류구분")
    error_co = Column(Numeric(10), nullable=True, comment="오류수")
    error_code = Column(String(3), nullable=True, comment="오류코드")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=func.current_timestamp(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")


class WebLog(Base):
    """웹로그 테이블 모델
    
    웹 접속 로그와 URL 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_weblog"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '웹로그'
    }
    
    # 기본 필드
    requst_id = Column(String(20), primary_key=True, comment="요청ID")
    occrrnc_de = Column(DateTime, nullable=True, comment="발생일")
    url = Column(String(200), nullable=True, comment="URL")
    rqester_id = Column(String(20), nullable=True, comment="요청자ID")
    rqester_ip = Column(String(23), nullable=True, comment="요청자IP")
    rqester_nm = Column(String(60), nullable=True, comment="요청자명")
    trget_menu_nm = Column(String(60), nullable=True, comment="대상메뉴명")
    process_se_code = Column(String(20), nullable=True, comment="처리구분코드")
    process_cn = Column(String(2000), nullable=True, comment="처리내용")
    process_time = Column(Numeric(10, 3), nullable=True, comment="처리시간")
    rqest_de = Column(DateTime, nullable=True, comment="요청일자")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=func.current_date(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")


class ProgrmList(Base):
    """프로그램목록 테이블 모델
    
    시스템의 프로그램 정보와 URL 매핑을 관리하는 테이블입니다.
    """
    __tablename__ = "tb_progrmlist"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '프로그램목록'
    }
    
    # 기본 필드
    progrm_file_nm = Column(String(60), primary_key=True, comment="프로그램파일명")
    progrm_stre_path = Column(String(100), nullable=False, comment="프로그램저장경로")
    progrm_korean_nm = Column(String(60), nullable=True, comment="프로그램한글명")
    progrm_dc = Column(String(200), nullable=True, comment="프로그램설명")
    url = Column(String(100), nullable=False, comment="URL")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=func.current_timestamp(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
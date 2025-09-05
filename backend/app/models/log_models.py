"""로그 관련 SQLAlchemy 모델

접속로그 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer
from ..database.database import Base


class LoginLog(Base):
    """접속로그 테이블 모델
    
    사용자의 시스템 접속 로그를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_loginlog"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '접속로그'
    }
    
    # 기본 필드
    log_id = Column(String(20), primary_key=True, comment="로그ID")
    conect_id = Column(String(20), nullable=True, comment="접속ID")
    conect_ip = Column(String(23), nullable=True, comment="접속IP")
    conect_mthd = Column(String(4), nullable=True, comment="접속방식")
    error_occrrnc_at = Column(String(1), nullable=True, comment="오류발생여부")
    error_code = Column(String(3), nullable=True, comment="오류코드")

    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=True, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    def __repr__(self):
        return f"<LoginLog(log_id='{self.log_id}', conect_id='{self.conect_id}', conect_ip='{self.conect_ip}')>"


class APIUsageLog(Base):
    """API 사용 로그 테이블 모델
    
    모든 API 엔드포인트 호출 내역을 기록하는 테이블입니다.
    """
    __tablename__ = "tb_api_usage_log"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': 'API 사용 로그'
    }
    
    # 기본 필드
    log_id = Column(String(20), primary_key=True, comment="로그ID")
    user_id = Column(String(20), nullable=True, comment="사용자ID")
    endpoint = Column(String(200), nullable=False, comment="API 엔드포인트")
    method = Column(String(10), nullable=False, comment="HTTP 메서드")
    ip_address = Column(String(45), nullable=True, comment="클라이언트 IP 주소")
    user_agent = Column(Text, nullable=True, comment="사용자 에이전트")
    request_body = Column(Text, nullable=True, comment="요청 본문")
    response_status = Column(Integer, nullable=True, comment="응답 상태 코드")
    response_time_ms = Column(Integer, nullable=True, comment="응답 시간(밀리초)")
    error_message = Column(Text, nullable=True, comment="오류 메시지")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=True, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    def __repr__(self):
        return f"<APIUsageLog(log_id='{self.log_id}', endpoint='{self.endpoint}', method='{self.method}', user_id='{self.user_id}')>"
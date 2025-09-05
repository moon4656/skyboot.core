"""조직 관련 모델

조직 정보 관련 테이블의 SQLAlchemy 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.sql import func
from ..database.database import Base


class Org(Base):
    """조직 테이블 모델
    
    조직 구조와 계층 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_org"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '조직'
    }
    
    # 기본 필드
    org_no = Column(Numeric(10), primary_key=True, comment="조직번호")
    parent_org_no = Column(Numeric(10), nullable=True, comment="상급부서번호")
    org_nm = Column(String(30), nullable=True, comment="조직명")
    org_ordr = Column(Numeric(3), nullable=True, comment="조직순번")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=func.current_timestamp(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
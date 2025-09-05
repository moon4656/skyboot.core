"""우편번호 관련 모델

우편번호 정보 관련 테이블의 SQLAlchemy 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Numeric, DateTime
from sqlalchemy.sql import func
from ..database.database import Base


class Zip(Base):
    """우편번호 테이블 모델
    
    우편번호와 주소 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_zip"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '우편번호'
    }
    
    # 기본 필드 (복합 기본키)
    zip = Column(String(6), primary_key=True, comment="우편번호")
    sn = Column(Numeric(10), primary_key=True, comment="일련번호")
    ctprvn_nm = Column(String(20), nullable=True, comment="시도명")
    signgu_nm = Column(String(20), nullable=True, comment="시군구명")
    emd_nm = Column(String(60), nullable=True, comment="읍면동명")
    li_buld_nm = Column(String(60), nullable=True, comment="리건물명")
    lnbr_dong_ho = Column(String(20), nullable=True, comment="번지동호")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=True, default=func.current_date(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
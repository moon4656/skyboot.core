"""공통코드 관련 SQLAlchemy 모델

공통코드와 공통상세코드 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database.database import Base


class CmmnGrpCode(Base):
    """공통코드 테이블 모델
    
    공통코드 그룹 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_cmmn_grp_code"
    __table_args__ = (
        Index('ix_cmmn_grp_code_01', 'cl_code'),
        {
            'schema': 'skybootcore',
            'comment': '공통코드'
        }
    )
    
    # 기본 필드
    code_id = Column(String(6), primary_key=True, comment="코드ID")
    code_id_nm = Column(String(60), nullable=True, comment="코드ID명")
    code_id_dc = Column(String(200), nullable=True, comment="코드ID설명")
    use_yn = Column(String(1), nullable=False, default='Y', comment="사용여부")
    cl_code = Column(String(10), nullable=True, comment="분류코드")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=True, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    detail_codes = relationship("CmmnCode", back_populates="group_code")
    
    def __repr__(self):
        return f"<CmmnGrpCode(code_id='{self.code_id}', code_id_nm='{self.code_id_nm}')>"


class CmmnCode(Base):
    """공통상세코드 테이블 모델
    
    공통코드의 상세 코드 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_cmmn_code"
    __table_args__ = (
        Index('ix_cmmn_code_01', 'code_id'),
        {
            'schema': 'skybootcore',
            'comment': '공통상세코드'
        }
    )
    
    # 기본 필드 (복합 기본키)
    code_id = Column(String(6), ForeignKey('skybootcore.tb_cmmn_grp_code.code_id'), 
                    primary_key=True, comment="코드ID")
    code = Column(String(15), primary_key=True, comment="코드")
    code_nm = Column(String(60), nullable=True, comment="코드명")
    code_dc = Column(String(200), nullable=True, comment="코드설명")
    attr1 = Column(String(20), nullable=True, comment="속성1")
    attr2 = Column(String(20), nullable=True, comment="속성2")
    attr3 = Column(String(20), nullable=True, comment="속성3")
    attr4 = Column(String(20), nullable=True, comment="속성4")
    use_yn = Column(String(1), nullable=False, default='Y', comment="사용여부")
    code_ordr = Column(Integer, nullable=True, default=1, comment="코드순서")
    
    # 공통 필드
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    frst_regist_pnttm = Column(DateTime, nullable=True, default=datetime.now, comment="최초등록시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    
    # 관계 설정
    group_code = relationship("CmmnGrpCode", back_populates="detail_codes")
    
    def __repr__(self):
        return f"<CmmnCode(code_id='{self.code_id}', code='{self.code}', code_nm='{self.code_nm}')>"
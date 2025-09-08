"""파일 관련 SQLAlchemy 모델

파일속성과 파일상세정보 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Numeric, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database.database import Base


class File(Base):
    """파일속성 테이블 모델
    
    첨부파일의 기본 속성 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_file"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '파일속성'
    }
    
    # 기본 필드
    atch_file_id = Column(String(36), primary_key=True, comment="첨부파일ID")
    creat_dt = Column(DateTime, nullable=False, comment="생성일시")
    use = Column(String(1), nullable=False, default='Y', comment="사용여부")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=False, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    file_details = relationship("FileDetail", back_populates="file")
    
    def __repr__(self):
        return f"<File(atch_file_id='{self.atch_file_id}', creat_dt='{self.creat_dt}')>"


class FileDetail(Base):
    """파일상세정보 테이블 모델
    
    첨부파일의 상세 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_filedetail"
    __table_args__ = (
        Index('ix_filedetail_01', 'atch_file_id'),
        {
            'schema': 'skybootcore',
            'comment': '파일상세정보'
        }
    )
    
    # 기본 필드 (복합 기본키)
    atch_file_id = Column(String(36), ForeignKey('skybootcore.tb_file.atch_file_id'), 
                         primary_key=True, comment="첨부파일ID")
    file_sn = Column(Numeric(10), primary_key=True, comment="파일순번")
    file_stre_cours = Column(String(2000), nullable=False, comment="파일저장경로")
    stre_file_nm = Column(String(255), nullable=False, comment="저장파일명")
    orignl_file_nm = Column(String(255), nullable=True, comment="원파일명")
    file_extsn = Column(String(20), nullable=False, comment="파일확장자")
    file_cn = Column(Text, nullable=True, comment="파일내용")
    file_size = Column(Numeric(8), nullable=True, comment="파일크기")
    dwld_co = Column(Numeric(10), nullable=True, default=0, comment="다운로드수")
    file_delete_yn = Column(String(1), nullable=False, default='N', comment="파일삭제삭제여부")
    
    # 공통 필드
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    
    # 관계 설정
    file = relationship("File", back_populates="file_details")
    
    def __repr__(self):
        return f"<FileDetail(atch_file_id='{self.atch_file_id}', file_sn={self.file_sn}, orignl_file_nm='{self.orignl_file_nm}')>"
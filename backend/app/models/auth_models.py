"""권한 관련 SQLAlchemy 모델

권한정보와 권한메뉴 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from ..database.database import Base


class AuthorInfo(Base):
    """권한정보 테이블 모델
    
    시스템의 권한 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_authorinfo"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '권한정보'
    }
    
    # 기본 필드
    author_code = Column(String(30), primary_key=True, comment="권한코드")
    author_nm = Column(String(60), nullable=False, comment="권한명")
    author_dc = Column(String(200), nullable=True, comment="권한설명")
    author_creat_de = Column(DateTime, nullable=False, comment="권한생성일")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=False, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    author_menus = relationship("AuthorMenu", back_populates="author_info")
    
    def __repr__(self):
        return f"<AuthorInfo(author_code='{self.author_code}', author_nm='{self.author_nm}')>"


class AuthorMenu(Base):
    """권한메뉴 테이블 모델
    
    권한별 메뉴 접근 권한을 관리하는 테이블입니다.
    """
    __tablename__ = "tb_authormenu"
    __table_args__ = (
        Index('ix_authormenu_01', 'menu_no'),
        Index('ix_authormenu_02', 'author_code'),
        {
            'schema': 'skybootcore',
            'comment': '권한메뉴'
        }
    )
    
    # 기본 필드 (복합 기본키)
    author_code = Column(String(30), ForeignKey('skybootcore.tb_authorinfo.author_code'), 
                        primary_key=True, comment="권한코드")
    menu_no = Column(String(7), ForeignKey('skybootcore.tb_menuinfo.menu_no'), 
                    primary_key=True, comment="메뉴번호")
    work_auth_code = Column(String(15), nullable=False, default='WA0000000000000', comment="작업권한")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    author_info = relationship("AuthorInfo", back_populates="author_menus")
    menu_info = relationship("MenuInfo")
    
    def __repr__(self):
        return f"<AuthorMenu(author_code='{self.author_code}', menu_no='{self.menu_no}')>"
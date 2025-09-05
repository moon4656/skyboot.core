"""메뉴 관련 SQLAlchemy 모델

메뉴정보 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric, Index, ForeignKey
from sqlalchemy.orm import relationship
from ..database.database import Base


class MenuInfo(Base):
    """메뉴정보 테이블 모델
    
    시스템의 메뉴 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_menuinfo"
    __table_args__ = (
        Index('ix_menuinfo_01', 'upper_menu_no'),
        {
            'schema': 'skybootcore',
            'comment': '메뉴정보'
        }
    )
    
    # 기본 필드
    menu_no = Column(String, primary_key=True, comment="메뉴번호")
    menu_nm = Column(String(60), nullable=False, comment="메뉴명")
    progrm_file_nm = Column(String(60), nullable=False, comment="프로그램파일명")
    upper_menu_no = Column(String, ForeignKey('skybootcore.tb_menuinfo.menu_no'), 
                          nullable=True, comment="상위메뉴번호")
    menu_ordr = Column(Numeric(5), nullable=False, comment="메뉴순서")
    menu_dc = Column(String(250), nullable=True, comment="메뉴설명")
    relate_image_path = Column(String(100), nullable=True, comment="관계이미지경로")
    relate_image_nm = Column(String(60), nullable=True, comment="관계이미지명")
    display_yn = Column(String(1), nullable=False, default='Y', comment="메뉴표시여부")
    use_tag_yn = Column(String(1), nullable=False, default='N', comment="메뉴 표시할때 이미지 URL 대신 태그내용를 사용하는지 여부표시")
    menu_tag = Column(String, nullable=True, comment="메뉴 표시 태그 use_tag_yn 이 Y 일때 사용")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정 (자기 참조)
    children = relationship("MenuInfo", 
                          backref="parent",
                          remote_side=[menu_no],
                          foreign_keys=[upper_menu_no])
    
    def __repr__(self):
        return f"<MenuInfo(menu_no='{self.menu_no}', menu_nm='{self.menu_nm}', menu_ordr={self.menu_ordr})>"
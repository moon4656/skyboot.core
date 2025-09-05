"""사용자 관련 모델

업무사용자정보 테이블의 SQLAlchemy 모델을 정의합니다.
"""

from sqlalchemy import Column, String, Numeric, DateTime, Text, Index, ForeignKey
from sqlalchemy.sql import func
from ..database.database import Base


class UserInfo(Base):
    """업무사용자정보 테이블 모델
    
    사용자의 기본 정보와 인증 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_userinfo"
    __table_args__ = (
        Index('ix_userinfo_01', 'orgnzt_id'),
        Index('ix_userinfo_02', 'group_id'),
        {
            'schema': 'skybootcore',
            'comment': '업무사용자정보'
        }
    )
    
    # 기본 필드
    user_id = Column(String(20), primary_key=True, comment="업무사용자ID")
    orgnzt_id = Column(String(20), nullable=True, comment="조직ID")
    user_nm = Column(String(60), nullable=False, comment="사용자명")
    password = Column(String(200), nullable=False, comment="비밀번호")
    empl_no = Column(String(20), nullable=True, comment="사원번호")
    ihidnum = Column(String(200), nullable=True, comment="주민등록번호")
    sexdstn_code = Column(String(1), nullable=True, comment="성별코드")
    brthdy = Column(String(20), nullable=True, comment="생일")
    fxnum = Column(String(20), nullable=True, comment="팩스번호")
    house_adres = Column(String(100), nullable=True, comment="주택주소")
    password_hint = Column(String(100), nullable=True, comment="비밀번호힌트")
    password_cnsr = Column(String(100), nullable=True, comment="비밀번호정답")
    house_end_telno = Column(String(4), nullable=True, comment="주택끝전화번호")
    area_no = Column(String(4), nullable=True, comment="지역번호")
    detail_adres = Column(String(100), nullable=True, comment="상세주소")
    zip = Column(String(6), nullable=True, comment="우편번호")
    offm_telno = Column(String(20), nullable=True, comment="사무실전화번호")
    mbtlnum = Column(String(20), nullable=True, comment="이동전화번호")
    email_adres = Column(String(50), nullable=True, comment="이메일주소")
    ofcps_nm = Column(String(60), nullable=True, comment="직위명")
    house_middle_telno = Column(String(4), nullable=True, comment="주택중간전화번호")
    group_id = Column(String(20), nullable=True, comment="그룹ID")
    pstinst_code = Column(String(8), nullable=True, comment="소속기관코드")
    emplyr_sttus_code = Column(String(1), nullable=False, default='A', comment="사용자상태코드")
    esntl_id = Column(String(20), nullable=True, comment="고유ID")
    crtfc_dn_value = Column(String(100), nullable=True, comment="인증DN값")
    sbscrb_de = Column(DateTime, nullable=True, comment="가입일자")
    lock_at = Column(String(1), nullable=True, default='N', comment="잠금여부")
    lock_cnt = Column(Numeric(3), nullable=True, comment="잠금회수")
    lock_last_pnttm = Column(DateTime, nullable=True, comment="잠금최종시점")
    chg_pwd_last_pnttm = Column(DateTime, nullable=True, comment="비밀번호변경최종시점")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=func.current_date(), comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
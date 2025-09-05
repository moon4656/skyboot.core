"""사용자 관련 Pydantic 스키마

사용자 정보, 조직, 우편번호 관련 요청/응답 모델을 정의합니다.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from decimal import Decimal


# ==================== UserInfo 스키마 ====================

class UserInfoBase(BaseModel):
    """사용자 정보 기본 스키마"""
    user_id: str = Field(..., max_length=20, description="업무사용자ID")
    orgnzt_id: Optional[str] = Field(None, max_length=20, description="조직ID")
    user_nm: str = Field(..., max_length=60, description="사용자명")
    empl_no: Optional[str] = Field(None, max_length=20, description="사원번호")
    ihidnum: Optional[str] = Field(None, max_length=200, description="주민등록번호")
    sexdstn_code: Optional[str] = Field(None, max_length=1, description="성별코드")
    brthdy: Optional[str] = Field(None, max_length=20, description="생일")
    fxnum: Optional[str] = Field(None, max_length=20, description="팩스번호")
    house_adres: Optional[str] = Field(None, max_length=100, description="주택주소")
    password_hint: Optional[str] = Field(None, max_length=100, description="비밀번호힌트")
    password_cnsr: Optional[str] = Field(None, max_length=100, description="비밀번호정답")
    house_end_telno: Optional[str] = Field(None, max_length=4, description="주택끝전화번호")
    area_no: Optional[str] = Field(None, max_length=4, description="지역번호")
    detail_adres: Optional[str] = Field(None, max_length=100, description="상세주소")
    zip: Optional[str] = Field(None, max_length=6, description="우편번호")
    offm_telno: Optional[str] = Field(None, max_length=20, description="사무실전화번호")
    mbtlnum: Optional[str] = Field(None, max_length=20, description="이동전화번호")
    email_adres: Optional[EmailStr] = Field(None, description="이메일주소")
    ofcps_nm: Optional[str] = Field(None, max_length=60, description="직위명")
    house_middle_telno: Optional[str] = Field(None, max_length=4, description="주택중간전화번호")
    group_id: Optional[str] = Field(None, max_length=20, description="그룹ID")
    pstinst_code: Optional[str] = Field(None, max_length=8, description="소속기관코드")
    emplyr_sttus_code: str = Field(..., max_length=1, description="사용자상태코드")
    esntl_id: Optional[str] = Field(None, max_length=20, description="고유ID")
    crtfc_dn_value: Optional[str] = Field(None, max_length=100, description="인증DN값")
    sbscrb_de: Optional[datetime] = Field(None, description="가입일자")
    lock_at: Optional[str] = Field(None, max_length=1, description="잠금여부")
    lock_cnt: Optional[Decimal] = Field(None, description="잠금회수")
    lock_last_pnttm: Optional[datetime] = Field(None, description="잠금최종시점")
    chg_pwd_last_pnttm: Optional[datetime] = Field(None, description="비밀번호변경최종시점")
    
class UserInfoBasicBase(BaseModel):
    """사용자 정보 기본 스키마"""
    user_id: str = Field(..., max_length=20, description="업무사용자ID")
    user_nm: str = Field(..., max_length=60, description="사용자명")
    password: str = Field(..., min_length=4, max_length=200, description="비밀번호")

class UserInfoCreate(UserInfoBase):
    """사용자 정보 생성 스키마"""
    user_id: str = Field(..., max_length=20, description="업무사용자ID")
    password: str = Field(..., min_length=4, max_length=200, description="비밀번호")
    ihidnum: Optional[str] = Field(None, max_length=200, description="주민등록번호")


class UserInfoUpdate(BaseModel):
    """사용자 정보 수정 스키마 - 부분 업데이트용"""
    orgnzt_id: Optional[str] = Field(None, max_length=20, description="조직ID")
    user_nm: Optional[str] = Field(None, max_length=60, description="사용자명")
    empl_no: Optional[str] = Field(None, max_length=20, description="사원번호")
    brthdy: Optional[str] = Field(None, max_length=20, description="생일")
    fxnum: Optional[str] = Field(None, max_length=20, description="팩스번호")
    offm_telno: Optional[str] = Field(None, max_length=20, description="사무실전화번호")
    mbtlnum: Optional[str] = Field(None, max_length=20, description="이동전화번호")
    email_adres: Optional[EmailStr] = Field(None, description="이메일주소")
    ofcps_nm: Optional[str] = Field(None, max_length=60, description="직위명")
    emplyr_sttus_code: Optional[str] = Field(None, max_length=1, description="사용자상태코드")


class UserInfoResponse(UserInfoBase):
    """사용자 정보 응답 스키마"""
    user_id: str = Field(..., description="업무사용자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class UserInfoPagination(BaseModel):
    """사용자 정보 페이지네이션 응답 스키마"""
    items: List[UserInfoResponse] = Field(..., description="사용자 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== Org 스키마 ====================

class OrgBase(BaseModel):
    """조직 기본 스키마"""
    parent_org_no: Optional[Decimal] = Field(None, description="상급부서번호")
    org_nm: Optional[str] = Field(None, max_length=30, description="조직명")
    org_ordr: Optional[Decimal] = Field(None, description="조직순번")


class OrgCreate(OrgBase):
    """조직 생성 스키마"""
    org_no: Decimal = Field(..., description="조직번호")


class OrgUpdate(OrgBase):
    """조직 수정 스키마"""
    pass


class OrgResponse(OrgBase):
    """조직 응답 스키마"""
    org_no: Decimal = Field(..., description="조직번호")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class OrgPagination(BaseModel):
    """조직 페이지네이션 응답 스키마"""
    items: List[OrgResponse] = Field(..., description="조직 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== Zip 스키마 ====================

class ZipBase(BaseModel):
    """우편번호 기본 스키마"""
    zip: Optional[str] = Field(None, max_length=6, description="우편번호")
    ctprvn_nm: Optional[str] = Field(None, max_length=30, description="시도명")
    signgu_nm: Optional[str] = Field(None, max_length=30, description="시군구명")
    emd_nm: Optional[str] = Field(None, max_length=30, description="읍면동명")
    li_buld_nm: Optional[str] = Field(None, max_length=30, description="리건물명")
    lnbr_dong_ho: Optional[str] = Field(None, max_length=30, description="지번동호")


class ZipCreate(ZipBase):
    """우편번호 생성 스키마"""
    sn: Decimal = Field(..., description="일련번호")


class ZipUpdate(ZipBase):
    """우편번호 수정 스키마"""
    pass


class ZipResponse(ZipBase):
    """우편번호 응답 스키마"""
    sn: Decimal = Field(..., description="일련번호")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class ZipPagination(BaseModel):
    """우편번호 페이지네이션 응답 스키마"""
    items: List[ZipResponse] = Field(..., description="우편번호 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== 검색 및 통계 스키마 ====================

class UserSearchParams(BaseModel):
    """사용자 검색 파라미터 스키마"""
    user_nm: Optional[str] = Field(None, description="사용자명")
    orgnzt_id: Optional[str] = Field(None, description="조직ID")
    emplyr_sttus_code: Optional[str] = Field(None, description="사용자상태코드")
    email_adres: Optional[str] = Field(None, description="이메일주소")
    group_id: Optional[str] = Field(None, description="그룹ID")
    lock_at: Optional[str] = Field(None, description="잠금여부")


class UserStatistics(BaseModel):
    """사용자 통계 스키마"""
    total_users: int = Field(..., description="전체 사용자 수")
    active_users: int = Field(..., description="활성 사용자 수")
    locked_users: int = Field(..., description="잠금된 사용자 수")
    users_by_status: dict = Field(..., description="상태별 사용자 수")
    users_by_organization: dict = Field(..., description="조직별 사용자 수")
    recent_registrations: int = Field(..., description="최근 가입자 수")


class OrgTreeNode(BaseModel):
    """조직 트리 노드 스키마"""
    org_no: Decimal = Field(..., description="조직번호")
    org_nm: Optional[str] = Field(None, description="조직명")
    parent_org_no: Optional[Decimal] = Field(None, description="상급부서번호")
    org_ordr: Optional[Decimal] = Field(None, description="조직순번")
    children: List['OrgTreeNode'] = Field(default=[], description="하위 조직")
    user_count: int = Field(default=0, description="소속 사용자 수")


# Pydantic 모델 업데이트 (순환 참조 해결)
OrgTreeNode.model_rebuild()
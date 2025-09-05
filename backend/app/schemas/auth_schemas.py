"""권한 관련 Pydantic 스키마

권한정보와 권한메뉴 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from .user_schemas import UserInfoResponse


# AuthorInfo 스키마
class AuthorInfoBase(BaseModel):
    """권한정보 기본 스키마"""
    author_nm: str = Field(..., max_length=60, description="권한명")
    author_dc: Optional[str] = Field(None, max_length=200, description="권한설명")
    author_creat_de: datetime = Field(..., description="권한생성일")


class AuthorInfoCreate(AuthorInfoBase):
    """권한정보 생성 스키마"""
    author_code: str = Field(..., max_length=30, description="권한코드")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class AuthorInfoUpdate(BaseModel):
    """권한정보 수정 스키마"""
    author_nm: Optional[str] = Field(None, max_length=60, description="권한명")
    author_dc: Optional[str] = Field(None, max_length=200, description="권한설명")
    author_creat_de: Optional[datetime] = Field(None, description="권한생성일")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class AuthorInfoResponse(AuthorInfoBase):
    """권한정보 응답 스키마"""
    author_code: str = Field(..., description="권한코드")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: str = Field(..., description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


# AuthorMenu 스키마
class AuthorMenuBase(BaseModel):
    """권한메뉴 기본 스키마"""
    work_auth_code: str = Field(default="WA0000000000000", max_length=15, description="작업권한")


class AuthorMenuCreate(AuthorMenuBase):
    """권한메뉴 생성 스키마"""
    author_code: str = Field(..., max_length=30, description="권한코드")
    menu_no: str = Field(..., max_length=7, description="메뉴번호")
    frst_register_id: Optional[str] = Field(None, max_length=20, description="최초등록자ID")


class AuthorMenuUpdate(BaseModel):
    """권한메뉴 수정 스키마"""
    work_auth_code: Optional[str] = Field(None, max_length=15, description="작업권한")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class AuthorMenuResponse(AuthorMenuBase):
    """권한메뉴 응답 스키마"""
    author_code: str = Field(..., description="권한코드")
    menu_no: str = Field(..., description="메뉴번호")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


# 권한정보와 권한메뉴 관계 포함 스키마
class AuthorInfoWithMenus(AuthorInfoResponse):
    """권한정보와 권한메뉴 관계 포함 응답 스키마"""
    author_menus: List[AuthorMenuResponse] = Field(default=[], description="권한메뉴 목록")


class AuthorMenuWithAuthor(AuthorMenuResponse):
    """권한메뉴와 권한정보 관계 포함 응답 스키마"""
    author_info: Optional[AuthorInfoResponse] = Field(None, description="권한정보")


# 페이지네이션 응답 스키마
class AuthorInfoListResponse(BaseModel):
    """권한정보 목록 응답 스키마"""
    items: List[AuthorInfoResponse] = Field(..., description="권한정보 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


class AuthorMenuListResponse(BaseModel):
    """권한메뉴 목록 응답 스키마"""
    items: List[AuthorMenuResponse] = Field(..., description="권한메뉴 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 페이지네이션 스키마
class AuthorInfoPagination(BaseModel):
    """권한정보 페이지네이션 응답 스키마"""
    items: List[AuthorInfoResponse] = Field(..., description="권한정보 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


class AuthorMenuPagination(BaseModel):
    """권한메뉴 페이지네이션 응답 스키마"""
    items: List[AuthorMenuResponse] = Field(..., description="권한메뉴 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


# 사용자 로그인 관련 스키마
class UserLoginRequest(BaseModel):
    """사용자 로그인 요청 스키마"""
    user_id: str = Field(..., max_length=20, description="사용자 ID")
    password: str = Field(..., min_length=4, description="비밀번호")


class UserLoginResponse(BaseModel):
    """사용자 로그인 응답 스키마"""
    access_token: str = Field(..., description="액세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="토큰 만료 시간(초)")
    user_info: dict = Field(..., description="사용자 정보")


class TokenRefreshRequest(BaseModel):
    """토큰 갱신 요청 스키마"""
    refresh_token: str = Field(..., description="리프레시 토큰")


class TokenRefreshResponse(BaseModel):
    """토큰 갱신 응답 스키마"""
    access_token: str = Field(..., description="새로운 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="토큰 만료 시간(초)")


class UserPermissionResponse(BaseModel):
    """사용자 권한 응답 스키마"""
    user_id: str = Field(..., description="사용자 ID")
    permissions: List[str] = Field(default=[], description="권한 목록")
    menus: List[AuthorMenuResponse] = Field(default=[], description="메뉴 권한 목록")
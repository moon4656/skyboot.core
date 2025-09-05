"""공통 코드 관련 Pydantic 스키마

공통그룹코드, 공통코드 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


# CmmnGrpCode 스키마
class CmmnGrpCodeBase(BaseModel):
    """공통그룹코드 기본 스키마"""
    group_code_nm: Optional[str] = Field(None, max_length=60, description="그룹코드명")
    group_code_dc: Optional[str] = Field(None, max_length=200, description="그룹코드설명")
    use_at: str = Field(default="Y", max_length=1, description="사용여부")
    delete_at: str = Field(default="N", max_length=1, description="삭제여부")


class CmmnGrpCodeCreate(CmmnGrpCodeBase):
    """공통그룹코드 생성 스키마"""
    group_code: str = Field(..., max_length=6, description="그룹코드")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class CmmnGrpCodeUpdate(BaseModel):
    """공통그룹코드 수정 스키마"""
    group_code_nm: Optional[str] = Field(None, max_length=60, description="그룹코드명")
    group_code_dc: Optional[str] = Field(None, max_length=200, description="그룹코드설명")
    use_at: Optional[str] = Field(None, max_length=1, description="사용여부")
    delete_at: Optional[str] = Field(None, max_length=1, description="삭제여부")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class CmmnGrpCodeResponse(CmmnGrpCodeBase):
    """공통그룹코드 응답 스키마"""
    group_code: str = Field(..., description="그룹코드")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# CmmnCode 스키마
class CmmnCodeBase(BaseModel):
    """공통코드 기본 스키마"""
    code_nm: Optional[str] = Field(None, max_length=60, description="코드명")
    code_dc: Optional[str] = Field(None, max_length=200, description="코드설명")
    use_at: str = Field(default="Y", max_length=1, description="사용여부")
    cl_code: Optional[str] = Field(None, max_length=5, description="분류코드")
    sort_ordr: Optional[Decimal] = Field(None, description="정렬순서")
    etc1: Optional[str] = Field(None, max_length=100, description="기타1")
    etc2: Optional[str] = Field(None, max_length=100, description="기타2")
    etc3: Optional[str] = Field(None, max_length=100, description="기타3")
    delete_at: str = Field(default="N", max_length=1, description="삭제여부")


class CmmnCodeCreate(CmmnCodeBase):
    """공통코드 생성 스키마"""
    code: str = Field(..., max_length=15, description="코드")
    group_code: str = Field(..., max_length=6, description="그룹코드")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class CmmnCodeUpdate(BaseModel):
    """공통코드 수정 스키마"""
    code_nm: Optional[str] = Field(None, max_length=60, description="코드명")
    code_dc: Optional[str] = Field(None, max_length=200, description="코드설명")
    use_at: Optional[str] = Field(None, max_length=1, description="사용여부")
    cl_code: Optional[str] = Field(None, max_length=5, description="분류코드")
    sort_ordr: Optional[Decimal] = Field(None, description="정렬순서")
    etc1: Optional[str] = Field(None, max_length=100, description="기타1")
    etc2: Optional[str] = Field(None, max_length=100, description="기타2")
    etc3: Optional[str] = Field(None, max_length=100, description="기타3")
    delete_at: Optional[str] = Field(None, max_length=1, description="삭제여부")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class CmmnCodeResponse(CmmnCodeBase):
    """공통코드 응답 스키마"""
    code: str = Field(..., description="코드")
    group_code: str = Field(..., description="그룹코드")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# 관계 포함 스키마
class CmmnGrpCodeWithCodes(CmmnGrpCodeResponse):
    """공통그룹코드와 공통코드 관계 포함 응답 스키마"""
    codes: List[CmmnCodeResponse] = Field(default=[], description="공통코드 목록")


class CmmnCodeWithGroup(CmmnCodeResponse):
    """공통코드와 그룹코드 관계 포함 응답 스키마"""
    group_info: Optional[CmmnGrpCodeResponse] = Field(None, description="그룹코드 정보")


# 페이지네이션 응답 스키마
class CmmnGrpCodeListResponse(BaseModel):
    """공통그룹코드 목록 응답 스키마"""
    items: List[CmmnGrpCodeResponse] = Field(..., description="공통그룹코드 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


class CmmnCodeListResponse(BaseModel):
    """공통코드 목록 응답 스키마"""
    items: List[CmmnCodeResponse] = Field(..., description="공통코드 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 코드 검색 스키마
class CodeSearchParams(BaseModel):
    """코드 검색 파라미터 스키마"""
    group_code: Optional[str] = Field(None, description="그룹코드")
    code: Optional[str] = Field(None, description="코드")
    code_nm: Optional[str] = Field(None, description="코드명")
    use_at: Optional[str] = Field(None, description="사용여부")
    cl_code: Optional[str] = Field(None, description="분류코드")


class GroupCodeSearchParams(BaseModel):
    """그룹코드 검색 파라미터 스키마"""
    group_code: Optional[str] = Field(None, description="그룹코드")
    group_code_nm: Optional[str] = Field(None, description="그룹코드명")
    use_at: Optional[str] = Field(None, description="사용여부")


# 코드 선택 옵션 스키마
class CodeOption(BaseModel):
    """코드 선택 옵션 스키마"""
    value: str = Field(..., description="코드값")
    label: str = Field(..., description="코드명")
    description: Optional[str] = Field(None, description="코드설명")
    group_code: Optional[str] = Field(None, description="그룹코드")
    sort_order: Optional[Decimal] = Field(None, description="정렬순서")


class CodeOptionsResponse(BaseModel):
    """코드 선택 옵션 목록 응답 스키마"""
    group_code: str = Field(..., description="그룹코드")
    group_name: Optional[str] = Field(None, description="그룹코드명")
    options: List[CodeOption] = Field(..., description="코드 옵션 목록")


# 페이지네이션 스키마 (라우터에서 사용)
class CmmnGrpCodePagination(BaseModel):
    """공통그룹코드 페이지네이션 응답 스키마"""
    items: List[CmmnGrpCodeResponse] = Field(..., description="공통그룹코드 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


class CmmnCodePagination(BaseModel):
    """공통코드 페이지네이션 응답 스키마"""
    items: List[CmmnCodeResponse] = Field(..., description="공통코드 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


# 관계 포함 스키마
class CmmnGrpCodeWithCodes(CmmnGrpCodeResponse):
    """공통그룹코드와 하위 코드 포함 응답 스키마"""
    codes: List[CmmnCodeResponse] = Field(default=[], description="하위 공통코드 목록")


# 검색 파라미터 스키마 (라우터에서 사용)
class CmmnCodeSearchParams(BaseModel):
    """공통코드 검색 파라미터 스키마"""
    group_code: Optional[str] = Field(None, description="그룹코드")
    code: Optional[str] = Field(None, description="코드")
    code_nm: Optional[str] = Field(None, description="코드명")
    use_at: Optional[str] = Field(None, description="사용여부")
    cl_code: Optional[str] = Field(None, description="분류코드")


# 통계 스키마
class CmmnGrpCodeStatistics(BaseModel):
    """공통그룹코드 통계 응답 스키마"""
    total_groups: int = Field(..., description="전체 그룹 수")
    active_groups: int = Field(..., description="활성 그룹 수")
    inactive_groups: int = Field(..., description="비활성 그룹 수")
    total_codes: int = Field(..., description="전체 코드 수")
    avg_codes_per_group: float = Field(..., description="그룹당 평균 코드 수")


class CmmnCodeStatistics(BaseModel):
    """공통코드 통계 응답 스키마"""
    total_codes: int = Field(..., description="전체 코드 수")
    active_codes: int = Field(..., description="활성 코드 수")
    inactive_codes: int = Field(..., description="비활성 코드 수")
    codes_by_group: dict = Field(..., description="그룹별 코드 수")
    most_used_group: Optional[str] = Field(None, description="가장 많이 사용된 그룹")
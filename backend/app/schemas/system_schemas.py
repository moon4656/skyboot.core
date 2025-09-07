"""시스템 관련 Pydantic 스키마

시스템 로그, 웹 로그, 프로그램 목록 관련 요청/응답 모델을 정의합니다.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal


# ==================== SysLog 스키마 ====================

class SysLogBase(BaseModel):
    """시스템 로그 기본 스키마"""
    requst_id: Optional[str] = Field(None, max_length=50, description="요청ID")
    job_se_code: Optional[str] = Field(None, max_length=10, description="업무구분코드")
    instt_code: Optional[str] = Field(None, max_length=20, description="기관코드")
    occrrnc_de: Optional[datetime] = Field(None, description="발생일")
    rqester_ip: Optional[str] = Field(None, max_length=50, description="요청자IP")
    rqester_id: Optional[str] = Field(None, max_length=50, description="요청자ID")
    trget_menu_nm: Optional[str] = Field(None, max_length=500, description="대상메뉴명")
    svc_nm: Optional[str] = Field(None, max_length=500, description="서비스명")
    method_nm: Optional[str] = Field(None, max_length=100, description="메서드명")
    process_se_code: Optional[str] = Field(None, max_length=10, description="처리구분코드")
    process_co: Optional[Decimal] = Field(None, description="처리수")
    process_time: Optional[str] = Field(None, max_length=50, description="처리시간")
    rspns_code: Optional[str] = Field(None, max_length=10, description="응답코드")
    error_se: Optional[str] = Field(None, max_length=10, description="오류구분")
    error_co: Optional[Decimal] = Field(None, description="오류수")
    error_code: Optional[str] = Field(None, max_length=10, description="오류코드")


class SysLogCreate(SysLogBase):
    """시스템 로그 생성 스키마"""
    requst_id: str = Field(..., max_length=50, description="요청ID")


class SysLogUpdate(SysLogBase):
    """시스템 로그 수정 스키마"""
    pass


class SysLogResponse(SysLogBase):
    """시스템 로그 응답 스키마"""
    requst_id: str = Field(..., description="요청ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class SysLogPagination(BaseModel):
    """시스템 로그 페이지네이션 응답 스키마"""
    items: List[SysLogResponse] = Field(..., description="시스템 로그 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== WebLog 스키마 ====================

class WebLogBase(BaseModel):
    """웹 로그 기본 스키마"""
    occrrnc_de: Optional[datetime] = Field(None, description="발생일")
    url: Optional[str] = Field(None, max_length=500, description="URL")
    rqester_id: Optional[str] = Field(None, max_length=50, description="요청자ID")
    rqester_ip: Optional[str] = Field(None, max_length=50, description="요청자IP")
    rqester_nm: Optional[str] = Field(None, max_length=100, description="요청자명")
    trget_menu_nm: Optional[str] = Field(None, max_length=100, description="대상메뉴명")
    process_se_code: Optional[str] = Field(None, max_length=50, description="처리구분코드")
    process_cn: Optional[str] = Field(None, description="처리내용")
    process_time: Optional[Decimal] = Field(None, description="처리시간")
    rqest_de: Optional[datetime] = Field(None, description="요청일자")


class WebLogCreate(WebLogBase):
    """웹 로그 생성 스키마"""
    requst_id: str = Field(..., max_length=50, description="요청ID")


class WebLogUpdate(WebLogBase):
    """웹 로그 수정 스키마"""
    pass


class WebLogResponse(WebLogBase):
    """웹 로그 응답 스키마"""
    requst_id: str = Field(..., description="요청ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class WebLogPagination(BaseModel):
    """웹 로그 페이지네이션 응답 스키마"""
    items: List[WebLogResponse] = Field(..., description="웹 로그 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== ProgrmList 스키마 ====================

class ProgrmListBase(BaseModel):
    """프로그램 목록 기본 스키마"""
    progrm_file_nm: Optional[str] = Field(None, max_length=100, description="프로그램파일명")
    progrm_stre_path: Optional[str] = Field(None, max_length=500, description="프로그램저장경로")
    progrm_korean_nm: Optional[str] = Field(None, max_length=100, description="프로그램한글명")
    progrm_dc: Optional[str] = Field(None, max_length=500, description="프로그램설명")
    url: Optional[str] = Field(None, max_length=500, description="URL")


class ProgrmListCreate(ProgrmListBase):
    """프로그램 목록 생성 스키마"""
    progrm_nm: str = Field(..., max_length=100, description="프로그램명")


class ProgrmListUpdate(ProgrmListBase):
    """프로그램 목록 수정 스키마"""
    pass


class ProgrmListResponse(ProgrmListBase):
    """프로그램 목록 응답 스키마"""
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


class ProgrmListPagination(BaseModel):
    """프로그램 목록 페이지네이션 응답 스키마"""
    items: List[ProgrmListResponse] = Field(..., description="프로그램 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# ==================== 검색 및 통계 스키마 ====================

class LogSearchParams(BaseModel):
    """로그 검색 파라미터 스키마"""
    rqester_id: Optional[str] = Field(None, description="요청자ID")
    rqester_ip: Optional[str] = Field(None, description="요청자IP")
    rqester_nm: Optional[str] = Field(None, description="요청자명")
    trget_menu_nm: Optional[str] = Field(None, description="대상메뉴명")
    process_se_code: Optional[str] = Field(None, description="처리구분코드")
    start_date: Optional[datetime] = Field(None, description="시작일자")
    end_date: Optional[datetime] = Field(None, description="종료일자")


class LogStatistics(BaseModel):
    """로그 통계 스키마"""
    total_requests: int = Field(..., description="전체 요청 수")
    unique_users: int = Field(..., description="고유 사용자 수")
    requests_by_hour: dict = Field(..., description="시간별 요청 수")
    requests_by_menu: dict = Field(..., description="메뉴별 요청 수")
    requests_by_process_type: dict = Field(..., description="처리구분별 요청 수")
    average_process_time: float = Field(..., description="평균 처리시간")
    top_users: List[dict] = Field(..., description="상위 사용자 목록")
    error_rate: float = Field(..., description="오류율")


class ProgrmSearchParams(BaseModel):
    """프로그램 검색 파라미터 스키마"""
    progrm_nm: Optional[str] = Field(None, description="프로그램명")
    progrm_korean_nm: Optional[str] = Field(None, description="프로그램한글명")
    progrm_file_nm: Optional[str] = Field(None, description="프로그램파일명")
    url: Optional[str] = Field(None, description="URL")


class SystemHealthCheck(BaseModel):
    """시스템 상태 확인 스키마"""
    database_status: str = Field(..., description="데이터베이스 상태")
    api_status: str = Field(..., description="API 상태")
    log_count_today: int = Field(..., description="오늘 로그 수")
    error_count_today: int = Field(..., description="오늘 오류 수")
    active_users_today: int = Field(..., description="오늘 활성 사용자 수")
    system_uptime: str = Field(..., description="시스템 가동시간")
    memory_usage: float = Field(..., description="메모리 사용률")
    cpu_usage: float = Field(..., description="CPU 사용률")


class DashboardSummary(BaseModel):
    """대시보드 요약 스키마"""
    total_users: int = Field(..., description="전체 사용자 수")
    active_users_today: int = Field(..., description="오늘 활성 사용자 수")
    total_requests_today: int = Field(..., description="오늘 총 요청 수")
    error_requests_today: int = Field(..., description="오늘 오류 요청 수")
    popular_menus: List[dict] = Field(..., description="인기 메뉴 목록")
    recent_activities: List[dict] = Field(..., description="최근 활동 목록")
    system_alerts: List[dict] = Field(..., description="시스템 알림 목록")
"""로그 관련 Pydantic 스키마

로그인로그 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


# LoginLog 스키마
class LoginLogBase(BaseModel):
    """로그인로그 기본 스키마"""
    user_id: Optional[str] = Field(None, max_length=20, description="사용자ID")
    login_id: Optional[str] = Field(None, max_length=20, description="로그인ID")
    login_ip: Optional[str] = Field(None, max_length=23, description="로그인IP")
    login_mthd: Optional[str] = Field(None, max_length=6, description="로그인방법")
    login_result: Optional[str] = Field(None, max_length=10, description="로그인결과")
    error_occrrnc_at: Optional[str] = Field(None, max_length=1, description="오류발생여부")
    error_code: Optional[str] = Field(None, max_length=3, description="오류코드")
    connect_stats: Optional[str] = Field(None, max_length=1, description="접속상태")
    user_agent: Optional[str] = Field(None, max_length=500, description="사용자 에이전트")
    session_id: Optional[str] = Field(None, max_length=100, description="세션ID")
    logout_time: Optional[datetime] = Field(None, description="로그아웃시간")


class LoginLogCreate(LoginLogBase):
    """로그인로그 생성 스키마"""
    log_id: Optional[str] = Field(None, max_length=20, description="로그ID")


class LoginLogUpdate(BaseModel):
    """로그인로그 수정 스키마"""
    connect_stats: Optional[str] = Field(None, max_length=1, description="접속상태")
    logout_time: Optional[datetime] = Field(None, description="로그아웃시간")
    error_occrrnc_at: Optional[str] = Field(None, max_length=1, description="오류발생여부")
    error_code: Optional[str] = Field(None, max_length=3, description="오류코드")


class LoginLogResponse(LoginLogBase):
    """로그인로그 응답 스키마"""
    log_id: str = Field(..., description="로그ID")
    frst_regist_pnttm: datetime = Field(..., description="생성일시")
    session_duration: Optional[int] = Field(None, description="세션 지속시간(분)")

    class Config:
        from_attributes = True


# 페이지네이션 응답 스키마
class LoginLogListResponse(BaseModel):
    """로그인로그 목록 응답 스키마"""
    items: List[LoginLogResponse] = Field(..., description="로그인로그 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 로그 검색 스키마
class LoginLogSearchParams(BaseModel):
    """로그인로그 검색 파라미터 스키마"""
    login_id: Optional[str] = Field(None, description="로그인ID")
    login_ip: Optional[str] = Field(None, description="로그인IP")
    login_mthd: Optional[str] = Field(None, description="로그인방법")
    error_occrrnc_at: Optional[str] = Field(None, description="오류발생여부")
    error_code: Optional[str] = Field(None, description="오류코드")
    connect_stats: Optional[str] = Field(None, description="접속상태")
    start_date: Optional[datetime] = Field(None, description="시작일시")
    end_date: Optional[datetime] = Field(None, description="종료일시")
    session_id: Optional[str] = Field(None, description="세션ID")


# 로그 통계 스키마
class LoginStatistics(BaseModel):
    """로그인 통계 스키마"""
    total_logins: int = Field(..., description="전체 로그인 수")
    successful_logins: int = Field(..., description="성공한 로그인 수")
    failed_logins: int = Field(..., description="실패한 로그인 수")
    unique_users: int = Field(..., description="고유 사용자 수")
    unique_ips: int = Field(..., description="고유 IP 수")
    avg_session_duration: float = Field(..., description="평균 세션 지속시간(분)")
    peak_login_hour: int = Field(..., description="최대 로그인 시간대")
    login_methods: dict = Field(..., description="로그인 방법별 통계")
    error_codes: dict = Field(..., description="오류 코드별 통계")


class DailyLoginStats(BaseModel):
    """일별 로그인 통계 스키마"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    total_logins: int = Field(..., description="총 로그인 수")
    successful_logins: int = Field(..., description="성공한 로그인 수")
    failed_logins: int = Field(..., description="실패한 로그인 수")
    unique_users: int = Field(..., description="고유 사용자 수")
    peak_hour: int = Field(..., description="최대 로그인 시간대")


class HourlyLoginStats(BaseModel):
    """시간별 로그인 통계 스키마"""
    hour: int = Field(..., description="시간 (0-23)")
    login_count: int = Field(..., description="로그인 수")
    success_rate: float = Field(..., description="성공률 (%)")


# 보안 관련 스키마
class SecurityAlert(BaseModel):
    """보안 알림 스키마"""
    alert_type: str = Field(..., description="알림 유형")
    severity: str = Field(..., description="심각도 (low, medium, high, critical)")
    login_id: str = Field(..., description="로그인ID")
    login_ip: str = Field(..., description="로그인IP")
    description: str = Field(..., description="알림 설명")
    detected_at: datetime = Field(..., description="탐지 시간")
    additional_info: dict = Field(default={}, description="추가 정보")


class SuspiciousActivity(BaseModel):
    """의심스러운 활동 스키마"""
    activity_type: str = Field(..., description="활동 유형")
    login_id: str = Field(..., description="로그인ID")
    ip_addresses: List[str] = Field(..., description="IP 주소 목록")
    login_attempts: int = Field(..., description="로그인 시도 횟수")
    time_window: str = Field(..., description="시간 범위")
    risk_score: float = Field(..., description="위험 점수 (0-100)")
    first_attempt: datetime = Field(..., description="첫 시도 시간")
    last_attempt: datetime = Field(..., description="마지막 시도 시간")


# 세션 관리 스키마
class ActiveSession(BaseModel):
    """활성 세션 스키마"""
    session_id: str = Field(..., description="세션ID")
    login_id: str = Field(..., description="로그인ID")
    login_ip: str = Field(..., description="로그인IP")
    login_time: datetime = Field(..., description="로그인시간")
    last_activity: datetime = Field(..., description="마지막 활동시간")
    user_agent: str = Field(..., description="사용자 에이전트")
    is_active: bool = Field(..., description="활성 상태")
    duration_minutes: int = Field(..., description="세션 지속시간(분)")


class SessionTerminateRequest(BaseModel):
    """세션 종료 요청 스키마"""
    session_ids: List[str] = Field(..., description="종료할 세션ID 목록")
    reason: Optional[str] = Field(None, description="종료 사유")


# 로그 내보내기 스키마
class LogExportRequest(BaseModel):
    """로그 내보내기 요청 스키마"""
    start_date: datetime = Field(..., description="시작일시")
    end_date: datetime = Field(..., description="종료일시")
    login_ids: Optional[List[str]] = Field(None, description="특정 로그인ID 목록")
    include_successful: bool = Field(default=True, description="성공 로그인 포함")
    include_failed: bool = Field(default=True, description="실패 로그인 포함")
    export_format: str = Field(default="csv", description="내보내기 형식 (csv, json, xlsx)")


class LogExportResponse(BaseModel):
    """로그 내보내기 응답 스키마"""
    export_id: str = Field(..., description="내보내기ID")
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일크기")
    record_count: int = Field(..., description="레코드 수")
    download_url: str = Field(..., description="다운로드 URL")
    expires_at: datetime = Field(..., description="만료시간")


# 로그 분석 스키마
class LoginPattern(BaseModel):
    """로그인 패턴 스키마"""
    login_id: str = Field(..., description="로그인ID")
    typical_login_hours: List[int] = Field(..., description="일반적인 로그인 시간대")
    typical_ips: List[str] = Field(..., description="일반적인 IP 주소")
    avg_session_duration: float = Field(..., description="평균 세션 지속시간")
    login_frequency: str = Field(..., description="로그인 빈도")
    last_login: datetime = Field(..., description="마지막 로그인")
    anomaly_score: float = Field(..., description="이상 점수")


class LoginTrend(BaseModel):
    """로그인 트렌드 스키마"""
    period: str = Field(..., description="기간 (daily, weekly, monthly)")
    data_points: List[dict] = Field(..., description="데이터 포인트")
    trend_direction: str = Field(..., description="트렌드 방향 (increasing, decreasing, stable)")
    growth_rate: float = Field(..., description="증가율 (%)")
    seasonal_patterns: List[dict] = Field(default=[], description="계절적 패턴")


# 페이지네이션 스키마
class LoginLogPagination(BaseModel):
    """로그인로그 페이지네이션 스키마"""
    items: List[LoginLogResponse] = Field(..., description="로그인로그 목록")
    total: int = Field(..., description="전체 항목 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 로그인로그 검색 파라미터 스키마
class LoginLogSearchParams(BaseModel):
    """로그인로그 검색 파라미터 스키마"""
    login_id: Optional[str] = Field(None, description="로그인ID")
    login_ip: Optional[str] = Field(None, description="로그인IP")
    start_date: Optional[datetime] = Field(None, description="시작일시")
    end_date: Optional[datetime] = Field(None, description="종료일시")
    connect_stats: Optional[str] = Field(None, description="접속상태")
    error_occrrnc_at: Optional[str] = Field(None, description="오류발생여부")
    login_mthd: Optional[str] = Field(None, description="로그인방법")


# 로그인로그 통계 스키마
class LoginLogStatistics(BaseModel):
    """로그인로그 통계 스키마"""
    total_logins: int = Field(..., description="전체 로그인 수")
    successful_logins: int = Field(..., description="성공 로그인 수")
    failed_logins: int = Field(..., description="실패 로그인 수")
    unique_users: int = Field(..., description="고유 사용자 수")
    unique_ips: int = Field(..., description="고유 IP 수")
    avg_session_duration: float = Field(..., description="평균 세션 지속시간")
    peak_login_hour: int = Field(..., description="최대 로그인 시간대")
    success_rate: float = Field(..., description="로그인 성공률")


# 보안 알림 응답 스키마
class SecurityAlertResponse(BaseModel):
    """보안 알림 응답 스키마"""
    alert_id: str = Field(..., description="알림ID")
    alert_type: str = Field(..., description="알림 유형")
    severity: str = Field(..., description="심각도")
    description: str = Field(..., description="설명")
    affected_user: str = Field(..., description="영향받은 사용자")
    source_ip: str = Field(..., description="출발지 IP")
    detected_at: datetime = Field(..., description="탐지 시간")
    status: str = Field(..., description="상태")
    actions_taken: List[str] = Field(default=[], description="취한 조치")


# 의심스러운 활동 응답 스키마
class SuspiciousActivityResponse(BaseModel):
    """의심스러운 활동 응답 스키마"""
    activity_id: str = Field(..., description="활동ID")
    user_id: str = Field(..., description="사용자ID")
    activity_type: str = Field(..., description="활동 유형")
    risk_score: float = Field(..., description="위험 점수")
    indicators: List[str] = Field(..., description="위험 지표")
    detected_at: datetime = Field(..., description="탐지 시간")
    location: dict = Field(..., description="위치 정보")
    device_info: dict = Field(..., description="디바이스 정보")
    recommended_actions: List[str] = Field(..., description="권장 조치")


# 세션 관리 응답 스키마
class SessionManagementResponse(BaseModel):
    """세션 관리 응답 스키마"""
    session_id: str = Field(..., description="세션ID")
    user_id: Optional[str] = Field(None, description="사용자ID")
    login_time: Optional[str] = Field(None, description="로그인 시간")
    last_activity: Optional[str] = Field(None, description="마지막 활동")
    ip_address: Optional[str] = Field(None, description="IP 주소")
    user_agent: Optional[str] = Field(None, description="사용자 에이전트")
    is_active: Optional[bool] = Field(None, description="활성 상태")
    session_duration: Optional[int] = Field(None, description="세션 지속시간(분)")
    location: Optional[dict] = Field(None, description="위치 정보")
    status: Optional[str] = Field(None, description="세션 상태")


# 로그 분석 응답 스키마
class LogAnalysisResponse(BaseModel):
    """로그 분석 응답 스키마"""
    analysis_id: str = Field(..., description="분석ID")
    analysis_type: str = Field(..., description="분석 유형")
    period: dict = Field(..., description="분석 기간")
    summary: dict = Field(..., description="분석 요약")
    patterns: List[LoginPattern] = Field(..., description="로그인 패턴")
    trends: List[LoginTrend] = Field(..., description="로그인 트렌드")
    anomalies: List[dict] = Field(..., description="이상 징후")
    recommendations: List[str] = Field(..., description="권장사항")
    generated_at: datetime = Field(..., description="생성 시간")


# 로그 내보내기 응답 스키마
class LogExportResponse(BaseModel):
    """로그 내보내기 응답 스키마"""
    status: str = Field(..., description="상태")
    data: dict = Field(..., description="내보내기 데이터")
    format: str = Field(..., description="내보내기 형식")


# 로그 분석 간단 응답 스키마
class LogAnalysisSimpleResponse(BaseModel):
    """로그 분석 간단 응답 스키마"""
    status: str = Field(..., description="상태")
    analysis_type: str = Field(..., description="분석 유형")
    days: int = Field(..., description="분석 기간(일)")
    result: dict = Field(..., description="분석 결과")
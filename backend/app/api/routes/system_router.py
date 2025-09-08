"""시스템 관련 API 라우터

시스템 로그, 웹 로그 관련 CRUD API 엔드포인트를 제공합니다.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.system_models import SysLog, WebLog
from app.schemas.system_schemas import (
    # SysLog 스키마
    SysLogCreate, SysLogUpdate, SysLogResponse, SysLogPagination,
    # WebLog 스키마
    WebLogCreate, WebLogUpdate, WebLogResponse, WebLogPagination,
    # 검색 및 통계 스키마
    LogSearchParams,
    LogStatistics, SystemHealthCheck, DashboardSummary
)
from app.services.system_service import SysLogService, WebLogService, SystemMonitoringService
from app.utils.auth import get_current_user_from_bearer

router = APIRouter(prefix="/system", tags=["시스템 관리"])


# ==================== SysLog 엔드포인트 ====================

@router.post("/logs/", response_model=SysLogResponse, status_code=status.HTTP_201_CREATED, summary="시스템 로그 생성")
async def create_syslog(
    log_data: SysLogCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 시스템 로그를 생성합니다.
    
    - **occrrn_de**: 발생일자 (필수)
    - **log_id**: 로그ID (필수, 고유값)
    - **process_se_code**: 처리구분코드 (선택)
    - **log_level**: 로그레벨 (선택)
    - **system_nm**: 시스템명 (선택)
    - **process_nm**: 처리명 (선택)
    - **error_code**: 에러코드 (선택)
    - **error_cn**: 에러내용 (선택)
    - **rqester_id**: 요청자ID (선택)
    """
    service = SysLogService()
    return service.create(db, log_data)


@router.get("/logs/", response_model=SysLogPagination, summary="시스템 로그 목록 조회")
async def get_system_logs(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시스템 로그 목록을 페이지네이션으로 조회합니다.
    
    - **skip**: 건너뛸 개수 (기본값: 0)
    - **limit**: 조회할 개수 (기본값: 100, 최대: 1000)
    """
    service = SysLogService()
    logs, total = service.get_multi(db, skip=skip, limit=limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return SysLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/logs/search", response_model=SysLogPagination, summary="시스템 로그 검색")
async def search_system_logs(
    start_date: Optional[date] = Query(None, description="시작일자"),
    end_date: Optional[date] = Query(None, description="종료일자"),
    log_level: Optional[str] = Query(None, description="로그레벨"),
    system_nm: Optional[str] = Query(None, description="시스템명"),
    process_nm: Optional[str] = Query(None, description="처리명"),
    error_code: Optional[str] = Query(None, description="에러코드"),
    rqester_id: Optional[str] = Query(None, description="요청자ID"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    다양한 조건으로 시스템 로그를 검색합니다.
    
    - **start_date**: 시작일자 (YYYY-MM-DD)
    - **end_date**: 종료일자 (YYYY-MM-DD)
    - **log_level**: 로그레벨 (DEBUG, INFO, WARNING, ERROR)
    - **system_nm**: 시스템명 (부분 일치)
    - **process_nm**: 처리명 (부분 일치)
    - **error_code**: 에러코드 (정확 일치)
    - **rqester_id**: 요청자ID (정확 일치)
    """
    search_params = LogSearchParams(
        start_date=start_date,
        end_date=end_date,
        log_level=log_level,
        system_nm=system_nm,
        process_nm=process_nm,
        error_code=error_code,
        rqester_id=rqester_id
    )
    
    service = SysLogService()
    logs, total = service.search_logs(db, search_params, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return SysLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/logs/statistics", response_model=LogStatistics, summary="시스템 로그 통계")
async def get_system_log_statistics(
    start_date: Optional[date] = Query(None, description="시작일자"),
    end_date: Optional[date] = Query(None, description="종료일자"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시스템 로그 통계 정보를 조회합니다.
    
    - 전체 로그 수
    - 로그 레벨별 통계
    - 시스템별 통계
    - 에러 발생 통계
    - 시간대별 통계
    """
    service = SysLogService()
    return service.get_log_statistics(db, start_date, end_date)


@router.get("/logs/{log_id}", response_model=SysLogResponse, summary="시스템 로그 상세 조회")
async def get_system_log(
    log_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 시스템 로그의 상세 정보를 조회합니다.
    
    - **log_id**: 로그ID
    """
    service = SysLogService()
    log = service.get_by_log_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시스템 로그를 찾을 수 없습니다."
        )
    return log


@router.put("/logs/{log_id}", response_model=SysLogResponse, summary="시스템 로그 수정")
async def update_system_log(
    log_id: str,
    log_data: SysLogUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시스템 로그 정보를 수정합니다.
    
    - **log_id**: 로그ID
    - **log_data**: 수정할 로그 정보
    """
    service = SysLogService()
    log = service.get_by_log_id(db, log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시스템 로그를 찾을 수 없습니다."
        )
    return service.update(db, log, log_data)


@router.delete("/logs/{log_id}", summary="시스템 로그 삭제")
async def delete_system_log(
    log_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시스템 로그를 삭제합니다.
    
    - **log_id**: 로그ID
    """
    service = SysLogService()
    success = service.delete(db, log_id)
    if success:
        return {"message": "시스템 로그가 성공적으로 삭제되었습니다."}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="시스템 로그 삭제에 실패했습니다."
        )


# ==================== WebLog 엔드포인트 ====================

@router.post("/web-logs/", response_model=WebLogResponse, summary="웹 로그 생성")
async def create_web_log(
    log_data: WebLogCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 웹 로그를 생성합니다.
    
    - **conect_dt**: 접속일시 (필수)
    - **conect_id**: 접속ID (필수, 고유값)
    - **conect_ip**: 접속IP (선택)
    - **conect_url**: 접속URL (선택)
    - **http_method**: HTTP메소드 (선택)
    - **user_agent**: 사용자에이전트 (선택)
    - **referer**: 리퍼러 (선택)
    - **response_code**: 응답코드 (선택)
    - **response_time**: 응답시간 (선택)
    - **user_id**: 사용자ID (선택)
    """
    service = WebLogService()
    return service.create(db, log_data)


@router.get("/web-logs/", response_model=WebLogPagination, summary="웹 로그 목록 조회")
async def get_web_logs(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    웹 로그 목록을 페이지네이션으로 조회합니다.
    """
    service = WebLogService()
    logs, total = service.get_multi(db, skip=skip, limit=limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return WebLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/web-logs/search", response_model=WebLogPagination, summary="웹 로그 검색")
async def search_web_logs(
    start_date: Optional[datetime] = Query(None, description="시작일시"),
    end_date: Optional[datetime] = Query(None, description="종료일시"),
    conect_ip: Optional[str] = Query(None, description="접속IP"),
    conect_url: Optional[str] = Query(None, description="접속URL"),
    http_method: Optional[str] = Query(None, description="HTTP메소드"),
    response_code: Optional[str] = Query(None, description="응답코드"),
    user_id: Optional[str] = Query(None, description="사용자ID"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    다양한 조건으로 웹 로그를 검색합니다.
    
    - **start_date**: 시작일시 (YYYY-MM-DD HH:MM:SS)
    - **end_date**: 종료일시 (YYYY-MM-DD HH:MM:SS)
    - **conect_ip**: 접속IP (부분 일치)
    - **conect_url**: 접속URL (부분 일치)
    - **http_method**: HTTP메소드 (GET, POST, PUT, DELETE 등)
    - **response_code**: 응답코드 (200, 404, 500 등)
    - **user_id**: 사용자ID (정확 일치)
    """
    search_params = LogSearchParams(
        start_date=start_date,
        end_date=end_date,
        conect_ip=conect_ip,
        conect_url=conect_url,
        http_method=http_method,
        response_code=response_code,
        user_id=user_id
    )
    
    service = WebLogService()
    logs, total = service.search_logs(db, search_params, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return WebLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/web-logs/popular-pages", response_model=List[Dict[str, Any]], summary="인기 페이지 조회")
async def get_popular_pages(
    start_date: Optional[datetime] = Query(None, description="시작일시"),
    end_date: Optional[datetime] = Query(None, description="종료일시"),
    limit: int = Query(10, ge=1, le=100, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    인기 페이지 목록을 조회합니다.
    
    - **start_date**: 시작일시
    - **end_date**: 종료일시
    - **limit**: 조회할 개수 (기본값: 10)
    """
    service = WebLogService()
    return service.get_popular_pages(db, start_date, end_date, limit)


@router.get("/web-logs/hourly-traffic", response_model=List[Dict[str, Any]], summary="시간대별 트래픽 조회")
async def get_hourly_traffic(
    target_date: Optional[date] = Query(None, description="대상일자"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시간대별 트래픽 통계를 조회합니다.
    
    - **target_date**: 대상일자 (기본값: 오늘)
    """
    service = WebLogService()
    return service.get_hourly_traffic(db, target_date)


@router.get("/web-logs/{conect_id}", response_model=WebLogResponse, summary="웹 로그 상세 조회")
async def get_web_log(
    conect_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 웹 로그의 상세 정보를 조회합니다.
    
    - **conect_id**: 접속ID
    """
    service = WebLogService()
    log = service.get_by_conect_id(db, conect_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="웹 로그를 찾을 수 없습니다."
        )
    return log


@router.put("/web-logs/{conect_id}", response_model=WebLogResponse, summary="웹 로그 수정")
async def update_web_log(
    conect_id: str,
    log_data: WebLogUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    웹 로그 정보를 수정합니다.
    
    - **conect_id**: 접속ID
    - **log_data**: 수정할 로그 정보
    """
    service = WebLogService()
    log = service.get_by_conect_id(db, conect_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="웹 로그를 찾을 수 없습니다."
        )
    return service.update(db, log, log_data)


@router.delete("/web-logs/{conect_id}", summary="웹 로그 삭제")
async def delete_web_log(
    conect_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    웹 로그를 삭제합니다.
    
    - **conect_id**: 접속ID
    """
    service = WebLogService()
    log = service.get_by_conect_id(db, conect_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="웹 로그를 찾을 수 없습니다."
        )
    service.remove(db, conect_id)
    return {"message": "웹 로그가 성공적으로 삭제되었습니다."}





# ==================== 시스템 모니터링 엔드포인트 ====================

@router.get("/health", response_model=SystemHealthCheck, summary="시스템 상태 확인")
async def get_system_health(
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    시스템의 전반적인 상태를 확인합니다.
    
    - 데이터베이스 연결 상태
    - 시스템 리소스 사용량
    - 최근 에러 발생 현황
    - 서비스 가용성
    """
    # 시스템 모니터링 서비스를 통해 상태 확인
    monitoring_service = SystemMonitoringService()
    
    return monitoring_service.get_system_health(db)


@router.get("/dashboard", response_model=DashboardSummary, summary="대시보드 요약 정보")
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    관리자 대시보드용 요약 정보를 조회합니다.
    
    - 오늘의 주요 통계
    - 최근 활동 현황
    - 시스템 알림
    - 성능 지표
    """
    monitoring_service = SystemMonitoringService()
    return monitoring_service.get_dashboard_summary(db)


@router.get("/logs/user/{user_id}", response_model=SysLogPagination, summary="사용자별 로그 조회")
async def get_user_logs(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 로그를 조회합니다.
    
    - **user_id**: 사용자 ID
    - **days**: 조회 기간 (일, 기본값: 30일)
    """
    service = SysLogService()
    logs, total = service.get_user_logs(db, user_id, days, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return SysLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/logs/errors", response_model=SysLogPagination, summary="오류 로그 조회")
async def get_error_logs(
    days: int = Query(7, ge=1, le=365, description="조회 기간 (일)"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    오류 로그를 조회합니다.
    
    - **days**: 조회 기간 (일, 기본값: 7일)
    """
    service = SysLogService()
    logs, total = service.get_error_logs(db, days, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return SysLogPagination(
        items=logs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/logs/export", summary="로그 데이터 내보내기")
async def export_logs(
    log_type: str = Query(..., description="로그 타입 (system, web)"),
    start_date: Optional[date] = Query(None, description="시작일자"),
    end_date: Optional[date] = Query(None, description="종료일자"),
    format: str = Query("csv", description="내보내기 형식 (csv, json, excel)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그 데이터를 지정된 형식으로 내보냅니다.
    
    - **log_type**: 로그 타입 (system, web)
    - **start_date**: 시작일자
    - **end_date**: 종료일자
    - **format**: 내보내기 형식 (csv, json, excel)
    """
    if log_type == "system":
        service = SysLogService()
        return service.export_logs(db, start_date, end_date, format)
    elif log_type == "web":
        service = WebLogService()
        return service.export_logs(db, start_date, end_date, format)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 로그 타입입니다. (system, web만 지원)"
        )


@router.delete("/logs/cleanup", summary="오래된 로그 정리")
async def cleanup_old_logs(
    log_type: str = Query(..., description="로그 타입 (system, web)"),
    days: int = Query(90, ge=1, description="보관 기간 (일)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    지정된 기간보다 오래된 로그를 정리합니다.
    
    - **log_type**: 로그 타입 (system, web)
    - **days**: 보관 기간 (일, 기본값: 90일)
    """
    if log_type == "system":
        service = SysLogService()
        deleted_count = service.cleanup_old_logs(db, days)
    elif log_type == "web":
        service = WebLogService()
        deleted_count = service.cleanup_old_logs(db, days)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="지원하지 않는 로그 타입입니다. (system, web만 지원)"
        )
    
    return {
        "message": f"{days}일 이전의 {log_type} 로그가 정리되었습니다.",
        "deleted_count": deleted_count
    }
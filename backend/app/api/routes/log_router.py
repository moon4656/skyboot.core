"""로그 관리 API 라우터

로그인 로그 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app.services import LoginLogService
from app.utils.auth import get_current_user_from_bearer
from app.schemas.log_schemas import (
    LoginLogResponse, LoginLogCreate, LoginLogUpdate,
    LoginLogPagination, LoginLogSearchParams, LoginLogStatistics,
    SecurityAlertResponse, SuspiciousActivityResponse,
    SessionManagementResponse, LogExportResponse, LogAnalysisResponse,
    LogAnalysisSimpleResponse
)

# 로그인 로그 라우터
log_router = APIRouter(
    prefix="/logs",
    tags=["로그인 로그 관리"],
    responses={404: {"description": "Not found"}}
)

# 서비스 인스턴스는 각 함수 내에서 초기화됩니다


# ==================== 로그인 로그 기본 API ====================

@log_router.get("/", response_model=LoginLogPagination, summary="로그인 로그 목록 조회")
async def get_login_logs(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    ip_address: Optional[str] = Query(None, description="IP 주소"),
    login_result: Optional[str] = Query(None, description="로그인 결과 (SUCCESS/FAILURE)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그인 로그 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **user_id**: 사용자 ID로 필터링
    - **ip_address**: IP 주소로 필터링
    - **login_result**: 로그인 결과로 필터링
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    """
    try:
        log_service = LoginLogService()
        search_params = LoginLogSearchParams(
            user_id=user_id,
            ip_address=ip_address,
            login_result=login_result,
            start_date=start_date,
            end_date=end_date
        )
        
        logs = log_service.search_logs(
            db=db,
            search_params=search_params,
            skip=skip,
            limit=limit
        )
        
        total_count = log_service.count(db=db)
        
        # 페이지네이션 정보 계산
        pages = (total_count + limit - 1) // limit
        page = (skip // limit) + 1
        
        return LoginLogPagination(
            items=logs,
            total=total_count,
            page=page,
            size=limit,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 로그 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/recent", response_model=List[LoginLogResponse], summary="최근 로그인 로그 조회")
async def get_recent_logs(
    hours: int = Query(24, ge=1, le=168, description="조회 시간 (시간)"),
    limit: int = Query(50, ge=1, le=200, description="조회할 최대 레코드 수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    최근 로그인 로그를 조회합니다.
    
    - **hours**: 조회 시간 (시간)
    - **limit**: 조회할 최대 레코드 수
    """
    try:
        log_service = LoginLogService()
        recent_logs = log_service.get_recent_logs(
            db=db,
            hours=hours,
            limit=limit
        )
        
        return recent_logs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최근 로그인 로그 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/user/{user_id}", response_model=List[LoginLogResponse], summary="사용자별 로그인 로그 조회")
async def get_user_logs(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    limit: int = Query(100, ge=1, le=500, description="조회할 최대 레코드 수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 로그인 로그를 조회합니다.
    
    - **user_id**: 사용자 ID
    - **days**: 조회 기간 (일)
    - **limit**: 조회할 최대 레코드 수
    """
    try:
        log_service = LoginLogService()
        user_logs = log_service.get_user_logs(
            db=db,
            user_id=user_id,
            days=days,
            limit=limit
        )
        
        return user_logs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자별 로그인 로그 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/failed", response_model=List[LoginLogResponse], summary="실패한 로그인 시도 조회")
async def get_failed_attempts(
    hours: int = Query(24, ge=1, le=168, description="조회 시간 (시간)"),
    limit: int = Query(100, ge=1, le=500, description="조회할 최대 레코드 수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    실패한 로그인 시도를 조회합니다.
    
    - **hours**: 조회 시간 (시간)
    - **limit**: 조회할 최대 레코드 수
    """
    try:
        log_service = LoginLogService()
        failed_attempts = log_service.get_failed_attempts(
            db=db,
            hours=hours,
            limit=limit
        )
        
        return failed_attempts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"실패한 로그인 시도 조회 중 오류가 발생했습니다: {str(e)}"
        )



@log_router.post("/", response_model=LoginLogResponse, summary="로그인 로그 생성")
async def create_login_log(
    log_data: LoginLogCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 로그인 로그를 생성합니다.
    
    - **user_id**: 사용자 ID
    - **ip_address**: IP 주소
    - **user_agent**: 사용자 에이전트
    - **login_result**: 로그인 결과 (SUCCESS/FAILURE)
    - **failure_reason**: 실패 사유 (실패 시)
    """
    try:
        log_service = LoginLogService()
        log = log_service.create_login_log(
            db=db,
            user_id=log_data.user_id,
            ip_address=log_data.login_ip,
            user_agent=getattr(log_data, 'user_agent', None),
            login_status=log_data.login_result,
            error_message=getattr(log_data, 'failure_reason', None)
        )
        return log
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 로그 생성 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.put("/{log_id}", response_model=LoginLogResponse, summary="로그인 로그 수정")
async def update_login_log(
    log_id: int,
    log_data: LoginLogUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그인 로그 정보를 수정합니다.
    
    - **log_id**: 수정할 로그 ID
    """
    try:
        log_service = LoginLogService()
        log = log_service.get_by_log_id(db=db, log_id=log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"로그인 로그를 찾을 수 없습니다: {log_id}"
            )
        
        updated_log = log_service.update(
            db=db,
            db_obj=log,
            obj_in=log_data
        )
        
        return updated_log
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 로그 수정 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.delete("/{log_id}", summary="로그인 로그 삭제")
async def delete_login_log(
    log_id: int,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그인 로그를 삭제합니다.
    
    - **log_id**: 삭제할 로그 ID
    """
    try:
        log_service = LoginLogService()
        log = log_service.get_by_log_id(db=db, log_id=log_id)
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"로그인 로그를 찾을 수 없습니다: {log_id}"
            )
        
        log_service.delete(db=db, id=log_id)
        
        return {"message": f"로그인 로그가 삭제되었습니다: {log_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 로그 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 로그 통계 및 분석 API ====================

@log_router.get("/statistics/overview", response_model=LoginLogStatistics, summary="로그인 통계 조회")
async def get_login_statistics(
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    로그인 통계 정보를 조회합니다.
    
    - **days**: 조회 기간 (일)
    """
    try:
        log_service = LoginLogService()
        statistics = log_service.get_login_statistics(db=db, days=days)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/statistics/daily", response_model=dict, summary="일별 로그인 통계 조회")
async def get_daily_statistics(
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    일별 로그인 통계를 조회합니다.
    
    - **days**: 조회 기간 (일)
    """
    try:
        log_service = LoginLogService()
        daily_stats = log_service.get_daily_login_stats(db=db, days=days)
        return daily_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"일별 로그인 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/statistics/hourly", response_model=dict, summary="시간별 로그인 통계 조회")
async def get_hourly_statistics(
    days: int = Query(7, ge=1, le=30, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    시간별 로그인 통계를 조회합니다.
    
    - **days**: 조회 기간 (일)
    """
    try:
        log_service = LoginLogService()
        hourly_stats = log_service.get_hourly_login_stats(db=db, days=days)
        return hourly_stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"시간별 로그인 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/statistics/top-ips", response_model=List[dict], summary="상위 IP 주소 통계 조회")
async def get_top_ip_statistics(
    days: int = Query(30, ge=1, le=365, description="조회 기간 (일)"),
    limit: int = Query(10, ge=1, le=50, description="조회할 최대 레코드 수"),
    db: Session = Depends(get_db)
):
    """
    상위 IP 주소 통계를 조회합니다.
    
    - **days**: 조회 기간 (일)
    - **limit**: 조회할 최대 레코드 수
    """
    try:
        log_service = LoginLogService()
        top_ips = log_service.get_top_ip_addresses(db=db, days=days, limit=limit)
        return top_ips
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"상위 IP 주소 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 보안 및 모니터링 API ====================

@log_router.get("/security/alerts", response_model=List[SecurityAlertResponse], summary="보안 알림 조회")
async def get_security_alerts(
    hours: int = Query(24, ge=1, le=168, description="조회 시간 (시간)"),
    alert_type: Optional[str] = Query(None, description="알림 유형"),
    db: Session = Depends(get_db)
):
    """
    보안 알림을 조회합니다.
    
    - **hours**: 조회 시간 (시간)
    - **alert_type**: 알림 유형으로 필터링
    """
    try:
        log_service = LoginLogService()
        alerts = log_service.get_security_alerts(
            db=db,
            hours=hours,
            alert_type=alert_type
        )
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보안 알림 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/security/suspicious", response_model=List[SuspiciousActivityResponse], summary="의심스러운 활동 조회")
async def get_suspicious_activities(
    hours: int = Query(24, ge=1, le=168, description="조회 시간 (시간)"),
    severity: Optional[str] = Query(None, description="심각도 (HIGH/MEDIUM/LOW)"),
    db: Session = Depends(get_db)
):
    """
    의심스러운 활동을 조회합니다.
    
    - **hours**: 조회 시간 (시간)
    - **severity**: 심각도로 필터링
    """
    try:
        log_service = LoginLogService()
        suspicious_activities = log_service.get_suspicious_activities(
            db=db,
            hours=hours,
            severity=severity
        )
        
        return suspicious_activities
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"의심스러운 활동 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/security/repeated-failures", response_model=List[dict], summary="반복 실패 시도 조회")
async def get_repeated_failures(
    hours: int = Query(24, ge=1, le=168, description="조회 시간 (시간)"),
    min_attempts: int = Query(5, ge=3, le=50, description="최소 시도 횟수"),
    db: Session = Depends(get_db)
):
    """
    반복된 로그인 실패 시도를 조회합니다.
    
    - **hours**: 조회 시간 (시간)
    - **min_attempts**: 최소 시도 횟수
    """
    try:
        log_service = LoginLogService()
        repeated_failures = log_service.get_repeated_login_failures(
            db=db,
            hours=hours,
            min_attempts=min_attempts
        )
        
        return repeated_failures
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"반복 실패 시도 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/security/unusual-times", response_model=List[dict], summary="비정상 시간대 로그인 조회")
async def get_unusual_login_times(
    days: int = Query(7, ge=1, le=30, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    비정상적인 시간대의 로그인을 조회합니다.
    
    - **days**: 조회 기간 (일)
    """
    try:
        log_service = LoginLogService()
        unusual_logins = log_service.get_unusual_login_times(db=db, days=days)
        return unusual_logins
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비정상 시간대 로그인 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/security/new-ip-logins", response_model=List[dict], summary="새로운 IP 로그인 조회")
async def get_new_ip_logins(
    days: int = Query(7, ge=1, le=30, description="조회 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    새로운 IP 주소에서의 로그인을 조회합니다.
    
    - **days**: 조회 기간 (일)
    """
    try:
        log_service = LoginLogService()
        new_ip_logins = log_service.get_new_ip_logins(db=db, days=days)
        return new_ip_logins
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"새로운 IP 로그인 조회 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 세션 관리 API ====================

@log_router.get("/sessions/active", response_model=List[SessionManagementResponse], summary="활성 세션 조회")
async def get_active_sessions(
    db: Session = Depends(get_db)
):
    """
    현재 활성 세션을 조회합니다.
    """
    try:
        log_service = LoginLogService()
        active_sessions = log_service.get_active_sessions(db=db)
        return active_sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 세션 조회 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/sessions/user/{user_id}", response_model=List[SessionManagementResponse], summary="사용자 세션 조회")
async def get_user_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 사용자의 세션을 조회합니다.
    
    - **user_id**: 사용자 ID
    """
    try:
        log_service = LoginLogService()
        user_sessions = log_service.get_user_sessions(db=db, user_id=user_id)
        return user_sessions
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 세션 조회 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 로그 관리 API ====================

@log_router.post("/cleanup", summary="오래된 로그 정리")
async def cleanup_old_logs(
    days: int = Query(90, ge=30, le=365, description="보관 기간 (일)"),
    db: Session = Depends(get_db)
):
    """
    지정된 기간보다 오래된 로그를 정리합니다.
    
    - **days**: 보관 기간 (일)
    """
    try:
        log_service = LoginLogService()
        deleted_count = log_service.cleanup_old_logs(db=db, days=days)
        
        return {"message": f"{deleted_count}개의 오래된 로그가 정리되었습니다"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"오래된 로그 정리 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/export", response_model=LogExportResponse, summary="로그 데이터 내보내기")
async def export_logs(
    format: str = Query("csv", description="내보내기 형식 (csv, json, excel)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    user_id: Optional[str] = Query(None, description="사용자 ID"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그 데이터를 내보냅니다.
    
    - **format**: 내보내기 형식 (csv, json, excel)
    - **start_date**: 시작 날짜
    - **end_date**: 종료 날짜
    - **user_id**: 사용자 ID로 필터링
    """
    try:
        log_service = LoginLogService()
        export_data = log_service.export_logs(
            db=db,
            format=format,
            start_date=start_date,
            end_date=end_date,
            user_id=user_id
        )
        
        return {"status": "success", "data": export_data, "format": format}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그 데이터 내보내기 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/analysis", response_model=LogAnalysisSimpleResponse, summary="로그 분석")
async def analyze_logs(
    days: int = Query(30, ge=1, le=365, description="분석 기간 (일)"),
    analysis_type: str = Query("overview", description="분석 유형 (overview, security, performance)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    로그 데이터를 분석합니다.
    
    - **days**: 분석 기간 (일)
    - **analysis_type**: 분석 유형
    """
    try:
        log_service = LoginLogService()
        analysis_result = log_service.analyze_logs(
            db=db,
            days=days,
            analysis_type=analysis_type
        )
        
        return {"status": "success", "analysis_type": analysis_type, "days": days, "result": analysis_result}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그 분석 중 오류가 발생했습니다: {str(e)}"
        )


@log_router.get("/{log_id}", response_model=LoginLogResponse, summary="로그인 로그 상세 조회")
async def get_login_log(
    log_id: int,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 로그인 로그의 상세 정보를 조회합니다.
    
    - **log_id**: 로그 ID
    """
    try:
        log_service = LoginLogService()
        log = log_service.get_by_log_id(db=db, log_id=log_id)
        
        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"로그인 로그를 찾을 수 없습니다: {log_id}"
            )
        
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 로그 조회 중 오류가 발생했습니다: {str(e)}"
        )
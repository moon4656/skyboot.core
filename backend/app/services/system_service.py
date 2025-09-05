"""시스템 관련 서비스 로직

시스템 로그, 웹 로그, 프로그램 목록 관련 CRUD 및 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc, text
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
import psutil
import time

from app.models.system_models import SysLog, WebLog, ProgrmList
from app.schemas.system_schemas import (
    SysLogCreate, SysLogUpdate,
    WebLogCreate, WebLogUpdate,
    ProgrmListCreate, ProgrmListUpdate,
    LogSearchParams, LogStatistics, ProgrmSearchParams,
    SystemHealthCheck, DashboardSummary
)
from app.services.base_service import BaseService
from app.utils.auth import logger

# 시스템 시작 시간 (서버 가동시간 계산용)
SYSTEM_START_TIME = time.time()


class SysLogService(BaseService[SysLog, SysLogCreate, SysLogUpdate]):
    """시스템 로그 서비스 클래스"""
    
    def __init__(self):
        super().__init__(SysLog)
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[SysLog], int]:
        """
        시스템 로그 목록을 페이지네이션으로 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            
        Returns:
            (로그 목록, 전체 개수) 튜플
        """
        try:
            query = db.query(self.model)
            total = query.count()
            items = query.order_by(desc(SysLog.occrrnc_de)).offset(skip).limit(limit).all()
            return items, total
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"시스템 로그 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    def create(self, db: Session, obj_in: SysLogCreate, current_user_id: Optional[str] = None) -> SysLog:
        """시스템 로그 생성"""
        obj_data = obj_in.model_dump()
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        obj_data["rqest_de"] = obj_data.get("rqest_de", datetime.now())
        
        db_obj = SysLog(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_log_entry(
        self,
        db: Session,
        requst_id: str,
        rqester_id: Optional[str] = None,
        rqester_ip: Optional[str] = None,
        rqester_nm: Optional[str] = None,
        trget_menu_nm: Optional[str] = None,
        process_se_code: Optional[str] = None,
        process_cn: Optional[str] = None,
        process_time: Optional[Decimal] = None
    ) -> SysLog:
        """시스템 로그 항목 생성 (편의 메서드)"""
        log_data = SysLogCreate(
            requst_id=requst_id,
            rqester_id=rqester_id,
            rqester_ip=rqester_ip,
            rqester_nm=rqester_nm,
            trget_menu_nm=trget_menu_nm,
            process_se_code=process_se_code,
            process_cn=process_cn,
            process_time=process_time,
            rqest_de=datetime.now()
        )
        return self.create(db, log_data)
    
    def search_logs(
        self,
        db: Session,
        search_params: LogSearchParams,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[SysLog], int]:
        """시스템 로그 검색"""
        query = db.query(SysLog)
        
        # 검색 조건 적용
        if search_params.rqester_id:
            query = query.filter(SysLog.rqester_id.ilike(f"%{search_params.rqester_id}%"))
        
        if search_params.rqester_ip:
            query = query.filter(SysLog.rqester_ip == search_params.rqester_ip)
        
        if search_params.rqester_nm:
            query = query.filter(SysLog.rqester_nm.ilike(f"%{search_params.rqester_nm}%"))
        
        if search_params.trget_menu_nm:
            query = query.filter(SysLog.trget_menu_nm.ilike(f"%{search_params.trget_menu_nm}%"))
        
        if search_params.process_se_code:
            query = query.filter(SysLog.process_se_code == search_params.process_se_code)
        
        if search_params.start_date:
            query = query.filter(SysLog.rqest_de >= search_params.start_date)
        
        if search_params.end_date:
            query = query.filter(SysLog.rqest_de <= search_params.end_date)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        logs = query.order_by(desc(SysLog.rqest_de)).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_logs_by_user(self, db: Session, user_id: str, days: int = 30) -> List[SysLog]:
        """특정 사용자의 로그 조회"""
        start_date = datetime.now() - timedelta(days=days)
        return db.query(SysLog).filter(
            and_(
                SysLog.rqester_id == user_id,
                SysLog.rqest_de >= start_date
            )
        ).order_by(desc(SysLog.rqest_de)).all()
    
    def get_error_logs(self, db: Session, days: int = 7) -> List[SysLog]:
        """오류 로그 조회"""
        start_date = datetime.now() - timedelta(days=days)
        return db.query(SysLog).filter(
            and_(
                SysLog.process_se_code.in_(['ERROR', 'EXCEPTION', 'FAIL']),
                SysLog.rqest_de >= start_date
            )
        ).order_by(desc(SysLog.rqest_de)).all()


class WebLogService(BaseService[WebLog, WebLogCreate, WebLogUpdate]):
    """웹 로그 서비스 클래스"""
    
    def __init__(self):
        super().__init__(WebLog)
    
    def get_multi(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[WebLog], int]:
        """
        웹 로그 목록을 페이지네이션으로 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 개수
            limit: 조회할 개수
            
        Returns:
            (로그 목록, 전체 개수) 튜플
        """
        try:
            query = db.query(self.model)
            total = query.count()
            items = query.order_by(desc(WebLog.occrrnc_de)).offset(skip).limit(limit).all()
            return items, total
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"웹 로그 조회 중 오류가 발생했습니다: {str(e)}"
            )
    
    def create(self, db: Session, obj_in: WebLogCreate, current_user_id: Optional[str] = None) -> WebLog:
        """웹 로그 생성"""
        obj_data = obj_in.model_dump()
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        obj_data["rqest_de"] = obj_data.get("rqest_de", datetime.now())
        
        db_obj = WebLog(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_web_log_entry(
        self,
        db: Session,
        requst_id: str,
        rqester_id: Optional[str] = None,
        rqester_ip: Optional[str] = None,
        rqester_nm: Optional[str] = None,
        trget_menu_nm: Optional[str] = None,
        process_se_code: Optional[str] = None,
        process_cn: Optional[str] = None,
        process_time: Optional[Decimal] = None
    ) -> WebLog:
        """웹 로그 항목 생성 (편의 메서드)"""
        log_data = WebLogCreate(
            requst_id=requst_id,
            rqester_id=rqester_id,
            rqester_ip=rqester_ip,
            rqester_nm=rqester_nm,
            trget_menu_nm=trget_menu_nm,
            process_se_code=process_se_code,
            process_cn=process_cn,
            process_time=process_time,
            rqest_de=datetime.now()
        )
        return self.create(db, log_data)
    
    def search_logs(
        self,
        db: Session,
        search_params: LogSearchParams,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[WebLog], int]:
        """웹 로그 검색"""
        query = db.query(WebLog)
        
        # 검색 조건 적용
        if search_params.rqester_id:
            query = query.filter(WebLog.rqester_id.ilike(f"%{search_params.rqester_id}%"))
        
        if search_params.rqester_ip:
            query = query.filter(WebLog.rqester_ip == search_params.rqester_ip)
        
        if search_params.rqester_nm:
            query = query.filter(WebLog.rqester_nm.ilike(f"%{search_params.rqester_nm}%"))
        
        if search_params.trget_menu_nm:
            query = query.filter(WebLog.trget_menu_nm.ilike(f"%{search_params.trget_menu_nm}%"))
        
        if search_params.process_se_code:
            query = query.filter(WebLog.process_se_code == search_params.process_se_code)
        
        if search_params.start_date:
            query = query.filter(WebLog.rqest_de >= search_params.start_date)
        
        if search_params.end_date:
            query = query.filter(WebLog.rqest_de <= search_params.end_date)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        logs = query.order_by(desc(WebLog.rqest_de)).offset(skip).limit(limit).all()
        
        return logs, total
    
    def get_popular_pages(self, db: Session, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """인기 페이지 조회"""
        start_date = datetime.now() - timedelta(days=days)
        
        popular_pages = db.query(
            WebLog.trget_menu_nm,
            func.count(WebLog.requst_id).label('visit_count')
        ).filter(
            and_(
                WebLog.rqest_de >= start_date,
                WebLog.trget_menu_nm.isnot(None)
            )
        ).group_by(WebLog.trget_menu_nm).order_by(
            desc('visit_count')
        ).limit(limit).all()
        
        return [
            {"menu_name": menu_name, "visit_count": count}
            for menu_name, count in popular_pages
        ]
    
    def get_hourly_traffic(self, db: Session, date: datetime) -> List[Dict[str, Any]]:
        """시간별 트래픽 조회"""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        
        hourly_traffic = db.query(
            func.extract('hour', WebLog.rqest_de).label('hour'),
            func.count(WebLog.requst_id).label('request_count')
        ).filter(
            and_(
                WebLog.rqest_de >= start_date,
                WebLog.rqest_de < end_date
            )
        ).group_by(
            func.extract('hour', WebLog.rqest_de)
        ).order_by('hour').all()
        
        return [
            {"hour": int(hour), "request_count": count}
            for hour, count in hourly_traffic
        ]


class ProgrmListService(BaseService[ProgrmList, ProgrmListCreate, ProgrmListUpdate]):
    """프로그램 목록 서비스 클래스"""
    
    def __init__(self):
        super().__init__(ProgrmList)
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> Tuple[List[ProgrmList], int]:
        """
        여러 레코드 조회 (페이지네이션 지원) - 총 개수와 함께 반환
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            filters: 필터 조건 딕셔너리
            order_by: 정렬 기준 컬럼명
            order_desc: 내림차순 정렬 여부
            
        Returns:
            (조회된 모델 인스턴스 리스트, 총 개수) 튜플
        """
        try:
            query = db.query(self.model)
            
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            # LIKE 검색
                            query = query.filter(getattr(self.model, key).like(value))
                        else:
                            # 정확한 매치
                            query = query.filter(getattr(self.model, key) == value)
            
            # 전체 개수 조회
            total = query.count()
            
            # 정렬 적용
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            
            # 페이지네이션 적용
            items = query.offset(skip).limit(limit).all()
            
            return items, total
            
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def create(self, db: Session, obj_in: ProgrmListCreate, current_user_id: Optional[str] = None) -> ProgrmList:
        """프로그램 목록 생성"""
        # 중복 프로그램명 확인
        existing_program = db.query(ProgrmList).filter(
            ProgrmList.progrm_file_nm == obj_in.progrm_file_nm
        ).first()
        if existing_program:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 프로그램명입니다."
            )
        
        obj_data = obj_in.model_dump()
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        
        # 모델에 존재하지 않는 필드 제거
        obj_data.pop("progrm_nm", None)
        
        db_obj = ProgrmList(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def search_programs(
        self,
        db: Session,
        search_params: ProgrmSearchParams,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[ProgrmList], int]:
        """프로그램 검색"""
        query = db.query(ProgrmList)
        
        # 검색 조건 적용
        if search_params.progrm_nm:
            query = query.filter(ProgrmList.progrm_file_nm.ilike(f"%{search_params.progrm_nm}%"))
        
        if search_params.progrm_korean_nm:
            query = query.filter(ProgrmList.progrm_korean_nm.ilike(f"%{search_params.progrm_korean_nm}%"))
        
        if search_params.progrm_file_nm:
            query = query.filter(ProgrmList.progrm_file_nm.ilike(f"%{search_params.progrm_file_nm}%"))
        
        if search_params.url:
            query = query.filter(ProgrmList.url.ilike(f"%{search_params.url}%"))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        programs = query.order_by(asc(ProgrmList.progrm_file_nm)).offset(skip).limit(limit).all()
        
        return programs, total
    
    def get_by_program_name(self, db: Session, program_name: str) -> Optional[ProgrmList]:
        """프로그램명으로 조회"""
        return db.query(ProgrmList).filter(
            ProgrmList.progrm_file_nm == program_name
        ).first()
    
    def get_by_file_name(self, db: Session, file_name: str) -> Optional[ProgrmList]:
        """프로그램파일명으로 조회"""
        return db.query(ProgrmList).filter(
            ProgrmList.progrm_file_nm == file_name
        ).first()
    
    def get_programs_by_path(self, db: Session, path: str) -> List[ProgrmList]:
        """경로로 프로그램 조회"""
        return db.query(ProgrmList).filter(
            ProgrmList.progrm_stre_path.ilike(f"%{path}%")
        ).order_by(asc(ProgrmList.progrm_file_nm)).all()
    
    def remove(self, db: Session, file_name: str) -> bool:
        """프로그램 삭제"""
        program = self.get_by_file_name(db, file_name)
        if program:
            db.delete(program)
            db.commit()
            return True
        return False


class SystemMonitoringService:
    """시스템 모니터링 서비스 클래스"""
    
    def __init__(self):
        self.syslog_service = SysLogService()
        self.weblog_service = WebLogService()
    
    def get_system_health_check(self, db: Session) -> SystemHealthCheck:
        """시스템 상태 확인"""
        try:
            # 데이터베이스 상태 확인
            db.execute(text("SELECT 1"))
            database_status = "정상"
        except Exception:
            database_status = "오류"
        
        # API 상태 (현재 메서드가 실행되고 있으므로 정상)
        api_status = "정상"
        
        # 오늘 로그 수 조회
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        log_count_today = db.query(func.count(SysLog.requst_id)).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow
            )
        ).scalar() or 0
        
        # 오늘 오류 수 조회
        error_count_today = db.query(func.count(SysLog.requst_id)).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow,
                SysLog.process_se_code.in_(['ERROR', 'EXCEPTION', 'FAIL'])
            )
        ).scalar() or 0
        
        # 오늘 활성 사용자 수 (로그에 기록된 고유 사용자)
        active_users_today = db.query(
            func.count(func.distinct(SysLog.rqester_id))
        ).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow,
                SysLog.rqester_id.isnot(None)
            )
        ).scalar() or 0
        
        # 시스템 가동시간
        uptime_seconds = time.time() - SYSTEM_START_TIME
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        system_uptime = f"{uptime_hours}시간 {uptime_minutes}분"
        
        # 메모리 및 CPU 사용률
        try:
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent(interval=1)
        except Exception:
            memory_usage = 0.0
            cpu_usage = 0.0
        
        return SystemHealthCheck(
            database_status=database_status,
            api_status=api_status,
            log_count_today=log_count_today,
            error_count_today=error_count_today,
            active_users_today=active_users_today,
            system_uptime=system_uptime,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage
        )
    
    def get_log_statistics(self, db: Session, days: int = 30) -> LogStatistics:
        """로그 통계 조회"""
        start_date = datetime.now() - timedelta(days=days)
        
        # 전체 요청 수
        total_requests = db.query(func.count(SysLog.requst_id)).filter(
            SysLog.rqest_de >= start_date
        ).scalar() or 0
        
        # 고유 사용자 수
        unique_users = db.query(
            func.count(func.distinct(SysLog.rqester_id))
        ).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.rqester_id.isnot(None)
            )
        ).scalar() or 0
        
        # 시간별 요청 수
        hourly_requests = db.query(
            func.extract('hour', SysLog.rqest_de).label('hour'),
            func.count(SysLog.requst_id).label('count')
        ).filter(
            SysLog.rqest_de >= start_date
        ).group_by(
            func.extract('hour', SysLog.rqest_de)
        ).all()
        requests_by_hour = {str(int(hour)): count for hour, count in hourly_requests}
        
        # 메뉴별 요청 수
        menu_requests = db.query(
            SysLog.trget_menu_nm,
            func.count(SysLog.requst_id).label('count')
        ).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.trget_menu_nm.isnot(None)
            )
        ).group_by(SysLog.trget_menu_nm).all()
        requests_by_menu = {menu: count for menu, count in menu_requests}
        
        # 처리구분별 요청 수
        process_requests = db.query(
            SysLog.process_se_code,
            func.count(SysLog.requst_id).label('count')
        ).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.process_se_code.isnot(None)
            )
        ).group_by(SysLog.process_se_code).all()
        requests_by_process_type = {process: count for process, count in process_requests}
        
        # 평균 처리시간
        avg_process_time = db.query(
            func.avg(SysLog.process_time)
        ).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.process_time.isnot(None)
            )
        ).scalar() or 0.0
        
        # 상위 사용자 목록
        top_users = db.query(
            SysLog.rqester_id,
            SysLog.rqester_nm,
            func.count(SysLog.requst_id).label('request_count')
        ).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.rqester_id.isnot(None)
            )
        ).group_by(
            SysLog.rqester_id, SysLog.rqester_nm
        ).order_by(
            desc('request_count')
        ).limit(10).all()
        
        top_users_list = [
            {
                "user_id": user_id,
                "user_name": user_name or "알 수 없음",
                "request_count": count
            }
            for user_id, user_name, count in top_users
        ]
        
        # 오류율 계산
        error_requests = db.query(func.count(SysLog.requst_id)).filter(
            and_(
                SysLog.rqest_de >= start_date,
                SysLog.process_se_code.in_(['ERROR', 'EXCEPTION', 'FAIL'])
            )
        ).scalar() or 0
        
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0.0
        
        return LogStatistics(
            total_requests=total_requests,
            unique_users=unique_users,
            requests_by_hour=requests_by_hour,
            requests_by_menu=requests_by_menu,
            requests_by_process_type=requests_by_process_type,
            average_process_time=float(avg_process_time),
            top_users=top_users_list,
            error_rate=error_rate
        )
    
    def get_dashboard_summary(self, db: Session) -> DashboardSummary:
        """대시보드 요약 정보 조회"""
        from app.models.user_models import UserInfo
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        # 전체 사용자 수
        total_users = db.query(func.count(UserInfo.user_id)).scalar() or 0
        
        # 오늘 활성 사용자 수
        active_users_today = db.query(
            func.count(func.distinct(SysLog.rqester_id))
        ).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow,
                SysLog.rqester_id.isnot(None)
            )
        ).scalar() or 0
        
        # 오늘 총 요청 수
        total_requests_today = db.query(func.count(SysLog.requst_id)).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow
            )
        ).scalar() or 0
        
        # 오늘 오류 요청 수
        error_requests_today = db.query(func.count(SysLog.requst_id)).filter(
            and_(
                SysLog.rqest_de >= today,
                SysLog.rqest_de < tomorrow,
                SysLog.process_se_code.in_(['ERROR', 'EXCEPTION', 'FAIL'])
            )
        ).scalar() or 0
        
        # 인기 메뉴 목록 (최근 7일)
        week_ago = datetime.now() - timedelta(days=7)
        popular_menus = db.query(
            SysLog.trget_menu_nm,
            func.count(SysLog.requst_id).label('count')
        ).filter(
            and_(
                SysLog.rqest_de >= week_ago,
                SysLog.trget_menu_nm.isnot(None)
            )
        ).group_by(SysLog.trget_menu_nm).order_by(
            desc('count')
        ).limit(5).all()
        
        popular_menus_list = [
            {"menu_name": menu, "access_count": count}
            for menu, count in popular_menus
        ]
        
        # 최근 활동 목록
        recent_activities = db.query(SysLog).filter(
            SysLog.rqester_id.isnot(None)
        ).order_by(desc(SysLog.rqest_de)).limit(10).all()
        
        recent_activities_list = [
            {
                "user_id": log.rqester_id,
                "user_name": log.rqester_nm or "알 수 없음",
                "menu_name": log.trget_menu_nm or "알 수 없음",
                "action": log.process_se_code or "알 수 없음",
                "timestamp": log.rqest_de.isoformat() if log.rqest_de else None
            }
            for log in recent_activities
        ]
        
        # 시스템 알림 목록 (최근 오류 로그)
        system_alerts = db.query(SysLog).filter(
            and_(
                SysLog.rqest_de >= week_ago,
                SysLog.process_se_code.in_(['ERROR', 'EXCEPTION', 'FAIL'])
            )
        ).order_by(desc(SysLog.rqest_de)).limit(5).all()
        
        system_alerts_list = [
            {
                "type": "error",
                "message": log.process_cn or "시스템 오류 발생",
                "timestamp": log.rqest_de.isoformat() if log.rqest_de else None,
                "user_id": log.rqester_id
            }
            for log in system_alerts
        ]
        
        return DashboardSummary(
            total_users=total_users,
            active_users_today=active_users_today,
            total_requests_today=total_requests_today,
            error_requests_today=error_requests_today,
            popular_menus=popular_menus_list,
            recent_activities=recent_activities_list,
            system_alerts=system_alerts_list
        )
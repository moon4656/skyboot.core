"""로그 관련 서비스

로그인 로그 관리를 위한 서비스 클래스를 정의합니다.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, timedelta
import logging

from app.models.log_models import LoginLog
from app.schemas.log_schemas import LoginLogCreate, LoginLogUpdate
from .base_service import BaseService

logger = logging.getLogger(__name__)


class LoginLogService(BaseService[LoginLog, LoginLogCreate, LoginLogUpdate]):
    """로그인 로그 서비스
    
    로그인 로그 관리, 보안 모니터링, 통계 분석 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(LoginLog)
    
    def get_by_log_id(self, db: Session, log_id: int) -> Optional[LoginLog]:
        """
        로그 ID로 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            log_id: 로그 ID
            
        Returns:
            로그인 로그 또는 None
        """
        try:
            return db.query(LoginLog).filter(
                LoginLog.log_id == log_id
            ).first()
        except Exception as e:
            logger.error(f"❌ 로그인 로그 조회 실패 - log_id: {log_id}, 오류: {str(e)}")
            raise
    
    def get_user_login_logs(
        self, 
        db: Session, 
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        사용자별 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            로그인 로그 목록
        """
        try:
            query = db.query(LoginLog).filter(
                LoginLog.user_id == user_id
            )
            
            # 날짜 범위 필터
            if start_date:
                query = query.filter(LoginLog.login_dt >= start_date)
            if end_date:
                query = query.filter(LoginLog.login_dt <= end_date)
            
            return query.order_by(desc(LoginLog.login_dt)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 사용자 로그인 로그 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_recent_login_logs(
        self, 
        db: Session, 
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        최근 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            hours: 조회할 시간 범위 (시간)
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            최근 로그인 로그 목록
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            return db.query(LoginLog).filter(
                LoginLog.login_dt >= cutoff_time
            ).order_by(desc(LoginLog.login_dt)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 최근 로그인 로그 조회 실패 - hours: {hours}, 오류: {str(e)}")
            raise
    
    def get_failed_login_attempts(
        self, 
        db: Session,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        hours: int = 24,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        실패한 로그인 시도 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID (선택적)
            ip_address: IP 주소 (선택적)
            hours: 조회할 시간 범위 (시간)
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            실패한 로그인 시도 목록
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            query = db.query(LoginLog).filter(
                and_(
                    LoginLog.login_sttus == 'FAIL',
                    LoginLog.login_dt >= cutoff_time
                )
            )
            
            if user_id:
                query = query.filter(LoginLog.user_id == user_id)
            
            if ip_address:
                query = query.filter(LoginLog.ip_adres == ip_address)
            
            return query.order_by(desc(LoginLog.login_dt)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 실패한 로그인 시도 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_login_logs(
        self, 
        db: Session,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        login_status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        로그인 로그 검색
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            ip_address: IP 주소
            login_status: 로그인 상태 (SUCCESS, FAIL)
            start_date: 시작 날짜
            end_date: 종료 날짜
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 로그인 로그 목록
        """
        try:
            query = db.query(LoginLog)
            
            # 검색 조건 적용
            if user_id:
                query = query.filter(LoginLog.user_id.like(f"%{user_id}%"))
            
            if ip_address:
                query = query.filter(LoginLog.ip_adres.like(f"%{ip_address}%"))
            
            if login_status:
                query = query.filter(LoginLog.login_sttus == login_status)
            
            if start_date:
                query = query.filter(LoginLog.login_dt >= start_date)
            
            if end_date:
                query = query.filter(LoginLog.login_dt <= end_date)
            
            return query.order_by(desc(LoginLog.login_dt)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 로그인 로그 검색 실패 - 오류: {str(e)}")
            raise
    
    def create_login_log(
        self, 
        db: Session,
        user_id: str,
        ip_address: str,
        user_agent: Optional[str] = None,
        login_status: str = 'SUCCESS',
        error_message: Optional[str] = None
    ) -> LoginLog:
        """
        로그인 로그 생성
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            ip_address: IP 주소
            user_agent: 사용자 에이전트
            login_status: 로그인 상태 (SUCCESS, FAIL)
            error_message: 오류 메시지 (실패 시)
            
        Returns:
            생성된 로그인 로그
        """
        try:
            # 로그 ID 생성 (현재 시간 기반)
            log_id = datetime.now().strftime('%Y%m%d%H%M%S%f')[:17]
            
            log_data = {
                'log_id': log_id,
                'conect_id': user_id,
                'conect_ip': ip_address,
                'error_occrrnc_at': 'Y' if login_status in ['FAIL', 'ERROR'] else 'N',
                'error_code': '001' if login_status == 'FAIL' else ('500' if login_status == 'ERROR' else None),
                'frst_regist_pnttm': datetime.now()
            }
            
            login_log = self.create(db, log_data)
            
            logger.info(
                f"✅ 로그인 로그 생성 완료 - "
                f"user_id: {user_id}, status: {login_status}, ip: {ip_address}"
            )
            
            return login_log
            
        except Exception as e:
            logger.error(f"❌ 로그인 로그 생성 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_login_statistics(
        self, 
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        로그인 통계 조회
        
        Args:
            db: 데이터베이스 세션
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            로그인 통계 정보
        """
        try:
            # 기본 날짜 범위 설정 (최근 30일)
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            base_query = db.query(LoginLog).filter(
                and_(
                    LoginLog.login_dt >= start_date,
                    LoginLog.login_dt <= end_date
                )
            )
            
            # 전체 로그인 시도 수
            total_attempts = base_query.count()
            
            # 성공한 로그인 수
            successful_logins = base_query.filter(
                LoginLog.login_sttus == 'SUCCESS'
            ).count()
            
            # 실패한 로그인 수
            failed_logins = base_query.filter(
                LoginLog.login_sttus == 'FAIL'
            ).count()
            
            # 고유 사용자 수
            unique_users = base_query.filter(
                LoginLog.login_sttus == 'SUCCESS'
            ).distinct(LoginLog.user_id).count()
            
            # 고유 IP 수
            unique_ips = base_query.distinct(LoginLog.ip_adres).count()
            
            # 일별 로그인 통계
            daily_stats = db.query(
                func.date(LoginLog.login_dt).label('date'),
                func.count(LoginLog.log_id).label('total'),
                func.sum(
                    func.case(
                        [(LoginLog.login_sttus == 'SUCCESS', 1)],
                        else_=0
                    )
                ).label('success'),
                func.sum(
                    func.case(
                        [(LoginLog.login_sttus == 'FAIL', 1)],
                        else_=0
                    )
                ).label('fail')
            ).filter(
                and_(
                    LoginLog.login_dt >= start_date,
                    LoginLog.login_dt <= end_date
                )
            ).group_by(
                func.date(LoginLog.login_dt)
            ).order_by(
                func.date(LoginLog.login_dt)
            ).all()
            
            # 시간대별 로그인 통계
            hourly_stats = db.query(
                func.extract('hour', LoginLog.login_dt).label('hour'),
                func.count(LoginLog.log_id).label('count')
            ).filter(
                and_(
                    LoginLog.login_dt >= start_date,
                    LoginLog.login_dt <= end_date,
                    LoginLog.login_sttus == 'SUCCESS'
                )
            ).group_by(
                func.extract('hour', LoginLog.login_dt)
            ).order_by(
                func.extract('hour', LoginLog.login_dt)
            ).all()
            
            # 상위 IP 주소
            top_ips = db.query(
                LoginLog.ip_adres,
                func.count(LoginLog.log_id).label('count')
            ).filter(
                and_(
                    LoginLog.login_dt >= start_date,
                    LoginLog.login_dt <= end_date
                )
            ).group_by(
                LoginLog.ip_adres
            ).order_by(
                desc(func.count(LoginLog.log_id))
            ).limit(10).all()
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_attempts': total_attempts,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'success_rate': round((successful_logins / total_attempts * 100) if total_attempts > 0 else 0, 2),
                    'unique_users': unique_users,
                    'unique_ips': unique_ips
                },
                'daily_stats': [
                    {
                        'date': stat.date.isoformat(),
                        'total': stat.total,
                        'success': stat.success,
                        'fail': stat.fail
                    }
                    for stat in daily_stats
                ],
                'hourly_stats': [
                    {
                        'hour': int(stat.hour),
                        'count': stat.count
                    }
                    for stat in hourly_stats
                ],
                'top_ips': [
                    {
                        'ip_address': stat.ip_adres,
                        'count': stat.count
                    }
                    for stat in top_ips
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 로그인 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_security_alerts(
        self, 
        db: Session,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        보안 알림 조회
        
        Args:
            db: 데이터베이스 세션
            hours: 조회할 시간 범위 (시간)
            
        Returns:
            보안 알림 정보
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # 반복적인 로그인 실패 (같은 IP에서 5회 이상)
            repeated_failures = db.query(
                LoginLog.ip_adres,
                func.count(LoginLog.log_id).label('fail_count'),
                func.max(LoginLog.login_dt).label('last_attempt')
            ).filter(
                and_(
                    LoginLog.login_sttus == 'FAIL',
                    LoginLog.login_dt >= cutoff_time
                )
            ).group_by(
                LoginLog.ip_adres
            ).having(
                func.count(LoginLog.log_id) >= 5
            ).order_by(
                desc(func.count(LoginLog.log_id))
            ).all()
            
            # 비정상적인 시간대 로그인 (새벽 2-6시)
            unusual_time_logins = db.query(LoginLog).filter(
                and_(
                    LoginLog.login_sttus == 'SUCCESS',
                    LoginLog.login_dt >= cutoff_time,
                    or_(
                        func.extract('hour', LoginLog.login_dt) >= 2,
                        func.extract('hour', LoginLog.login_dt) <= 6
                    )
                )
            ).order_by(desc(LoginLog.login_dt)).limit(50).all()
            
            # 새로운 IP에서의 로그인
            recent_successful_ips = db.query(LoginLog.ip_adres).filter(
                and_(
                    LoginLog.login_sttus == 'SUCCESS',
                    LoginLog.login_dt >= cutoff_time
                )
            ).distinct().subquery()
            
            historical_ips = db.query(LoginLog.ip_adres).filter(
                and_(
                    LoginLog.login_sttus == 'SUCCESS',
                    LoginLog.login_dt < cutoff_time
                )
            ).distinct().subquery()
            
            new_ip_logins = db.query(LoginLog).filter(
                and_(
                    LoginLog.login_sttus == 'SUCCESS',
                    LoginLog.login_dt >= cutoff_time,
                    LoginLog.ip_adres.in_(recent_successful_ips),
                    ~LoginLog.ip_adres.in_(historical_ips)
                )
            ).order_by(desc(LoginLog.login_dt)).all()
            
            return {
                'period_hours': hours,
                'repeated_failures': [
                    {
                        'ip_address': failure.ip_adres,
                        'fail_count': failure.fail_count,
                        'last_attempt': failure.last_attempt.isoformat()
                    }
                    for failure in repeated_failures
                ],
                'unusual_time_logins': [
                    {
                        'log_id': login.log_id,
                        'user_id': login.user_id,
                        'ip_address': login.ip_adres,
                        'login_time': login.login_dt.isoformat()
                    }
                    for login in unusual_time_logins
                ],
                'new_ip_logins': [
                    {
                        'log_id': login.log_id,
                        'user_id': login.user_id,
                        'ip_address': login.ip_adres,
                        'login_time': login.login_dt.isoformat()
                    }
                    for login in new_ip_logins
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 보안 알림 조회 실패 - 오류: {str(e)}")
            raise
    
    def cleanup_old_logs(
        self, 
        db: Session,
        days_to_keep: int = 90
    ) -> int:
        """
        오래된 로그 정리
        
        Args:
            db: 데이터베이스 세션
            days_to_keep: 보관할 일수
            
        Returns:
            삭제된 로그 수
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            deleted_count = db.query(LoginLog).filter(
                LoginLog.login_dt < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"✅ 오래된 로그 정리 완료 - 삭제된 로그 수: {deleted_count}")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 오래된 로그 정리 실패 - 오류: {str(e)}")
            raise
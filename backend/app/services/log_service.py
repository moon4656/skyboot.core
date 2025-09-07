"""로그 관련 서비스

로그인 로그 관리를 위한 서비스 클래스를 정의합니다.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func, case
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
                query = query.filter(LoginLog.frst_regist_pnttm >= start_date)
            if end_date:
                query = query.filter(LoginLog.frst_regist_pnttm <= end_date)
            
            return query.order_by(desc(LoginLog.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
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
                LoginLog.frst_regist_pnttm >= cutoff_time
        ).order_by(desc(LoginLog.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
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
                    LoginLog.error_occrrnc_at == 'Y',
                    LoginLog.frst_regist_pnttm >= cutoff_time
                )
            )
            
            if user_id:
                query = query.filter(LoginLog.conect_id == user_id)
            
            if ip_address:
                query = query.filter(LoginLog.conect_ip == ip_address)
            
            return query.order_by(desc(LoginLog.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
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
                query = query.filter(LoginLog.conect_ip.like(f"%{ip_address}%"))
            
            if login_status:
                query = query.filter(LoginLog.error_occrrnc_at == ('Y' if login_status == 'FAIL' else 'N'))
            
            if start_date:
                query = query.filter(LoginLog.frst_regist_pnttm >= start_date)
            if end_date:
                query = query.filter(LoginLog.frst_regist_pnttm <= end_date)
            
            return query.order_by(desc(LoginLog.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
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
        days: int = 30,
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
            # 기본 날짜 범위 설정
            if not start_date:
                start_date = datetime.now() - timedelta(days=days)
            if not end_date:
                end_date = datetime.now()
            
            base_query = db.query(LoginLog).filter(
                and_(
                    LoginLog.frst_regist_pnttm >= start_date,
                    LoginLog.frst_regist_pnttm <= end_date
                )
            )
            
            # 전체 로그인 시도 수
            total_attempts = base_query.count()
            
            # 성공한 로그인 수
            successful_logins = base_query.filter(
                LoginLog.error_occrrnc_at == 'N'
            ).count()
            
            # 실패한 로그인 수
            failed_logins = base_query.filter(
                LoginLog.error_occrrnc_at == 'Y'
            ).count()
            
            # 고유 사용자 수
            unique_users = base_query.filter(
                LoginLog.error_occrrnc_at == 'N'
            ).distinct(LoginLog.conect_id).count()
            
            # 고유 IP 수
            unique_ips = base_query.distinct(LoginLog.conect_ip).count()
            
            # 일별 로그인 통계
            daily_stats = db.query(
                func.date(LoginLog.frst_regist_pnttm).label('date'),
                func.count(LoginLog.log_id).label('total'),
                func.sum(
                    case(
                        (LoginLog.error_occrrnc_at == 'N', 1),
                        else_=0
                    )
                ).label('success'),
                func.sum(
                    case(
                        (LoginLog.error_occrrnc_at == 'Y', 1),
                        else_=0
                    )
                ).label('fail')
            ).filter(
                and_(
                    LoginLog.frst_regist_pnttm >= start_date,
                    LoginLog.frst_regist_pnttm <= end_date
                )
            ).group_by(
                func.date(LoginLog.frst_regist_pnttm)
            ).order_by(
                func.date(LoginLog.frst_regist_pnttm)
            ).all()
            
            # 시간대별 로그인 통계
            hourly_stats = db.query(
                func.extract('hour', LoginLog.frst_regist_pnttm).label('hour'),
                func.count(LoginLog.log_id).label('count')
            ).filter(
                and_(
                    LoginLog.frst_regist_pnttm >= start_date,
                    LoginLog.frst_regist_pnttm <= end_date,
                    LoginLog.error_occrrnc_at == 'N'
                )
            ).group_by(
                func.extract('hour', LoginLog.frst_regist_pnttm)
            ).order_by(
                func.extract('hour', LoginLog.frst_regist_pnttm)
            ).all()
            
            # 상위 IP 주소
            top_ips = db.query(
                LoginLog.conect_ip,
                func.count(LoginLog.log_id).label('count')
            ).filter(
                and_(
                    LoginLog.frst_regist_pnttm >= start_date,
                    LoginLog.frst_regist_pnttm <= end_date
                )
            ).group_by(LoginLog.conect_ip).order_by(
                desc(func.count(LoginLog.log_id))
            ).limit(10).all()
            
            # 평균 세션 지속시간 계산 (임시값)
            avg_session_duration = 0.0
            
            # 최대 로그인 시간대 계산
            peak_login_hour = 0
            if hourly_stats:
                peak_hour_stat = max(hourly_stats, key=lambda x: x.count)
                peak_login_hour = int(peak_hour_stat.hour)
            
            return {
                'total_logins': total_attempts,
                'successful_logins': successful_logins,
                'failed_logins': failed_logins,
                'unique_users': unique_users,
                'unique_ips': unique_ips,
                'avg_session_duration': avg_session_duration,
                'peak_login_hour': peak_login_hour,
                'success_rate': round((successful_logins / total_attempts * 100) if total_attempts > 0 else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ 로그인 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_security_alerts(
        self, 
        db: Session,
        hours: int = 24,
        alert_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        보안 알림 조회
        
        Args:
            db: 데이터베이스 세션
            hours: 조회할 시간 범위 (시간)
            alert_type: 알림 유형 필터 (선택사항)
            
        Returns:
            보안 알림 리스트
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            alerts = []
            
            # 반복적인 로그인 실패 (같은 IP에서 5회 이상)
            repeated_failures = db.query(
                LoginLog.conect_ip,
                func.count(LoginLog.log_id).label('fail_count'),
                func.max(LoginLog.frst_regist_pnttm).label('last_attempt')
            ).filter(
                and_(
                    LoginLog.error_occrrnc_at == 'Y',
                    LoginLog.frst_regist_pnttm >= cutoff_time
                )
            ).group_by(
                LoginLog.conect_ip
            ).having(
                func.count(LoginLog.log_id) >= 5
            ).order_by(
                desc(func.count(LoginLog.log_id))
            ).all()
            
            # 반복 실패 알림 생성
            for failure in repeated_failures:
                if not alert_type or alert_type == 'repeated_failures':
                    alerts.append({
                        'alert_id': f"rf_{failure.conect_ip}_{int(failure.last_attempt.timestamp()) if failure.last_attempt else 0}",
                        'alert_type': 'repeated_failures',
                        'severity': 'high' if failure.fail_count >= 10 else 'medium',
                        'description': f"IP {failure.conect_ip}에서 {failure.fail_count}회 연속 로그인 실패",
                        'affected_user': 'unknown',
                        'source_ip': failure.conect_ip,
                        'detected_at': failure.last_attempt,
                        'status': 'active',
                        'actions_taken': ['IP 모니터링 강화']
                    })
            
            # 비정상적인 시간대 로그인 (새벽 2-6시)
            unusual_time_logins = db.query(LoginLog).filter(
                and_(
                    LoginLog.error_occrrnc_at == 'N',
                    LoginLog.frst_regist_pnttm >= cutoff_time,
                    func.extract('hour', LoginLog.frst_regist_pnttm) >= 2,
                    func.extract('hour', LoginLog.frst_regist_pnttm) <= 6
                )
            ).order_by(desc(LoginLog.frst_regist_pnttm)).limit(50).all()
            
            # 비정상 시간 로그인 알림 생성
            for login in unusual_time_logins:
                if not alert_type or alert_type == 'unusual_time':
                    alerts.append({
                        'alert_id': f"ut_{login.log_id}",
                        'alert_type': 'unusual_time',
                        'severity': 'medium',
                        'description': f"비정상 시간대({login.frst_regist_pnttm.hour}시) 로그인 감지",
                        'affected_user': login.conect_id or 'unknown',
                        'source_ip': login.conect_ip,
                        'detected_at': login.frst_regist_pnttm,
                        'status': 'active',
                        'actions_taken': ['사용자 알림 발송']
                    })
            
            # 새로운 IP에서의 로그인
            recent_successful_ips = [ip[0] for ip in db.query(LoginLog.conect_ip).filter(
                and_(
                    LoginLog.error_occrrnc_at == 'N',
                    LoginLog.frst_regist_pnttm >= cutoff_time
                )
            ).distinct().all()]
            
            historical_ips = [ip[0] for ip in db.query(LoginLog.conect_ip).filter(
                and_(
                    LoginLog.error_occrrnc_at == 'N',
                    LoginLog.frst_regist_pnttm < cutoff_time
                )
            ).distinct().all()]
            
            new_ips = [ip for ip in recent_successful_ips if ip not in historical_ips]
            
            new_ip_logins = db.query(LoginLog).filter(
                and_(
                    LoginLog.error_occrrnc_at == 'N',
                    LoginLog.frst_regist_pnttm >= cutoff_time,
                    LoginLog.conect_ip.in_(new_ips)
                )
            ).order_by(desc(LoginLog.frst_regist_pnttm)).all() if new_ips else []
            
            # 새로운 IP 로그인 알림 생성
            for login in new_ip_logins:
                if not alert_type or alert_type == 'new_ip':
                    alerts.append({
                        'alert_id': f"ni_{login.log_id}",
                        'alert_type': 'new_ip',
                        'severity': 'low',
                        'description': f"새로운 IP {login.conect_ip}에서 로그인",
                        'affected_user': login.conect_id or 'unknown',
                        'source_ip': login.conect_ip,
                        'detected_at': login.frst_regist_pnttm,
                        'status': 'active',
                        'actions_taken': ['IP 기록 업데이트']
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"❌ 보안 알림 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_logs(
        self,
        db: Session,
        search_params,
        skip: int = 0,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        로그인 로그 검색
        
        Args:
            db: 데이터베이스 세션
            search_params: 검색 파라미터
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 로그인 로그 목록
        """
        try:
            query = db.query(LoginLog)
            
            if search_params.login_id:
                query = query.filter(LoginLog.conect_id == search_params.login_id)
            
            if search_params.login_ip:
                query = query.filter(LoginLog.conect_ip.like(f"%{search_params.login_ip}%"))
            
            if search_params.error_occrrnc_at:
                query = query.filter(LoginLog.error_occrrnc_at == search_params.error_occrrnc_at)
            
            if search_params.start_date:
                query = query.filter(LoginLog.frst_regist_pnttm >= search_params.start_date)
            
            if search_params.end_date:
                query = query.filter(LoginLog.frst_regist_pnttm <= search_params.end_date)
            
            return query.order_by(desc(LoginLog.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 로그인 로그 검색 실패 - 오류: {str(e)}")
            raise
    
    def get_recent_logs(
        self,
        db: Session,
        hours: int = 24,
        limit: int = 50
    ) -> List[LoginLog]:
        """
        최근 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            hours: 조회할 시간 범위
            limit: 조회할 최대 레코드 수
            
        Returns:
            최근 로그인 로그 목록
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            return db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= cutoff_time
            ).order_by(desc(LoginLog.frst_regist_pnttm)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 최근 로그인 로그 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_user_logs(
        self,
        db: Session,
        user_id: str,
        days: int = 30,
        limit: int = 100
    ) -> List[LoginLog]:
        """
        사용자별 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            days: 조회 기간 (일)
            limit: 조회할 최대 레코드 수
            
        Returns:
            사용자 로그인 로그 목록
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            return db.query(LoginLog).filter(
                and_(
                    LoginLog.conect_id == user_id,
                    LoginLog.frst_regist_pnttm >= cutoff_date
                )
            ).order_by(desc(LoginLog.frst_regist_pnttm)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 사용자별 로그인 로그 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_daily_login_stats(
        self,
        db: Session,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        일별 로그인 통계 조회
        
        Args:
            db: 데이터베이스 세션
            days: 조회 기간 (일)
            
        Returns:
            일별 로그인 통계
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            daily_stats = db.query(
                func.date(LoginLog.frst_regist_pnttm).label('date'),
                func.count(LoginLog.log_id).label('total'),
                func.sum(
                    case(
                        (LoginLog.error_occrrnc_at == 'N', 1),
                        else_=0
                    )
                ).label('success'),
                func.sum(
                    case(
                        (LoginLog.error_occrrnc_at == 'Y', 1),
                        else_=0
                    )
                ).label('fail')
            ).filter(
                LoginLog.frst_regist_pnttm >= cutoff_date
            ).group_by(
                func.date(LoginLog.frst_regist_pnttm)
            ).order_by(
                func.date(LoginLog.frst_regist_pnttm)
            ).all()
            
            return {
                'period_days': days,
                'daily_stats': [
                    {
                        'date': stat.date.isoformat(),
                        'total': stat.total,
                        'success': stat.success,
                        'fail': stat.fail
                    }
                    for stat in daily_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 일별 로그인 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_hourly_login_stats(
        self,
        db: Session,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        시간별 로그인 통계 조회
        
        Args:
            db: 데이터베이스 세션
            days: 조회 기간 (일)
            
        Returns:
            시간별 로그인 통계
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            hourly_stats = db.query(
                func.extract('hour', LoginLog.frst_regist_pnttm).label('hour'),
                func.count(LoginLog.log_id).label('count')
            ).filter(
                and_(
                    LoginLog.frst_regist_pnttm >= cutoff_date,
                    LoginLog.error_occrrnc_at == 'N'
                )
            ).group_by(
                func.extract('hour', LoginLog.frst_regist_pnttm)
            ).order_by(
                func.extract('hour', LoginLog.frst_regist_pnttm)
            ).all()
            
            return {
                'period_days': days,
                'hourly_stats': [
                    {
                        'hour': int(stat.hour),
                        'count': stat.count
                    }
                    for stat in hourly_stats
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 시간별 로그인 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def export_logs(
        self,
        db: Session,
        format: str = "csv",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        로그 데이터 내보내기
        
        Args:
            db: 데이터베이스 세션
            format: 내보내기 형식
            start_date: 시작 날짜
            end_date: 종료 날짜
            user_id: 사용자 ID
            
        Returns:
            내보내기 결과
        """
        try:
            query = db.query(LoginLog)
            
            if start_date:
                query = query.filter(LoginLog.frst_regist_pnttm >= start_date)
            if end_date:
                query = query.filter(LoginLog.frst_regist_pnttm <= end_date)
            if user_id:
                query = query.filter(LoginLog.conect_id == user_id)
            
            logs = query.order_by(desc(LoginLog.frst_regist_pnttm)).all()
            
            # 간단한 내보내기 응답 (실제로는 파일 생성 로직 필요)
            return {
                'format': format,
                'total_records': len(logs),
                'export_time': datetime.now().isoformat(),
                'file_url': f'/exports/login_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{format}'
            }
            
        except Exception as e:
            logger.error(f"❌ 로그 데이터 내보내기 실패 - 오류: {str(e)}")
            raise
    
    def analyze_logs(
        self,
        db: Session,
        days: int = 30,
        analysis_type: str = "overview"
    ) -> Dict[str, Any]:
        """
        로그 데이터 분석
        
        Args:
            db: 데이터베이스 세션
            days: 분석 기간 (일)
            analysis_type: 분석 유형
            
        Returns:
            분석 결과
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            base_query = db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= cutoff_date
            )
            
            total_attempts = base_query.count()
            successful_logins = base_query.filter(
                LoginLog.error_occrrnc_at == 'N'
            ).count()
            failed_logins = base_query.filter(
                LoginLog.error_occrrnc_at == 'Y'
            ).count()
            
            unique_users = base_query.filter(
                LoginLog.error_occrrnc_at == 'N'
            ).distinct(LoginLog.conect_id).count()
            
            unique_ips = base_query.distinct(LoginLog.conect_ip).count()
            
            return {
                'analysis_type': analysis_type,
                'period_days': days,
                'summary': {
                    'total_attempts': total_attempts,
                    'successful_logins': successful_logins,
                    'failed_logins': failed_logins,
                    'success_rate': round((successful_logins / total_attempts * 100) if total_attempts > 0 else 0, 2),
                    'unique_users': unique_users,
                    'unique_ips': unique_ips
                },
                'analysis_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ 로그 데이터 분석 실패 - 오류: {str(e)}")
            raise
    
    def get_user_sessions(
        self,
        db: Session,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        사용자 세션 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            사용자 세션 목록
        """
        try:
            # 최근 30일간의 성공한 로그인만 조회
            cutoff_date = datetime.now() - timedelta(days=30)
            
            sessions = db.query(LoginLog).filter(
                and_(
                    LoginLog.conect_id == user_id,
                    LoginLog.error_occrrnc_at == 'N',
                    LoginLog.frst_regist_pnttm >= cutoff_date
                )
            ).order_by(desc(LoginLog.frst_regist_pnttm)).all()
            
            return [
                {
                    'session_id': log.log_id,
                    'login_time': log.frst_regist_pnttm.isoformat() if log.frst_regist_pnttm else None,
                    'ip_address': log.conect_ip,
                    'status': 'active' if log.frst_regist_pnttm and log.frst_regist_pnttm > datetime.now() - timedelta(hours=24) else 'expired'
                }
                for log in sessions
            ]
            
        except Exception as e:
            logger.error(f"❌ 사용자 세션 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
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
                LoginLog.frst_regist_pnttm < cutoff_date
            ).delete()
            
            db.commit()
            
            logger.info(f"✅ 오래된 로그 정리 완료 - 삭제된 로그 수: {deleted_count}")
            return deleted_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 오래된 로그 정리 실패 - 오류: {str(e)}")
            raise
    
    def get_suspicious_activities(
        self, 
        db: Session, 
        hours: int = 24, 
        severity: str = None
    ) -> List[dict]:
        """
        의심스러운 활동을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            hours: 조회 시간 (시간)
            severity: 심각도 필터
        
        Returns:
            의심스러운 활동 목록
        """
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            # 의심스러운 활동 패턴 조회
            suspicious_activities = []
            
            # 반복적인 실패 시도
            failed_attempts = db.query(
                LoginLog.conect_ip,
                func.count(LoginLog.log_id).label('attempt_count')
            ).filter(
                LoginLog.frst_regist_pnttm >= since_time,
                LoginLog.error_occrrnc_at == 'Y'
            ).group_by(LoginLog.conect_ip).having(
                func.count(LoginLog.log_id) >= 5
            ).all()
            
            for attempt in failed_attempts:
                suspicious_activities.append({
                    'activity_id': f"suspicious_{attempt.conect_ip}_{int(datetime.now().timestamp())}",
                    'user_id': 'unknown',
                    'activity_type': 'repeated_failures',
                    'risk_score': min(attempt.attempt_count * 10.0, 100.0),
                    'indicators': [f"반복된 로그인 실패 ({attempt.attempt_count}회)", f"IP: {attempt.conect_ip}"],
                    'detected_at': datetime.now().isoformat(),
                    'location': {'ip': attempt.conect_ip, 'country': 'Unknown', 'city': 'Unknown'},
                    'device_info': {'user_agent': 'Unknown', 'device_type': 'Unknown'},
                    'recommended_actions': ['IP 차단 검토', '보안 모니터링 강화'] if attempt.attempt_count >= 10 else ['모니터링 지속']
                })
            
            # 심각도 필터링
            if severity:
                suspicious_activities = [a for a in suspicious_activities if a['severity'] == severity]
            
            return suspicious_activities
            
        except Exception as e:
            logger.error(f"❌ 의심스러운 활동 조회 중 오류 발생: {str(e)}")
            raise
    
    def get_repeated_login_failures(
        self, 
        db: Session, 
        hours: int = 24, 
        min_attempts: int = 5
    ) -> List[dict]:
        """
        반복된 로그인 실패 시도를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            hours: 조회 시간 (시간)
            min_attempts: 최소 시도 횟수
        
        Returns:
            반복 실패 시도 목록
        """
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            repeated_failures = db.query(
                LoginLog.conect_ip,
                LoginLog.conect_id,
                func.count(LoginLog.log_id).label('failure_count'),
                func.min(LoginLog.frst_regist_pnttm).label('first_attempt'),
                func.max(LoginLog.frst_regist_pnttm).label('last_attempt')
            ).filter(
                LoginLog.frst_regist_pnttm >= since_time,
                LoginLog.error_occrrnc_at == 'Y'
            ).group_by(
                LoginLog.conect_ip, LoginLog.conect_id
            ).having(
                func.count(LoginLog.log_id) >= min_attempts
            ).all()
            
            result = []
            for failure in repeated_failures:
                result.append({
                    'ip_address': failure.conect_ip,
                    'user_id': failure.conect_id,
                    'failure_count': failure.failure_count,
                    'first_attempt': failure.first_attempt,
                    'last_attempt': failure.last_attempt,
                    'risk_level': 'HIGH' if failure.failure_count >= 10 else 'MEDIUM'
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 반복된 로그인 실패 시도 조회 중 오류 발생: {str(e)}")
            raise
            
    def get_top_ip_addresses(
        self,
        db: Session,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        상위 IP 주소 통계 조회
        
        Args:
            db: 데이터베이스 세션
            days: 조회할 일수
            limit: 반환할 최대 개수
            
        Returns:
            상위 IP 주소 목록
        """
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            top_ips = db.query(
                LoginLog.conect_ip,
                func.count(LoginLog.log_id).label('login_count'),
                func.count(func.distinct(LoginLog.conect_id)).label('unique_users'),
                func.sum(case((LoginLog.error_occrrnc_at == 'N', 1), else_=0)).label('success_count'),
                func.sum(case((LoginLog.error_occrrnc_at == 'Y', 1), else_=0)).label('fail_count')
            ).filter(
                LoginLog.frst_regist_pnttm >= start_date
            ).group_by(
                LoginLog.conect_ip
            ).order_by(
                desc(func.count(LoginLog.log_id))
            ).limit(limit).all()
            
            result = []
            for ip_stat in top_ips:
                success_rate = (ip_stat.success_count / ip_stat.login_count * 100) if ip_stat.login_count > 0 else 0
                result.append({
                    'ip_address': ip_stat.conect_ip,
                    'login_count': ip_stat.login_count,
                    'unique_users': ip_stat.unique_users,
                    'success_count': ip_stat.success_count,
                    'fail_count': ip_stat.fail_count,
                    'success_rate': round(success_rate, 2)
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 상위 IP 주소 통계 조회 중 오류 발생: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"❌ 반복 로그인 실패 조회 중 오류 발생: {str(e)}")
            raise
    
    def get_unusual_login_times(
        self, 
        db: Session, 
        days: int = 7
    ) -> List[dict]:
        """
        비정상적인 시간대의 로그인을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            days: 조회 기간 (일)
        
        Returns:
            비정상 시간대 로그인 목록
        """
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            # 새벽 시간대 (00:00-06:00) 또는 늦은 밤 (22:00-24:00) 로그인
            unusual_logins = db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= since_date,
                LoginLog.error_occrrnc_at == 'N',
                or_(
                    func.extract('hour', LoginLog.frst_regist_pnttm).between(0, 6),
                    func.extract('hour', LoginLog.frst_regist_pnttm).between(22, 23)
                )
            ).all()
            
            result = []
            for login in unusual_logins:
                result.append({
                    'log_id': login.log_id,
                    'user_id': login.conect_id,
                    'ip_address': login.conect_ip,
                    'login_time': login.frst_regist_pnttm,
                    'hour': login.frst_regist_pnttm.hour,
                    'risk_level': 'MEDIUM'
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ 비정상 시간대 로그인 조회 중 오류 발생: {str(e)}")
            raise
    
    def get_new_ip_logins(
        self, 
        db: Session, 
        days: int = 7
    ) -> List[dict]:
        """
        새로운 IP 주소에서의 로그인을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            days: 조회 기간 (일)
        
        Returns:
            새로운 IP 로그인 목록
        """
        try:
            since_date = datetime.now() - timedelta(days=days)
            
            # 각 사용자별로 최근 로그인 IP 조회
            recent_logins = db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= since_date,
                LoginLog.error_occrrnc_at == 'N'
            ).order_by(LoginLog.frst_regist_pnttm.desc()).all()
            
            new_ip_logins = []
            user_known_ips = {}
            
            for login in recent_logins:
                user_id = login.conect_id
                ip_address = login.conect_ip
                
                # 사용자의 알려진 IP 목록 구축
                if user_id not in user_known_ips:
                    # 30일 전부터의 IP 목록 조회
                    historical_ips = db.query(LoginLog.conect_ip).filter(
                        LoginLog.conect_id == user_id,
                        LoginLog.frst_regist_pnttm < since_date,
                        LoginLog.error_occrrnc_at == 'N'
                    ).distinct().all()
                    
                    user_known_ips[user_id] = {ip.conect_ip for ip in historical_ips}
                
                # 새로운 IP인지 확인
                if ip_address not in user_known_ips[user_id]:
                    new_ip_logins.append({
                        'log_id': login.log_id,
                        'user_id': user_id,
                        'ip_address': ip_address,
                        'login_time': login.frst_regist_pnttm,
                        'risk_level': 'MEDIUM'
                    })
                    
                    # 알려진 IP 목록에 추가
                    user_known_ips[user_id].add(ip_address)
            
            return new_ip_logins
            
        except Exception as e:
            logger.error(f"❌ 새로운 IP 로그인 조회 중 오류 발생: {str(e)}")
            raise
    
    def get_active_sessions(
        self, 
        db: Session
    ) -> List[dict]:
        """
        현재 활성 세션을 조회합니다.
        
        Args:
            db: 데이터베이스 세션
        
        Returns:
            활성 세션 목록
        """
        try:
            # 최근 24시간 내 성공한 로그인 중 로그아웃 기록이 없는 세션
            since_time = datetime.now() - timedelta(hours=24)
            
            active_logins = db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= since_time,
                LoginLog.error_occrrnc_at == 'N'
            ).order_by(LoginLog.frst_regist_pnttm.desc()).all()
            
            active_sessions = []
            seen_users = set()
            
            for login in active_logins:
                # 사용자별로 최근 로그인만 활성 세션으로 간주
                if login.conect_id not in seen_users:
                    # 세션 지속시간 계산 (현재 시간 - 로그인 시간, 분 단위)
                    session_duration = 0
                    if login.frst_regist_pnttm:
                        duration_delta = datetime.now() - login.frst_regist_pnttm
                        session_duration = int(duration_delta.total_seconds() / 60)
                    
                    active_sessions.append({
                        'session_id': f"session_{login.log_id}",
                        'user_id': login.conect_id,
                        'ip_address': login.conect_ip,
                        'login_time': login.frst_regist_pnttm.isoformat() if login.frst_regist_pnttm else None,
                        'last_activity': login.frst_regist_pnttm.isoformat() if login.frst_regist_pnttm else None,
                        'user_agent': getattr(login, 'user_agent', 'Unknown'),
                        'is_active': True,
                        'session_duration': session_duration
                    })
                    seen_users.add(login.conect_id)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"❌ 활성 세션 조회 중 오류 발생: {str(e)}")
            raise
    
    def get_failed_attempts(
        self, 
        db: Session, 
        hours: int = 24, 
        limit: int = 100
    ) -> List[LoginLog]:
        """
        실패한 로그인 시도를 조회합니다.
        
        Args:
            db: 데이터베이스 세션
            hours: 조회 시간 (시간)
            limit: 조회할 최대 레코드 수
        
        Returns:
            실패한 로그인 시도 목록
        """
        try:
            since_time = datetime.now() - timedelta(hours=hours)
            
            failed_attempts = db.query(LoginLog).filter(
                LoginLog.frst_regist_pnttm >= since_time,
                LoginLog.error_occrrnc_at == 'Y'
            ).order_by(LoginLog.frst_regist_pnttm.desc()).limit(limit).all()
            
            return failed_attempts
            
        except Exception as e:
            logger.error(f"❌ 실패한 로그인 시도 조회 중 오류 발생: {str(e)}")
            raise
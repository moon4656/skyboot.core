import logging
import logging.handlers
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import traceback
from pythonjsonlogger import jsonlogger


class ProductionLogger:
    """
    프로덕션 환경을 위한 고급 로거 클래스
    
    특징:
    - JSON 형식 로그 출력
    - 구조화된 로깅
    - 로그 레벨별 분리
    - 성능 최적화
    - 보안 로깅
    - 메트릭 수집
    """
    
    def __init__(self, log_dir: str = "logs", app_name: str = "skyboot-api"):
        """
        프로덕션 로거 초기화
        
        Args:
            log_dir: 로그 파일이 저장될 디렉토리
            app_name: 애플리케이션 이름
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.app_name = app_name
        
        # 환경 설정
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.enable_json_logs = os.getenv("ENABLE_JSON_LOGS", "true").lower() == "true"
        
        # 로거 설정
        self._setup_loggers()
    
    def _setup_loggers(self):
        """
        다양한 로거들을 설정합니다.
        """
        # 메인 애플리케이션 로거
        self.app_logger = self._create_logger(
            "app", 
            "application.log", 
            level=self.log_level
        )
        
        # API 요청/응답 로거
        self.api_logger = self._create_logger(
            "api", 
            "api_requests.log", 
            level="INFO"
        )
        
        # 보안 이벤트 로거
        self.security_logger = self._create_logger(
            "security", 
            "security.log", 
            level="WARNING"
        )
        
        # 에러 로거
        self.error_logger = self._create_logger(
            "error", 
            "errors.log", 
            level="ERROR"
        )
        
        # 성능 메트릭 로거
        self.metrics_logger = self._create_logger(
            "metrics", 
            "metrics.log", 
            level="INFO"
        )
        
        # 감사 로그 (audit log)
        self.audit_logger = self._create_logger(
            "audit", 
            "audit.log", 
            level="INFO"
        )
    
    def _create_logger(self, name: str, filename: str, level: str = "INFO") -> logging.Logger:
        """
        개별 로거를 생성합니다.
        
        Args:
            name: 로거 이름
            filename: 로그 파일명
            level: 로그 레벨
            
        Returns:
            설정된 로거 인스턴스
        """
        logger = logging.getLogger(f"{self.app_name}.{name}")
        logger.setLevel(getattr(logging, level))
        
        # 기존 핸들러 제거
        if logger.handlers:
            logger.handlers.clear()
        
        # 파일 핸들러 설정
        self._add_file_handler(logger, filename)
        
        # 콘솔 핸들러 설정 (개발 환경에서만)
        if self.environment != "production":
            self._add_console_handler(logger)
        
        return logger
    
    def _add_file_handler(self, logger: logging.Logger, filename: str):
        """
        파일 핸들러를 추가합니다.
        
        Args:
            logger: 로거 인스턴스
            filename: 로그 파일명
        """
        log_file = self.log_dir / filename
        
        # 로테이팅 파일 핸들러 (크기 기반 + 시간 기반)
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_file),
            when='midnight',
            interval=1,
            backupCount=int(os.getenv("LOG_BACKUP_COUNT", "30")),
            encoding='utf-8'
        )
        
        # 최대 파일 크기 설정
        max_bytes = int(os.getenv("LOG_MAX_BYTES", "52428800"))  # 50MB
        file_handler.maxBytes = max_bytes
        
        # 포맷터 설정
        if self.enable_json_logs:
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def _add_console_handler(self, logger: logging.Logger):
        """
        콘솔 핸들러를 추가합니다.
        
        Args:
            logger: 로거 인스턴스
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    def log_api_request(self, method: str, url: str, client_ip: str, 
                       user_agent: Optional[str] = None, user_id: Optional[str] = None,
                       request_id: Optional[str] = None):
        """
        API 요청을 로깅합니다.
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            client_ip: 클라이언트 IP
            user_agent: User-Agent 헤더
            user_id: 사용자 ID
            request_id: 요청 추적 ID
        """
        log_data = {
            "event_type": "api_request",
            "method": method,
            "url": url,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.enable_json_logs:
            self.api_logger.info(json.dumps(log_data))
        else:
            message = f"🚀 {method} {url} | IP: {client_ip} | User: {user_id or 'Anonymous'}"
            if request_id:
                message += f" | RequestID: {request_id}"
            self.api_logger.info(message)
    
    def log_api_response(self, method: str, url: str, status_code: int, 
                        response_time: float, response_size: Optional[int] = None,
                        request_id: Optional[str] = None):
        """
        API 응답을 로깅합니다.
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            status_code: HTTP 상태 코드
            response_time: 응답 시간 (초)
            response_size: 응답 크기 (바이트)
            request_id: 요청 추적 ID
        """
        log_data = {
            "event_type": "api_response",
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time": response_time,
            "response_size": response_size,
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.enable_json_logs:
            self.api_logger.info(json.dumps(log_data))
        else:
            status_emoji = "✅" if 200 <= status_code < 300 else "❌" if status_code >= 400 else "⚠️"
            message = f"{status_emoji} {method} {url} | Status: {status_code} | Time: {response_time:.3f}s"
            if response_size:
                message += f" | Size: {response_size} bytes"
            if request_id:
                message += f" | RequestID: {request_id}"
            
            if status_code >= 400:
                self.api_logger.error(message)
            elif status_code >= 300:
                self.api_logger.warning(message)
            else:
                self.api_logger.info(message)
    
    def log_security_event(self, event_type: str, description: str, 
                          client_ip: str, user_id: Optional[str] = None,
                          severity: str = "medium", **kwargs):
        """
        보안 이벤트를 로깅합니다.
        
        Args:
            event_type: 이벤트 유형 (login_failed, rate_limit_exceeded 등)
            description: 이벤트 설명
            client_ip: 클라이언트 IP
            user_id: 사용자 ID
            severity: 심각도 (low, medium, high, critical)
            **kwargs: 추가 데이터
        """
        log_data = {
            "event_type": "security_event",
            "security_event_type": event_type,
            "description": description,
            "client_ip": client_ip,
            "user_id": user_id,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            **kwargs
        }
        
        if self.enable_json_logs:
            self.security_logger.warning(json.dumps(log_data))
        else:
            message = f"🚨 SECURITY | {event_type} | {description} | IP: {client_ip}"
            if user_id:
                message += f" | User: {user_id}"
            self.security_logger.warning(message)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None,
                 request_id: Optional[str] = None):
        """
        에러를 로깅합니다.
        
        Args:
            error: 발생한 예외
            context: 에러 컨텍스트 정보
            request_id: 요청 추적 ID
        """
        log_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.enable_json_logs:
            self.error_logger.error(json.dumps(log_data))
        else:
            message = f"💥 ERROR | {type(error).__name__}: {str(error)}"
            if request_id:
                message += f" | RequestID: {request_id}"
            if context:
                message += f" | Context: {context}"
            self.error_logger.error(message)
    
    def log_metrics(self, metric_name: str, value: float, unit: str = "",
                   tags: Optional[Dict[str, str]] = None):
        """
        메트릭을 로깅합니다.
        
        Args:
            metric_name: 메트릭 이름
            value: 메트릭 값
            unit: 단위
            tags: 태그 정보
        """
        log_data = {
            "event_type": "metric",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "tags": tags or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.enable_json_logs:
            self.metrics_logger.info(json.dumps(log_data))
        else:
            message = f"📊 METRIC | {metric_name}: {value}{unit}"
            if tags:
                tag_str = ", ".join([f"{k}={v}" for k, v in tags.items()])
                message += f" | Tags: {tag_str}"
            self.metrics_logger.info(message)
    
    def log_audit(self, action: str, resource: str, user_id: str,
                 result: str = "success", details: Optional[Dict[str, Any]] = None):
        """
        감사 로그를 기록합니다.
        
        Args:
            action: 수행된 작업 (create, update, delete 등)
            resource: 대상 리소스
            user_id: 사용자 ID
            result: 결과 (success, failure)
            details: 상세 정보
        """
        log_data = {
            "event_type": "audit",
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "result": result,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if self.enable_json_logs:
            self.audit_logger.info(json.dumps(log_data))
        else:
            message = f"📋 AUDIT | {action} {resource} | User: {user_id} | Result: {result}"
            if details:
                message += f" | Details: {details}"
            self.audit_logger.info(message)


# 전역 프로덕션 로거 인스턴스
production_logger = None


def get_production_logger() -> ProductionLogger:
    """
    프로덕션 로거 인스턴스를 반환합니다.
    
    Returns:
        ProductionLogger 인스턴스
    """
    global production_logger
    if production_logger is None:
        production_logger = ProductionLogger()
    return production_logger


def setup_production_logging():
    """
    프로덕션 로깅을 설정합니다.
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    # 프로덕션 로거 초기화
    get_production_logger()
    
    print("🔧 프로덕션 로깅 설정 완료")
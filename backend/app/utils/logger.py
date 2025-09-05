import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class APILogger:
    """
    API 요청/응답 로깅을 위한 로거 클래스
    10MB 단위로 매일 로테이션되는 로그 파일을 생성합니다.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        로거 초기화
        
        Args:
            log_dir: 로그 파일이 저장될 디렉토리 경로
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # 로거 설정
        self.logger = logging.getLogger("api_logger")
        self.logger.setLevel(logging.INFO)
        
        # 기존 핸들러 제거 (중복 방지)
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # 파일 핸들러 설정 (10MB, 매일 로테이션)
        self._setup_file_handler()
        
        # 콘솔 핸들러 설정
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """
        파일 핸들러 설정 - 10MB 단위, 매일 로테이션
        """
        log_file = self.log_dir / "api_requests.log"
        
        # TimedRotatingFileHandler와 RotatingFileHandler 조합
        # 매일 로테이션하되, 10MB 초과 시에도 로테이션
        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=str(log_file),
            when='midnight',
            interval=1,
            backupCount=30,  # 30일간 보관
            encoding='utf-8'
        )
        
        # 10MB 제한을 위한 추가 설정
        file_handler.maxBytes = 10 * 1024 * 1024  # 10MB
        
        # 로그 포맷 설정
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """
        콘솔 핸들러 설정
        """
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        console_formatter = logging.Formatter(
            '%(asctime)s | API | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
    
    def log_request(self, method: str, url: str, client_ip: str, 
                   user_agent: Optional[str] = None, user_id: Optional[str] = None):
        """
        API 요청 로깅
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            client_ip: 클라이언트 IP 주소
            user_agent: User-Agent 헤더
            user_id: 사용자 ID (인증된 경우)
        """
        log_data = {
            "type": "REQUEST",
            "method": method,
            "url": url,
            "client_ip": client_ip,
            "user_agent": user_agent or "Unknown",
            "user_id": user_id or "Anonymous",
            "timestamp": datetime.now().isoformat()
        }
        
        message = f"🚀 {method} {url} | IP: {client_ip} | User: {user_id or 'Anonymous'}"
        self.logger.info(message)
    
    def log_response(self, method: str, url: str, status_code: int, 
                    response_time: float, response_size: Optional[int] = None):
        """
        API 응답 로깅
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            status_code: HTTP 상태 코드
            response_time: 응답 시간 (초)
            response_size: 응답 크기 (바이트)
        """
        status_emoji = "✅" if 200 <= status_code < 300 else "❌" if status_code >= 400 else "⚠️"
        
        message = f"{status_emoji} {method} {url} | Status: {status_code} | Time: {response_time:.3f}s"
        if response_size:
            message += f" | Size: {response_size} bytes"
        
        if status_code >= 400:
            self.logger.error(message)
        elif status_code >= 300:
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def log_error(self, method: str, url: str, error: Exception, 
                 client_ip: str, user_id: Optional[str] = None):
        """
        API 에러 로깅
        
        Args:
            method: HTTP 메서드
            url: 요청 URL
            error: 발생한 예외
            client_ip: 클라이언트 IP 주소
            user_id: 사용자 ID (인증된 경우)
        """
        message = f"💥 ERROR {method} {url} | IP: {client_ip} | User: {user_id or 'Anonymous'} | Error: {str(error)}"
        self.logger.error(message)
    
    def log_custom(self, level: str, message: str, **kwargs):
        """
        커스텀 로그 메시지
        
        Args:
            level: 로그 레벨 (info, warning, error, debug)
            message: 로그 메시지
            **kwargs: 추가 데이터
        """
        if kwargs:
            extra_data = " | ".join([f"{k}: {v}" for k, v in kwargs.items()])
            message = f"{message} | {extra_data}"
        
        log_method = getattr(self.logger, level.lower(), self.logger.info)
        log_method(message)


# 전역 로거 인스턴스
api_logger = APILogger()


def get_api_logger() -> APILogger:
    """
    API 로거 인스턴스 반환
    
    Returns:
        APILogger 인스턴스
    """
    return api_logger
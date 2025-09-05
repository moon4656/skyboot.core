import time
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import get_api_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    API 요청/응답 로깅 미들웨어
    모든 HTTP 요청과 응답을 자동으로 로깅합니다.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_api_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청/응답 처리 및 로깅
        
        Args:
            request: FastAPI Request 객체
            call_next: 다음 미들웨어 또는 엔드포인트 호출 함수
        
        Returns:
            Response 객체
        """
        # 요청 시작 시간 기록
        start_time = time.time()
        
        # 클라이언트 정보 추출
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "Unknown")
        method = request.method
        url = str(request.url)
        
        # 사용자 정보 추출 (인증된 경우)
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = getattr(request.state.user, 'id', None)
        
        # 요청 로깅
        self.logger.log_request(
            method=method,
            url=url,
            client_ip=client_ip,
            user_agent=user_agent,
            user_id=user_id
        )
        
        try:
            # 다음 미들웨어 또는 엔드포인트 호출
            response = await call_next(request)
            
            # 응답 시간 계산
            process_time = time.time() - start_time
            
            # 응답 크기 계산 (가능한 경우)
            response_size = None
            if hasattr(response, 'body'):
                response_size = len(response.body) if response.body else 0
            
            # 응답 로깅
            self.logger.log_response(
                method=method,
                url=url,
                status_code=response.status_code,
                response_time=process_time,
                response_size=response_size
            )
            
            # 응답 헤더에 처리 시간 추가
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # 에러 발생 시 로깅
            process_time = time.time() - start_time
            
            self.logger.log_error(
                method=method,
                url=url,
                error=e,
                client_ip=client_ip,
                user_id=user_id
            )
            
            # 에러 응답 생성
            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "timestamp": time.time()
                }
            )
            error_response.headers["X-Process-Time"] = str(process_time)
            
            return error_response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        클라이언트 IP 주소 추출
        
        Args:
            request: FastAPI Request 객체
        
        Returns:
            클라이언트 IP 주소
        """
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # 첫 번째 IP가 실제 클라이언트 IP
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 직접 연결된 클라이언트 IP
        if request.client:
            return request.client.host
        
        return "Unknown"


class RequestSizeMiddleware(BaseHTTPMiddleware):
    """
    요청 크기 제한 미들웨어
    대용량 파일 업로드 등을 제한합니다.
    """
    
    def __init__(self, app: ASGIApp, max_size: int = 50 * 1024 * 1024):  # 50MB
        super().__init__(app)
        self.max_size = max_size
        self.logger = get_api_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 크기 검증 및 처리
        
        Args:
            request: FastAPI Request 객체
            call_next: 다음 미들웨어 또는 엔드포인트 호출 함수
        
        Returns:
            Response 객체
        """
        # Content-Length 헤더 확인
        content_length = request.headers.get("content-length")
        
        if content_length:
            content_length = int(content_length)
            if content_length > self.max_size:
                client_ip = request.client.host if request.client else "Unknown"
                
                self.logger.log_custom(
                    level="warning",
                    message=f"Request size limit exceeded: {content_length} bytes",
                    client_ip=client_ip,
                    url=str(request.url),
                    max_size=self.max_size
                )
                
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "Request Entity Too Large",
                        "message": f"요청 크기가 제한을 초과했습니다. 최대 크기: {self.max_size // (1024*1024)}MB",
                        "max_size_mb": self.max_size // (1024*1024)
                    }
                )
        
        return await call_next(request)
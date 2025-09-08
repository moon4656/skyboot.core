from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.auth_service import AuthorInfoService
from app.utils.logger import get_api_logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    JWT 토큰 인증 미들웨어
    보호된 엔드포인트에 대한 access token 검증을 수행합니다.
    """
    
    # 인증이 필요하지 않은 경로들
    EXCLUDED_PATHS = {
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/favicon.ico",
        "/health",
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/users/one-click-login",
        "/api/v1/files/upload-process",  # 테스트용 임시 추가
    }
    
    # 인증이 필요하지 않은 경로 패턴들
    EXCLUDED_PATH_PATTERNS = {
        "/static/",
        "/docs/",
        "/redoc/"
    }
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_api_logger()
        self.auth_service = AuthorInfoService()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        요청 인증 검증 및 처리
        
        Args:
            request: FastAPI Request 객체
            call_next: 다음 미들웨어 또는 엔드포인트 호출 함수
        
        Returns:
            Response 객체
        """
        path = request.url.path
        method = request.method
        
        # 인증이 필요하지 않은 경로 확인
        if self._is_excluded_path(path):
            return await call_next(request)
        
        # OPTIONS 요청은 인증 제외 (CORS preflight)
        if method == "OPTIONS":
            return await call_next(request)
        
        # Authorization 헤더에서 토큰 추출
        authorization = request.headers.get("Authorization")
        if not authorization:
            return self._create_auth_error_response(
                "Authorization header missing",
                "인증 헤더가 누락되었습니다."
            )
        
        # Bearer 토큰 형식 확인
        if not authorization.startswith("Bearer "):
            return self._create_auth_error_response(
                "Invalid authorization format",
                "잘못된 인증 형식입니다. Bearer 토큰을 사용해주세요."
            )
        
        # 토큰 추출
        token = authorization.split(" ")[1]
        
        try:
            # 데이터베이스 세션 생성
            db = next(get_db())
            
            # 토큰 검증 및 사용자 정보 조회
            user_info = self.auth_service.verify_access_token(token)
            
            if not user_info:
                return self._create_auth_error_response(
                    "Invalid or expired token",
                    "유효하지 않거나 만료된 토큰입니다."
                )
            
            # 사용자 정보를 request.state에 저장
            request.state.user = user_info
            request.state.user_id = user_info.get('user_id')
            
            # 인증 성공 로깅
            client_ip = self._get_client_ip(request)
            self.logger.log_custom(
                level="info",
                message=f"🔐 Authentication successful - User: {user_info.get('user_id')}",
                client_ip=client_ip,
                url=path,
                method=method,
                user_id=user_info.get('user_id')
            )
            
            return await call_next(request)
            
        except Exception as e:
            # 토큰 검증 실패 로깅
            client_ip = self._get_client_ip(request)
            self.logger.log_custom(
                level="warning",
                message=f"❌ Authentication failed - Error: {str(e)}",
                client_ip=client_ip,
                url=path,
                method=method,
                error=str(e)
            )
            
            return self._create_auth_error_response(
                "Authentication failed",
                "인증에 실패했습니다."
            )
        
        finally:
            # 데이터베이스 세션 정리
            if 'db' in locals():
                db.close()
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        인증이 필요하지 않은 경로인지 확인
        
        Args:
            path: 요청 경로
        
        Returns:
            인증 제외 여부
        """
        # 정확한 경로 매칭
        if path in self.EXCLUDED_PATHS:
            return True
        
        # 패턴 매칭
        for pattern in self.EXCLUDED_PATH_PATTERNS:
            if path.startswith(pattern):
                return True
        
        return False
    
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
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 직접 연결된 클라이언트 IP
        if request.client:
            return request.client.host
        
        return "Unknown"
    
    def _create_auth_error_response(self, error: str, message: str) -> JSONResponse:
        """
        인증 오류 응답 생성
        
        Args:
            error: 오류 코드
            message: 오류 메시지
        
        Returns:
            JSONResponse 객체
        """
        return JSONResponse(
            status_code=401,
            content={
                "error": error,
                "message": message,
                "detail": "유효한 인증 토큰이 필요합니다."
            }
        )
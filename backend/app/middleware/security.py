# SkyBoot Core API - 보안 미들웨어
# 프로덕션 환경 보안 설정 강화

import os
import time
import logging
from typing import Dict, List, Optional
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from collections import defaultdict, deque
from datetime import datetime, timedelta
import ipaddress

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    보안 강화를 위한 미들웨어
    - Rate Limiting
    - IP 화이트리스트/블랙리스트
    - 보안 헤더 추가
    - 요청 크기 제한
    """
    
    def __init__(
        self,
        app,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
        allowed_ips: Optional[List[str]] = None,
        blocked_ips: Optional[List[str]] = None,
        enable_security_headers: bool = True
    ):
        super().__init__(app)
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.max_request_size = max_request_size
        self.allowed_ips = set(allowed_ips or [])
        self.blocked_ips = set(blocked_ips or [])
        self.enable_security_headers = enable_security_headers
        
        # Rate limiting 저장소
        self.request_counts: Dict[str, deque] = defaultdict(deque)
        
        logger.info("🔒 보안 미들웨어 초기화 완료")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        보안 검사를 수행하고 요청을 처리합니다.
        """
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        try:
            # 1. IP 기반 접근 제어
            if not self._check_ip_access(client_ip):
                logger.warning(f"🚫 IP 접근 차단: {client_ip}")
                raise HTTPException(status_code=403, detail="Access denied")
            
            # 2. Rate Limiting 검사
            if not self._check_rate_limit(client_ip):
                logger.warning(f"⚠️ Rate limit 초과: {client_ip}")
                raise HTTPException(status_code=429, detail="Too many requests")
            
            # 3. 요청 크기 검사
            if not await self._check_request_size(request):
                logger.warning(f"📦 요청 크기 초과: {client_ip}")
                raise HTTPException(status_code=413, detail="Request entity too large")
            
            # 4. 요청 처리
            response = await call_next(request)
            
            # 5. 보안 헤더 추가
            if self.enable_security_headers:
                self._add_security_headers(response)
            
            # 6. 처리 시간 로깅
            process_time = time.time() - start_time
            logger.info(f"🔒 보안 검사 완료 - IP: {client_ip}, 처리시간: {process_time:.3f}s")
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ 보안 미들웨어 오류: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def _get_client_ip(self, request: Request) -> str:
        """
        클라이언트 IP 주소를 추출합니다.
        """
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 직접 연결된 클라이언트 IP
        return request.client.host if request.client else "unknown"
    
    def _check_ip_access(self, client_ip: str) -> bool:
        """
        IP 기반 접근 제어를 확인합니다.
        """
        try:
            ip_obj = ipaddress.ip_address(client_ip)
            
            # 블랙리스트 확인
            if self.blocked_ips:
                for blocked_ip in self.blocked_ips:
                    if ip_obj in ipaddress.ip_network(blocked_ip, strict=False):
                        return False
            
            # 화이트리스트 확인 (설정된 경우)
            if self.allowed_ips:
                for allowed_ip in self.allowed_ips:
                    if ip_obj in ipaddress.ip_network(allowed_ip, strict=False):
                        return True
                return False  # 화이트리스트가 설정되었지만 매치되지 않음
            
            return True  # 화이트리스트가 설정되지 않은 경우 허용
            
        except ValueError:
            logger.warning(f"⚠️ 잘못된 IP 형식: {client_ip}")
            return False
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Rate limiting을 확인합니다.
        """
        now = time.time()
        window_start = now - self.rate_limit_window
        
        # 현재 IP의 요청 기록 가져오기
        requests = self.request_counts[client_ip]
        
        # 윈도우 밖의 오래된 요청 제거
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # 현재 요청 수 확인
        if len(requests) >= self.rate_limit_requests:
            return False
        
        # 현재 요청 기록
        requests.append(now)
        return True
    
    async def _check_request_size(self, request: Request) -> bool:
        """
        요청 크기를 확인합니다.
        """
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                return size <= self.max_request_size
            except ValueError:
                return False
        return True
    
    def _add_security_headers(self, response: Response) -> None:
        """
        보안 헤더를 추가합니다.
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value

class APIKeyMiddleware(BaseHTTPMiddleware):
    """
    API 키 기반 인증 미들웨어
    """
    
    def __init__(self, app, api_keys: Optional[List[str]] = None, exempt_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.api_keys = set(api_keys or [])
        self.exempt_paths = set(exempt_paths or ["/health", "/docs", "/redoc", "/openapi.json"])
        
        logger.info(f"🔑 API 키 미들웨어 초기화 - 등록된 키: {len(self.api_keys)}개")
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        API 키 인증을 확인합니다.
        """
        path = request.url.path
        
        # 예외 경로 확인
        if any(path.startswith(exempt_path) for exempt_path in self.exempt_paths):
            return await call_next(request)
        
        # API 키가 설정되지 않은 경우 통과
        if not self.api_keys:
            return await call_next(request)
        
        # API 키 확인
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
        
        if not api_key or api_key not in self.api_keys:
            logger.warning(f"🚫 유효하지 않은 API 키: {request.client.host if request.client else 'unknown'}")
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        logger.info(f"✅ API 키 인증 성공: {path}")
        return await call_next(request)

def get_security_config() -> Dict:
    """
    환경 변수에서 보안 설정을 가져옵니다.
    """
    return {
        "rate_limit_requests": int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
        "rate_limit_window": int(os.getenv("RATE_LIMIT_WINDOW", "60")),
        "max_request_size": int(os.getenv("MAX_REQUEST_SIZE", str(10 * 1024 * 1024))),
        "allowed_ips": os.getenv("ALLOWED_IPS", "").split(",") if os.getenv("ALLOWED_IPS") else None,
        "blocked_ips": os.getenv("BLOCKED_IPS", "").split(",") if os.getenv("BLOCKED_IPS") else None,
        "api_keys": os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else None,
        "enable_security_headers": os.getenv("ENABLE_SECURITY_HEADERS", "true").lower() == "true"
    }
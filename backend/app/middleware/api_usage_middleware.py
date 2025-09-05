import time
import json
import uuid
from typing import Callable, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.log_models import APIUsageLog
from app.utils.logger import get_api_logger


class APIUsageMiddleware(BaseHTTPMiddleware):
    """
    API 사용 로그 데이터베이스 저장 미들웨어
    모든 API 요청/응답을 데이터베이스에 기록합니다.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_api_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        API 요청/응답 처리 및 데이터베이스 로깅
        
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
        endpoint = request.url.path
        
        # 사용자 정보 추출 (인증된 경우)
        user_id = None
        if hasattr(request.state, 'user'):
            if isinstance(request.state.user, dict):
                user_id = request.state.user.get('user_id')
            else:
                user_id = getattr(request.state.user, 'user_id', None)
        
        # 요청 본문 추출 (POST, PUT, PATCH의 경우)
        request_body = None
        if method in ["POST", "PUT", "PATCH"]:
            try:
                # 요청 본문을 읽되, 스트림을 다시 사용할 수 있도록 처리
                body = await request.body()
                if body:
                    # JSON 형태로 파싱 시도
                    try:
                        request_body = json.loads(body.decode('utf-8'))
                        # 민감한 정보 마스킹
                        request_body = self._mask_sensitive_data(request_body)
                        request_body = json.dumps(request_body, ensure_ascii=False)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        request_body = "[Binary or Invalid JSON Data]"
            except Exception as e:
                self.logger.logger.error(f"요청 본문 읽기 실패: {str(e)}")
                request_body = "[Error reading request body]"
        
        # 로그 ID 생성
        log_id = self._generate_log_id()
        
        response = None
        error_message = None
        
        try:
            # 다음 미들웨어 또는 엔드포인트 호출
            response = await call_next(request)
            
        except Exception as e:
            # 에러 발생 시 기록
            error_message = str(e)
            self.logger.logger.error(f"API 호출 중 오류 발생: {error_message}")
            
            # 에러 응답 생성
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "서버 내부 오류가 발생했습니다.",
                    "timestamp": time.time()
                }
            )
        
        # 응답 시간 계산
        process_time_ms = int((time.time() - start_time) * 1000)
        
        # 데이터베이스에 로그 저장
        await self._save_api_log(
            log_id=log_id,
            user_id=user_id,
            endpoint=endpoint,
            method=method,
            ip_address=client_ip,
            user_agent=user_agent,
            request_body=request_body,
            response_status=response.status_code if response else 500,
            response_time_ms=process_time_ms,
            error_message=error_message
        )
        
        # 응답 헤더에 처리 시간 추가
        if response:
            response.headers["X-Process-Time"] = str(process_time_ms)
        
        return response
    
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
    
    def _generate_log_id(self) -> str:
        """
        고유한 로그 ID 생성
        
        Returns:
            20자리 로그 ID
        """
        # UUID4의 앞 20자리 사용
        return str(uuid.uuid4()).replace('-', '')[:20]
    
    def _mask_sensitive_data(self, data: dict) -> dict:
        """
        민감한 데이터 마스킹
        
        Args:
            data: 요청 데이터
        
        Returns:
            마스킹된 데이터
        """
        if not isinstance(data, dict):
            return data
        
        sensitive_fields = [
            'password', 'passwd', 'pwd',
            'token', 'access_token', 'refresh_token',
            'secret', 'key', 'api_key',
            'credit_card', 'card_number',
            'ssn', 'social_security_number'
        ]
        
        masked_data = data.copy()
        for key, value in masked_data.items():
            if isinstance(key, str) and any(sensitive in key.lower() for sensitive in sensitive_fields):
                if isinstance(value, str) and len(value) > 0:
                    masked_data[key] = "*" * min(len(value), 8)
                else:
                    masked_data[key] = "[MASKED]"
            elif isinstance(value, dict):
                masked_data[key] = self._mask_sensitive_data(value)
        
        return masked_data
    
    async def _save_api_log(
        self,
        log_id: str,
        user_id: Optional[str],
        endpoint: str,
        method: str,
        ip_address: str,
        user_agent: str,
        request_body: Optional[str],
        response_status: int,
        response_time_ms: int,
        error_message: Optional[str]
    ):
        """
        API 사용 로그를 데이터베이스에 저장
        
        Args:
            log_id: 로그 ID
            user_id: 사용자 ID
            endpoint: API 엔드포인트
            method: HTTP 메서드
            ip_address: 클라이언트 IP
            user_agent: 사용자 에이전트
            request_body: 요청 본문
            response_status: 응답 상태 코드
            response_time_ms: 응답 시간(밀리초)
            error_message: 오류 메시지
        """
        try:
            # 데이터베이스 세션 생성
            db_gen = get_db()
            db: Session = next(db_gen)
            
            try:
                # API 사용 로그 생성
                api_log = APIUsageLog(
                    log_id=log_id,
                    user_id=user_id,
                    endpoint=endpoint,
                    method=method,
                    ip_address=ip_address,
                    user_agent=user_agent[:1000] if user_agent else None,  # 길이 제한
                    request_body=request_body[:5000] if request_body else None,  # 길이 제한
                    response_status=response_status,
                    response_time_ms=response_time_ms,
                    error_message=error_message[:1000] if error_message else None,  # 길이 제한
                    frst_register_id=user_id or 'system'
                )
                
                # 데이터베이스에 저장
                db.add(api_log)
                db.commit()
                
                self.logger.logger.info(f"[SUCCESS] API 로그 저장 완료 - ID: {log_id}, 엔드포인트: {endpoint}")
                
            except Exception as e:
                db.rollback()
                self.logger.logger.error(f"[ERROR] API 로그 저장 실패: {str(e)}")
                raise
            finally:
                db.close()
                
        except Exception as e:
            self.logger.logger.error(f"[ERROR] 데이터베이스 연결 실패: {str(e)}")
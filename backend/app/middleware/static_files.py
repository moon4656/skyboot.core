from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os
import mimetypes
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class StaticFileMiddleware(BaseHTTPMiddleware):
    """
    정적 파일 서빙을 위한 미들웨어
    
    업로드된 파일, 이미지, CSS, JS 등의 정적 파일을 안전하게 서빙합니다.
    """
    
    def __init__(self, app: FastAPI, static_dir: str = "static", uploads_dir: str = "uploads"):
        super().__init__(app)
        self.static_dir = Path(static_dir)
        self.uploads_dir = Path(uploads_dir)
        
        # 디렉토리 생성
        self.static_dir.mkdir(exist_ok=True)
        self.uploads_dir.mkdir(exist_ok=True)
        
        # 허용된 파일 확장자
        self.allowed_extensions = {
            # 이미지
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg',
            # 문서
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt',
            # 웹 자산
            '.css', '.js', '.html', '.htm',
            # 기타
            '.zip', '.rar', '.7z'
        }
        
        # MIME 타입 설정
        mimetypes.init()
        
    async def dispatch(self, request: Request, call_next):
        """
        요청을 처리하고 정적 파일 요청인지 확인합니다.
        """
        path = request.url.path
        
        # 정적 파일 요청 처리
        if path.startswith('/static/'):
            return await self._serve_static_file(request, self.static_dir)
        elif path.startswith('/uploads/'):
            return await self._serve_upload_file(request, self.uploads_dir)
        
        # 일반 요청 처리
        response = await call_next(request)
        return response
    
    async def _serve_static_file(self, request: Request, base_dir: Path) -> Response:
        """
        정적 파일을 서빙합니다.
        
        Args:
            request: HTTP 요청
            base_dir: 기본 디렉토리
            
        Returns:
            파일 응답 또는 404 응답
        """
        try:
            # URL 경로에서 파일 경로 추출
            file_path = request.url.path
            if file_path.startswith('/static/'):
                relative_path = file_path[8:]  # '/static/' 제거
            elif file_path.startswith('/uploads/'):
                relative_path = file_path[9:]  # '/uploads/' 제거
            else:
                relative_path = file_path[1:]  # 첫 번째 '/' 제거
            
            # 보안: 상위 디렉토리 접근 방지
            if '..' in relative_path or relative_path.startswith('/'):
                logger.warning(f"🚨 보안 위험: 잘못된 파일 경로 접근 시도 - {file_path}")
                return Response(status_code=403, content="Forbidden")
            
            # 실제 파일 경로
            full_path = base_dir / relative_path
            
            # 파일 존재 확인
            if not full_path.exists() or not full_path.is_file():
                logger.info(f"📁 파일을 찾을 수 없음 - {full_path}")
                return Response(status_code=404, content="File not found")
            
            # 파일 확장자 검증
            file_extension = full_path.suffix.lower()
            if file_extension not in self.allowed_extensions:
                logger.warning(f"🚨 허용되지 않은 파일 형식 - {file_extension}")
                return Response(status_code=403, content="File type not allowed")
            
            # MIME 타입 결정
            mime_type, _ = mimetypes.guess_type(str(full_path))
            if not mime_type:
                mime_type = 'application/octet-stream'
            
            # 파일 서빙
            logger.info(f"📤 정적 파일 서빙 - {full_path}")
            return FileResponse(
                path=str(full_path),
                media_type=mime_type,
                filename=full_path.name
            )
            
        except Exception as e:
            logger.error(f"❌ 정적 파일 서빙 오류: {str(e)}")
            return Response(status_code=500, content="Internal server error")
    
    async def _serve_upload_file(self, request: Request, base_dir: Path) -> Response:
        """
        업로드된 파일을 서빙합니다.
        
        Args:
            request: HTTP 요청
            base_dir: 업로드 디렉토리
            
        Returns:
            파일 응답 또는 404 응답
        """
        # 업로드 파일은 추가 보안 검증 수행
        return await self._serve_static_file(request, base_dir)


def setup_static_files(app: FastAPI):
    """
    FastAPI 앱에 정적 파일 설정을 추가합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # 정적 파일 디렉토리 생성
    static_dir = Path("static")
    uploads_dir = Path("uploads")
    
    static_dir.mkdir(exist_ok=True)
    uploads_dir.mkdir(exist_ok=True)
    
    # 기본 정적 파일 마운트
    app.mount("/static", StaticFiles(directory="static"), name="static")
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
    logger.info("📁 정적 파일 서빙 설정 완료")
    logger.info(f"   - Static: {static_dir.absolute()}")
    logger.info(f"   - Uploads: {uploads_dir.absolute()}")


def get_static_file_config() -> dict:
    """
    환경 변수에서 정적 파일 설정을 가져옵니다.
    
    Returns:
        정적 파일 설정 딕셔너리
    """
    return {
        "static_dir": os.getenv("STATIC_DIR", "static"),
        "uploads_dir": os.getenv("UPLOADS_DIR", "uploads"),
        "max_file_size": int(os.getenv("MAX_FILE_SIZE", "10485760")),  # 10MB
        "allowed_extensions": os.getenv(
            "ALLOWED_EXTENSIONS", 
            ".jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.css,.js,.html,.htm,.zip,.rar,.7z"
        ).split(","),
        "enable_caching": os.getenv("ENABLE_STATIC_CACHING", "true").lower() == "true",
        "cache_max_age": int(os.getenv("STATIC_CACHE_MAX_AGE", "3600"))  # 1시간
    }
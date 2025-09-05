from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# 미들웨어 임포트
from app.middleware.logging_middleware import LoggingMiddleware, RequestSizeMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.api_usage_middleware import APIUsageMiddleware
from app.utils.logger import get_api_logger

# API 라우터 import
from app.api.routes import api_v1

# 라이프사이클 이벤트 핸들러
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프사이클 이벤트 핸들러
    """
    # 시작 이벤트
    logger = get_api_logger()
    logger.log_custom(
        level="info",
        message="🚀 SkyBoot Core API 서버가 시작되었습니다.",
        version="1.0.0",
        environment="development"
    )
    
    yield
    
    # 종료 이벤트
    logger.log_custom(
        level="info",
        message="🛑 SkyBoot Core API 서버가 종료되었습니다."
    )

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="SkyBoot Core API",
    description="SkyBoot Core Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 미들웨어 설정 (순서 중요: 요청 크기 제한 -> API 사용 로그 -> 인증 -> 로깅)
# 주의: FastAPI는 미들웨어를 역순으로 실행하므로 실제 실행 순서는 LoggingMiddleware -> AuthMiddleware -> APIUsageMiddleware -> RequestSizeMiddleware
app.add_middleware(RequestSizeMiddleware, max_size=50 * 1024 * 1024)  # 50MB 제한
app.add_middleware(APIUsageMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "Welcome to SkyBoot Core API", "status": "running"}

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "SkyBoot Core API"}

# API 라우터 등록
app.include_router(api_v1)

# API 정보 엔드포인트
@app.get("/api/info")
async def api_info():
    return {
        "name": "SkyBoot Core API",
        "version": "1.0.0",
        "description": "SkyBoot Core Backend API",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "api_v1": "/api/v1"
        },
        "routers": {
            "user": "/api/v1/users",
            "organization": "/api/v1/organizations",
            "auth": "/api/v1/auth",
            "author_menu": "/api/v1/author-menu",
            "bbs_master": "/api/v1/bbs-master",
            "bbs": "/api/v1/bbs",
            "comment": "/api/v1/comments",
            "grp_code": "/api/v1/common-group-codes",
            "code": "/api/v1/common-codes",
            "file": "/api/v1/file-groups",
            "file_detail": "/api/v1/files",
            "menu": "/api/v1/menus",
            "log": "/api/v1/logs",
            "zip_codes": "/api/v1/zip-codes",
            "system": "/api/v1/system"
        }
    }



if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
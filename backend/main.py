from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

# 미들웨어 임포트
from app.middleware.logging_middleware import LoggingMiddleware, RequestSizeMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.api_usage_middleware import APIUsageMiddleware
from app.middleware.security import SecurityMiddleware, APIKeyMiddleware, get_security_config
from app.middleware.static_files import setup_static_files, get_static_file_config
from app.utils.logger import get_api_logger
from app.utils.production_logger import get_production_logger, setup_production_logging
import os

# API 라우터 import
from app.api.routes import api_v1

# 라이프사이클 이벤트 핸들러
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프사이클 이벤트 핸들러
    """
    # 프로덕션 환경에서는 고급 로깅 설정
    environment = os.getenv("ENVIRONMENT", "development")
    if environment == "production":
        setup_production_logging()
        prod_logger = get_production_logger()
        prod_logger.app_logger.info("🚀 SkyBoot Core API 서버가 시작되었습니다. (프로덕션 모드)")
    else:
        # 개발 환경에서는 기존 로거 사용
        logger = get_api_logger()
        logger.log_custom(
            level="info",
            message="🚀 SkyBoot Core API 서버가 시작되었습니다.",
            version="1.0.0",
            environment=environment
        )
    
    yield
    
    # 종료 이벤트
    if environment == "production":
        prod_logger = get_production_logger()
        prod_logger.app_logger.info("🛑 SkyBoot Core API 서버가 종료되었습니다.")
    else:
        logger = get_api_logger()
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

# 보안 설정 로드
security_config = get_security_config()

# 정적 파일 설정 로드
static_config = get_static_file_config()

# 미들웨어 설정 (순서 중요: 보안 -> 요청 크기 제한 -> API 키 -> API 사용 로그 -> 인증 -> 로깅)
# 주의: FastAPI는 미들웨어를 역순으로 실행하므로 실제 실행 순서는 역순
app.add_middleware(RequestSizeMiddleware, max_size=security_config.get("max_request_size", 50 * 1024 * 1024))
app.add_middleware(APIUsageMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# API 키 미들웨어 (선택적)
if security_config.get("api_keys"):
    app.add_middleware(APIKeyMiddleware, api_keys=security_config["api_keys"])

# 보안 미들웨어 (프로덕션 환경에서만)
if os.getenv("ENVIRONMENT", "development") == "production":
    app.add_middleware(
        SecurityMiddleware,
        rate_limit_requests=security_config["rate_limit_requests"],
        rate_limit_window=security_config["rate_limit_window"],
        max_request_size=security_config["max_request_size"],
        allowed_ips=security_config["allowed_ips"],
        blocked_ips=security_config["blocked_ips"],
        enable_security_headers=security_config["enable_security_headers"]
    )

# CORS 미들웨어 설정 (환경별 설정)
cors_origins = ["*"]  # 기본값
if os.getenv("ENVIRONMENT") == "production":
    # 프로덕션 환경에서는 특정 도메인만 허용
    cors_origins = os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
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

# 정적 파일 서빙 설정
setup_static_files(app)

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
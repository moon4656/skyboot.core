"""API 라우터 패키지

API v1 엔드포인트를 관리하는 라우터들을 정의합니다.
"""

from fastapi import APIRouter
from .auth_router import auth_router
from .author_menu_router import author_menu_router
from .board_router import bbs_master_router, bbs_router, comment_router
from .common_router import grp_code_router, code_router
from .file_router import file_router, file_detail_router
from .menu_router import menu_router
from .log_router import log_router
from .user_router import router as user_router
from .org_router import router as org_router
from .zip_router import router as zip_router
from .system_router import router as system_router
from .program_router import router as program_router

# API v1 라우터 생성
api_v1 = APIRouter(prefix="/api/v1")

# 인증 관련 라우터
api_v1.include_router(auth_router)

# 파일 관리 관련 라우터
api_v1.include_router(file_router)
api_v1.include_router(file_detail_router)

# 사용자 관리 관련 라우터
api_v1.include_router(user_router)

# 프로그램 관리 관련 라우터
api_v1.include_router(program_router)

# 메뉴 관리 관련 라우터
api_v1.include_router(menu_router)

# 권한 메뉴 관련 라우터
api_v1.include_router(author_menu_router)

# 조직 관리 관련 라우터
api_v1.include_router(org_router)

# 우편번호 관련 라우터
api_v1.include_router(zip_router)

# 시스템 관리 관련 라우터
api_v1.include_router(system_router)

# 게시판 관련 라우터
api_v1.include_router(bbs_master_router)
api_v1.include_router(bbs_router)
api_v1.include_router(comment_router)

# 공통 코드 관련 라우터
api_v1.include_router(grp_code_router)
api_v1.include_router(code_router)


# 로그 관리 관련 라우터
api_v1.include_router(log_router)


__all__ = ["api_v1"]
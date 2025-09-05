"""FastAPI 라우터 패키지

API 엔드포인트를 관리하는 라우터들을 정의합니다.
"""

from .routes import (
    auth_router, author_menu_router,
    bbs_master_router, bbs_router, comment_router,
    grp_code_router, code_router,
    file_router, file_detail_router,
    menu_router, log_router,
    user_router, system_router
)

__all__ = [
    "auth_router", "author_menu_router",
    "bbs_master_router", "bbs_router", "comment_router",
    "grp_code_router", "code_router",
    "file_router", "file_detail_router",
    "menu_router",
    "log_router",
    "user_router",
    "system_router"
]
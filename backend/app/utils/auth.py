"""인증 관련 유틸리티 함수

사용자 인증 및 권한 관리를 위한 유틸리티 함수들을 정의합니다.
"""

import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import AuthorInfoService

# 로거 설정
logger = logging.getLogger(__name__)

# HTTPBearer 보안 스키마
security = HTTPBearer()


def get_current_user_from_bearer(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """
    HTTPBearer 토큰에서 현재 사용자 정보를 추출합니다.
    """
    try:
        token = credentials.credentials
        auth_service = AuthorInfoService()
        user_info = auth_service.get_current_user_from_token(db, token)
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_info
    except Exception as e:
        logger.error(f"❌ HTTPBearer 인증 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증에 실패했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
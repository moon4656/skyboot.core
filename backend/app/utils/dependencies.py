"""FastAPI 의존성 주입 함수들

JWT 토큰 검증 및 사용자 인증을 위한 의존성 함수들을 정의합니다.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.auth_service import AuthorInfoService
from app.utils.jwt_utils import verify_token
from app.utils.logger import get_api_logger

logger = get_api_logger()
security = HTTPBearer()


def verify_token_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    JWT 액세스 토큰을 검증하는 의존성 함수
    
    Args:
        credentials: HTTP Bearer 토큰 자격 증명
        
    Returns:
        토큰 페이로드 (사용자 정보 포함)
        
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우 401 오류
    """
    try:
        # 토큰 검증
        payload = verify_token(credentials.credentials, "access")
        
        if not payload:
            logger.warning(f"⚠️ 토큰 검증 실패 - token: {credentials.credentials[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.log_custom("INFO", f"✅ 토큰 검증 성공 - user_id: {payload.get('user_id')}")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("GET", "/token-verify", e, "unknown")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰 검증 중 오류가 발생했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token_payload: Dict[str, Any] = Depends(verify_token_dependency)) -> Dict[str, Any]:
    """
    현재 인증된 사용자 정보를 반환하는 의존성 함수
    
    Args:
        token_payload: 검증된 토큰 페이로드
        
    Returns:
        현재 사용자 정보
    """
    return {
        "user_id": token_payload.get("user_id"),
        "email": token_payload.get("email"),
        "group_id": token_payload.get("group_id"),
        "sub": token_payload.get("sub")
    }


def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    현재 인증된 사용자 ID를 반환하는 의존성 함수
    
    Args:
        current_user: 현재 사용자 정보
        
    Returns:
        사용자 ID
    """
    return current_user["user_id"]


def get_current_user_with_db(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    데이터베이스 세션과 함께 현재 사용자 정보를 반환하는 의존성 함수
    
    Args:
        db: 데이터베이스 세션
        current_user: 현재 사용자 정보
        
    Returns:
        (db, current_user) 튜플
    """
    return db, current_user


def verify_refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    JWT 리프레시 토큰을 검증하는 의존성 함수
    
    Args:
        credentials: HTTP Bearer 토큰 자격 증명
        
    Returns:
        토큰 페이로드
        
    Raises:
        HTTPException: 토큰이 유효하지 않은 경우 401 오류
    """
    try:
        # 리프레시 토큰 검증
        payload = verify_token(credentials.credentials, "refresh")
        
        if not payload:
            logger.warning(f"⚠️ 리프레시 토큰 검증 실패 - token: {credentials.credentials[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 리프레시 토큰입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.log_custom("INFO", f"✅ 리프레시 토큰 검증 성공 - user_id: {payload.get('user_id')}")
        return payload
        
    except HTTPException:
        raise
    except Exception as e:
        logger.log_error("POST", "/refresh-token", e, "unknown")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰 검증 중 오류가 발생했습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# 별칭 함수들은 충돌을 방지하기 위해 제거됨
# verify_token = verify_token_dependency  # jwt_utils.verify_token과 충돌
# current_user = get_current_user
# current_user_id = get_current_user_id
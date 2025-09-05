"""JWT 토큰 관련 유틸리티

JWT 토큰 생성, 검증, 디코딩 기능을 제공합니다.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from jose.exceptions import JWTError
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# JWT 설정
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    액세스 토큰을 생성합니다.
    
    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 토큰 만료 시간 (기본값: 30분)
        
    Returns:
        생성된 JWT 액세스 토큰
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ 액세스 토큰 생성 완료 - user_id: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ 액세스 토큰 생성 실패: {str(e)}")
        raise


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    리프레시 토큰을 생성합니다.
    
    Args:
        data: 토큰에 포함할 데이터
        expires_delta: 토큰 만료 시간 (기본값: 7일)
        
    Returns:
        생성된 JWT 리프레시 토큰
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"✅ 리프레시 토큰 생성 완료 - user_id: {data.get('sub')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"❌ 리프레시 토큰 생성 실패: {str(e)}")
        raise


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    JWT 토큰을 검증하고 페이로드를 반환합니다.
    
    Args:
        token: 검증할 JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")
        
    Returns:
        토큰이 유효한 경우 페이로드, 그렇지 않으면 None
    """
    try:
        # 토큰 형식 검증
        if not token or not isinstance(token, str):
            logger.warning(f"⚠️ 토큰이 비어있거나 잘못된 형식입니다: {type(token)}")
            return None
        
        # JWT 형식 확인 (3개 부분으로 구성되어야 함)
        token_parts = token.split('.')
        if len(token_parts) != 3:
            logger.warning(f"⚠️ JWT 토큰 형식 오류 - segments: {len(token_parts)}, token: {token[:50]}...")
            return None
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 토큰 타입 확인
        if payload.get("type") != token_type:
            logger.warning(f"⚠️ 토큰 타입 불일치 - 예상: {token_type}, 실제: {payload.get('type')}")
            return None
        
        # 만료 시간 확인
        exp = payload.get("exp")
        if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
            logger.warning(f"⚠️ 토큰 만료 - user_id: {payload.get('sub')}")
            return None
        
        logger.info(f"✅ 토큰 검증 성공 - user_id: {payload.get('sub')}, type: {token_type}")
        return payload
        
    except JWTError as e:
        logger.warning(f"⚠️ 토큰 검증 실패: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"❌ 토큰 검증 중 오류: {str(e)}")
        return None


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    JWT 토큰을 디코딩합니다 (검증 없이).
    
    Args:
        token: 디코딩할 JWT 토큰
        
    Returns:
        토큰 페이로드 또는 None
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        logger.error(f"❌ 토큰 디코딩 실패: {str(e)}")
        return None


def get_token_expiry_time(token_type: str = "access") -> int:
    """
    토큰 타입별 만료 시간을 초 단위로 반환합니다.
    
    Args:
        token_type: 토큰 타입 ("access" 또는 "refresh")
        
    Returns:
        만료 시간 (초)
    """
    if token_type == "access":
        return ACCESS_TOKEN_EXPIRE_MINUTES * 60
    elif token_type == "refresh":
        return REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    else:
        return ACCESS_TOKEN_EXPIRE_MINUTES * 60


def create_token_pair(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    액세스 토큰과 리프레시 토큰 쌍을 생성합니다.
    
    Args:
        user_data: 사용자 데이터
        
    Returns:
        토큰 쌍 정보
    """
    try:
        # 토큰 페이로드 준비
        token_data = {
            "sub": user_data.get("user_id"),
            "user_id": user_data.get("user_id"),
            "email": user_data.get("email_adres"),
            "group_id": user_data.get("group_id")
        }
        
        # 토큰 생성
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        logger.info(f"✅ 토큰 쌍 생성 완료 - user_id: {user_data.get('user_id')}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": get_token_expiry_time("access")
        }
        
    except Exception as e:
        logger.error(f"❌ 토큰 쌍 생성 실패: {str(e)}")
        raise
"""사용자 관련 API 라우터

사용자 정보, 조직, 우편번호 관련 CRUD API 엔드포인트를 제공합니다.
인증 없는 원클릭 로그인과 HTTPBearer 인증이 필요한 엔드포인트를 포함합니다.
"""

import traceback
from typing import List, Optional, Dict, Any
from decimal import Decimal
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user_models import UserInfo
from app.schemas.user_schemas import (
    # UserInfo 스키마
    UserInfoCreate, UserInfoUpdate, UserInfoResponse, UserInfoPagination, UserInfoBasicBase,
    # 검색 및 통계 스키마
    UserSearchParams, UserStatistics
)
from app.schemas.auth_schemas import UserLoginRequest, UserLoginResponse
from app.services.user_service import UserInfoService
from app.services.auth_service import AuthorInfoService
from app.services.log_service import LoginLogService
from app.utils.dependencies import get_current_user, get_current_user_id, verify_token_dependency
from app.utils.auth import get_current_user_from_bearer

# 로거 설정
logger = logging.getLogger(__name__)

# IP 주소 추출 함수
def get_client_ip(request: Request) -> str:
    """
    클라이언트 IP 주소를 추출합니다.
    """
    # X-Forwarded-For 헤더 확인 (프록시 환경)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # 첫 번째 IP가 실제 클라이언트 IP
        return forwarded_for.split(",")[0].strip()
    
    # X-Real-IP 헤더 확인 (nginx 등)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # 직접 연결된 클라이언트 IP
    if hasattr(request.client, 'host') and request.client.host:
        return request.client.host
    
    return "unknown"

router = APIRouter(prefix="/users", tags=["사용자 관리"])


# ==================== 인증 없는 엔드포인트 ====================

@router.post("/one-click-login", response_model=UserLoginResponse, summary="원클릭 로그인")
async def one_click_login(
    login_data: UserLoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    원클릭 로그인을 처리합니다. (인증 불필요)
    
    - **user_id**: 사용자 ID
    - **password**: 비밀번호
    
    이 엔드포인트는 인증 없이 접근할 수 있으며, 성공 시 JWT 토큰을 반환하고 응답 헤더에 access token을 포함합니다.
    """
    # 클라이언트 IP 주소 추출
    client_ip = request.client.host if request.client else "unknown"
    if "x-forwarded-for" in request.headers:
        client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
    elif "x-real-ip" in request.headers:
        client_ip = request.headers["x-real-ip"]
    
    login_log_service = LoginLogService()
    
    try:
        # 사용자 인증 및 JWT 토큰 생성
        auth_service = AuthorInfoService()
        auth_result = auth_service.authenticate_and_create_tokens(
            db, login_data.user_id, login_data.password
        )
        
        if not auth_result:
            # 로그인 실패 로그 기록
            login_log_service.create_login_log(
                db=db,
                user_id=login_data.user_id,
                ip_address=client_ip,
                login_status="FAIL"
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자 ID 또는 비밀번호가 올바르지 않습니다."
            )
        
        # 로그인 성공 로그 기록
        login_log_service.create_login_log(
            db=db,
            user_id=login_data.user_id,
            ip_address=client_ip,
            login_status="SUCCESS"
        )
        
        # 응답 헤더에 access token 추가
        response.headers["Access-Token"] = auth_result["access_token"]
        response.headers["Authorization"] = f"Bearer {auth_result['access_token']}"
        
        response_data = UserLoginResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result["expires_in"],
            user_info=auth_result["user_info"]
        )
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        # 로그인 오류 로그 기록
        try:
            login_log_service.create_login_log(
                db=db,
                user_id=login_data.user_id,
                ip_address=client_ip,
                login_status="ERROR",
                error_message=str(e)
            )
        except Exception:
            pass  # 로그 기록 실패 시 무시
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다."
        )


# ==================== HTTPBearer 인증이 필요한 엔드포인트 ====================

@router.get("/profile", response_model=UserInfoResponse, summary="내 프로필 조회")
async def get_my_profile(
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    현재 로그인한 사용자의 프로필 정보를 조회합니다.
    
    - **Authorization**: Bearer 토큰 필요
    """
    try:
        service = UserInfoService()
        user = service.get_by_user_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return user
    except Exception as e:
        logger.error(f"❌ 프로필 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 조회 중 오류가 발생했습니다."
        )

@router.put("/profile", response_model=UserInfoResponse, summary="내 프로필 수정")
async def update_my_profile(
    user_data: UserInfoUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    현재 로그인한 사용자의 프로필 정보를 수정합니다.
    
    - **user_data**: 수정할 사용자 정보
    - **Authorization**: Bearer 토큰 필요
    """
    try:
        service = UserInfoService()
        user = service.get_by_user_id(db, current_user["user_id"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        return service.update(db, user, user_data, current_user["user_id"])
    except Exception as e:
        logger.error(f"❌ 프로필 수정 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 수정 중 오류가 발생했습니다."
        )

@router.get("/list", response_model=UserInfoPagination, summary="사용자 목록 조회 (관리자)")
async def get_users_list(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    모든 사용자 목록을 조회합니다. (관리자 권한 필요)
    
    - **Authorization**: Bearer 토큰 필요
    """
    try:
        service = UserInfoService()
        users = service.get_multi(db, skip=skip, limit=limit)
        total = service.count(db)
        
        pages = (total + limit - 1) // limit
        page = (skip // limit) + 1
        
        return UserInfoPagination(
            items=users,
            total=total,
            page=page,
            size=limit,
            pages=pages
        )
    except Exception as e:
        logger.error(f"❌ 사용자 목록 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 목록 조회 중 오류가 발생했습니다."
        )


# ==================== 기존 UserInfo 엔드포인트 (기존 인증 방식 유지) ====================

@router.post("/admin/create", response_model=UserInfoResponse, summary="사용자 생성 (관리자용)")
async def create_user(
    user_data: UserInfoCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)  # JWT 토큰에서 사용자 ID 추출
):
    """
    새로운 사용자를 생성합니다.
    
    - **user_id**: 업무사용자ID (필수, 고유값)
    - **user_nm**: 사용자명 (필수)
    - **password**: 비밀번호 (필수, 8자 이상)
    - **email_adres**: 이메일주소 (선택, 고유값)
    - **orgnzt_id**: 조직ID (선택)
    - **기타**: 다양한 사용자 정보 필드들
    """
    try:
        logger.info(f"🚀 사용자 생성 요청 - user_id: {user_data.user_id}, user_nm: {user_data.user_nm}")
        service = UserInfoService()
        result = service.create(db, user_data, current_user_id)
        logger.info(f"✅ 사용자 생성 성공 - user_id: {result.user_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 사용자 생성 실패 - user_id: {user_data.user_id}, 오류: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e


@router.post("/basic", response_model=UserInfoBasicBase, summary="사용자 기본 자료 생성")
async def create_user_basic(
    user_data: UserInfoBasicBase,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)  # JWT 토큰에서 사용자 ID 추출
):
    """
    새로운 사용자를 생성합니다.
    
    - **user_id**: 업무사용자ID (필수, 고유값)
    - **user_nm**: 사용자명 (필수)
    - **password**: 비밀번호 (필수, 8자 이상)
    - **email_adres**: 이메일주소 (선택, 고유값)
    - **orgnzt_id**: 조직ID (선택)
    - **기타**: 다양한 사용자 정보 필드들
    """
    try:
        logger.info(f"🚀 기본 사용자 생성 요청 - user_id: {user_data.user_id}, user_nm: {user_data.user_nm}")
        service = UserInfoService()
        result = service.create(db, user_data, current_user_id)
        logger.info(f"✅ 기본 사용자 생성 성공 - user_id: {result.user_id}")
        return result
    except Exception as e:
        logger.error(f"❌ 기본 사용자 생성 실패 - user_id: {user_data.user_id}, 오류: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise e


@router.get("/", response_model=UserInfoPagination, summary="사용자 목록 조회")
async def get_users(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # JWT 토큰 검증 및 사용자 정보 추출
):
    """
    사용자 목록을 페이지네이션으로 조회합니다.
    
    - **skip**: 건너뛸 개수 (기본값: 0)
    - **limit**: 조회할 개수 (기본값: 100, 최대: 1000)
    """
    service = UserInfoService()
    users = service.get_multi(db, skip=skip, limit=limit)
    total = service.count(db)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return UserInfoPagination(
        items=users,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/search", response_model=List[UserInfoResponse], summary="사용자 검색 (관리자)")
async def search_users(
    query: str = Query(..., description="검색 키워드"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    사용자를 검색합니다. (관리자 권한 필요)
    
    - **query**: 검색할 키워드 (사용자명, 이메일 등)
    - **Authorization**: Bearer 토큰 필요
    """
    try:
        service = UserInfoService()
        # 검색 키워드를 UserSearchParams 객체로 변환
        search_params = UserSearchParams(
            user_nm=query,
            email_adres=query  # 사용자명과 이메일 모두에서 검색
        )
        users, total = service.search_users(db, search_params)
        return users
    except Exception as e:
        logger.error(f"❌ 사용자 검색 실패: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용자 검색 중 오류가 발생했습니다."
        )


@router.get("/statistics", response_model=UserStatistics, summary="사용자 통계")
async def get_user_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):  
    """
    사용자 관련 통계 정보를 조회합니다.
    
    - 전체 사용자 수
    - 활성 사용자 수
    - 잠금된 사용자 수
    - 상태별 사용자 수
    - 조직별 사용자 수
    - 최근 가입자 수
    """
    service = UserInfoService()
    return service.get_user_statistics(db)


@router.get("/{user_id}", response_model=UserInfoResponse, summary="사용자 상세 조회")
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user)
):
    """
    특정 사용자의 상세 정보를 조회합니다.
    
    - **user_id**: 업무사용자ID
    """
    service = UserInfoService()
    user = service.get_by_user_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return user


@router.put("/{user_id}", response_model=UserInfoResponse, summary="사용자 정보 수정")
async def update_user(
    user_id: str,
    user_data: UserInfoUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 정보를 수정합니다.
    
    - **user_id**: 업무사용자ID
    - **user_data**: 수정할 사용자 정보
    """
    service = UserInfoService()
    user = service.get_by_user_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    return service.update(db, user, user_data, current_user.get('user_id'))


@router.delete("/{user_id}", summary="사용자 삭제")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자를 삭제합니다.
    
    - **user_id**: 업무사용자ID
    """
    service = UserInfoService()
    user = service.get_by_user_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )
    service.delete(db, user.user_id)
    return {"message": "사용자가 성공적으로 삭제되었습니다."}


@router.post("/{user_id}/lock", response_model=UserInfoResponse, summary="사용자 계정 잠금")
async def lock_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 계정을 잠금 처리합니다.
    
    - **user_id**: 업무사용자ID
    """
    service = UserInfoService()
    return service.lock_user(db, user_id, current_user.get('user_id'))


@router.post("/{user_id}/unlock", response_model=UserInfoResponse, summary="사용자 계정 잠금 해제")
async def unlock_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 계정의 잠금을 해제합니다.
    
    - **user_id**: 업무사용자ID
    """
    service = UserInfoService()
    return service.unlock_user(db, user_id, current_user.get('user_id'))
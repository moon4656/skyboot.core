"""인증 관련 API 라우터

사용자 인증 및 권한 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.services import AuthorInfoService, LoginLogService
from app.utils.dependencies import get_current_user
from app.schemas.auth_schemas import (
    AuthorInfoResponse, AuthorInfoCreate, AuthorInfoUpdate,
    AuthorInfoPagination,
    UserLoginRequest, UserLoginResponse, UserPermissionResponse,
    TokenRefreshRequest, TokenRefreshResponse
)
from ...schemas.user_schemas import UserInfoBase, UserInfoResponse, UserInfoPagination

# 인증 라우터
auth_router = APIRouter(
    prefix="/auth",
    tags=["인증 관리"],
    responses={404: {"description": "Not found"}}
)



# 서비스 인스턴스는 각 함수 내에서 초기화됩니다


# ==================== 사용자 인증 API ====================

@auth_router.post("/login", response_model=UserLoginResponse, summary="사용자 로그인")
async def login_user(
    login_data: UserLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    사용자 로그인을 처리합니다.
    
    - **user_id**: 사용자 ID
    - **password**: 비밀번호
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
        
        response = UserLoginResponse(
            access_token=auth_result["access_token"],
            refresh_token=auth_result["refresh_token"],
            token_type=auth_result["token_type"],
            expires_in=auth_result["expires_in"],
            user_info=auth_result["user_info"]
        )
        
        return response
        
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
        except:
            pass  # 로그 기록 실패 시에도 원본 오류를 유지
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 오류가 발생했습니다: {str(e)}"
        )


@auth_router.post("/refresh", response_model=TokenRefreshResponse, summary="토큰 갱신")
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: Session = Depends(get_db)
):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급합니다.
    
    - **refresh_token**: 리프레시 토큰
    """
    try:
        # 리프레시 토큰을 사용하여 새로운 액세스 토큰 생성
        auth_service = AuthorInfoService()
        token_result = auth_service.refresh_access_token(db, token_request.refresh_token)
        
        if not token_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다."
            )
        
        response = TokenRefreshResponse(
            access_token=token_result["access_token"],
            token_type=token_result["token_type"],
            expires_in=token_result["expires_in"]
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 갱신 처리 중 오류가 발생했습니다: {str(e)}"
        )

# @auth_router.get("/users", response_model=UserInfoPagination, summary="사용자 목록 조회")
# async def get_users(
#     skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
#     limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
#     search: Optional[str] = Query(None, description="검색어 (사용자명, 이메일)"),
#     author_code: Optional[str] = Query(None, description="권한 코드"),
#     use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
#     db: Session = Depends(get_db)
# ):
#     """
#     사용자 목록을 조회합니다.
    
#     - **skip**: 건너뛸 레코드 수 (페이징)
#     - **limit**: 조회할 최대 레코드 수
#     - **search**: 검색어 (사용자명, 이메일에서 검색)
#     - **author_code**: 권한 코드로 필터링
#     - **use_at**: 사용 여부로 필터링
#     """
#     try:
#         author_info_service = AuthorInfoService()
#         users = author_info_service.search_users(
#             db=db,
#             search_term=search,
#             author_code=author_code,
#             use_at=use_at,
#             skip=skip,
#             limit=limit
#         )
        
#         total_count = author_info_service.count(
#             db=db,
#             search_term=search,
#             author_code=author_code,
#             use_at=use_at,
#             group_id=None,
#             emplyr_sttus_code=None
#         )
        
#         return UserInfoPagination(
#             items=users,
#             total=total_count,
#             skip=skip,
#             limit=limit
#         )
        
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
#         )


# @auth_router.get("/users/{user_id}", response_model=UserInfoBase, summary="사용자 상세 조회")
# async def get_user(
#     user_id: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     특정 사용자의 상세 정보를 조회합니다.
    
#     - **user_id**: 조회할 사용자 ID
#     """
#     try:
#         author_info_service = AuthorInfoService()
#         user = author_info_service.get_by_user_id(db=db, user_id=user_id)
        
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"사용자를 찾을 수 없습니다: {user_id}"
#             )
        
#         return user
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 조회 중 오류가 발생했습니다: {str(e)}"
#         )


# @auth_router.post("/users", response_model=UserInfoBase, summary="사용자 생성")
# async def create_user(
#     user_data: UserInfoBase,
#     db: Session = Depends(get_db)
# ):
#     """
#     새로운 사용자를 생성합니다.
    
#     - **user_id**: 사용자 ID (고유값)
#     - **user_nm**: 사용자명
#     - **password**: 비밀번호
#     - **email_adres**: 이메일 주소
#     - **author_code**: 권한 코드
#     """
#     try:
#         author_info_service = AuthorInfoService()
#         # 중복 확인
#         existing_user = author_info_service.get_by_user_id(db=db, user_id=user_data.user_id)
#         if existing_user:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f"이미 존재하는 사용자 ID입니다: {user_data.user_id}"
#             )
        
#         user = author_info_service.create_user(
#             db=db,
#             user_data=user_data
#         )
        
#         return user
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 생성 중 오류가 발생했습니다: {str(e)}"
#         )


# @auth_router.put("/users/{user_id}", response_model=UserInfoBase, summary="사용자 정보 수정")
# async def update_user(
#     user_id: str,
#     user_data: AuthorInfoUpdate,
#     db: Session = Depends(get_db)
# ):
#     """
#     사용자 정보를 수정합니다.
    
#     - **user_id**: 수정할 사용자 ID
#     - **user_nm**: 사용자명
#     - **email_adres**: 이메일 주소
#     - **author_code**: 권한 코드
#     - **use_at**: 사용 여부
#     """
#     try:
#         author_info_service = AuthorInfoService()
#         user = author_info_service.get_by_user_id(db=db, user_id=user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"사용자를 찾을 수 없습니다: {user_id}"
#             )
        
#         updated_user = author_info_service.update(
#             db=db,
#             db_obj=user,
#             obj_in=user_data
#         )
        
#         return updated_user
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 정보 수정 중 오류가 발생했습니다: {str(e)}"
#         )


# @auth_router.delete("/users/{user_id}", summary="사용자 삭제")
# async def delete_user(
#     user_id: str,
#     db: Session = Depends(get_db)
# ):
#     """
#     사용자를 삭제합니다 (소프트 삭제).
    
#     - **user_id**: 삭제할 사용자 ID
#     """
#     try:
#         author_info_service = AuthorInfoService()
#         user = author_info_service.get_by_user_id(db=db, user_id=user_id)
#         if not user:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"사용자를 찾을 수 없습니다: {user_id}"
#             )
        
#         author_info_service.soft_delete(db=db, db_obj=user)
        
#         return {"message": f"사용자가 삭제되었습니다: {user_id}"}
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"사용자 삭제 중 오류가 발생했습니다: {str(e)}"
#         )


@auth_router.put("/users/{user_id}/password", summary="비밀번호 변경")
async def change_password(
    user_id: str,
    current_password: str,
    new_password: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자 비밀번호를 변경합니다.
    
    - **user_id**: 사용자 ID
    - **current_password**: 현재 비밀번호
    - **new_password**: 새 비밀번호
    """
    try:
        author_info_service = AuthorInfoService()
        success = author_info_service.update_password(
            db=db,
            user_id=user_id,
            current_password=current_password,
            new_password=new_password
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="현재 비밀번호가 올바르지 않습니다"
            )
        
        return {"message": "비밀번호가 성공적으로 변경되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"비밀번호 변경 중 오류가 발생했습니다: {str(e)}"
        )


@auth_router.get("/users/{user_id}/permissions", response_model=UserPermissionResponse, summary="사용자 권한 조회")
async def get_user_permissions(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    사용자의 권한 정보를 조회합니다.
    
    - **user_id**: 사용자 ID
    """
    try:
        author_info_service = AuthorInfoService()
        permissions = author_info_service.get_user_permissions(db=db, user_id=user_id)
        
        return UserPermissionResponse(
            user_id=user_id,
            permissions=permissions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 권한 조회 중 오류가 발생했습니다: {str(e)}"
        )
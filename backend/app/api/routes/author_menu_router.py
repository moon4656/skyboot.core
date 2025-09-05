"""권한 메뉴 관련 API 라우터

권한 메뉴 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import AuthorMenuService
from app.schemas.auth_schemas import (
    AuthorMenuResponse, AuthorMenuCreate, AuthorMenuUpdate,
    AuthorMenuPagination
)
from app.utils.auth import get_current_user_from_bearer

# 권한 메뉴 라우터
author_menu_router = APIRouter(
    prefix="/author-menu",
    tags=["권한 메뉴 관리"],
    responses={404: {"description": "Not found"}}
)


# ==================== 권한 메뉴 API ====================

@author_menu_router.get("/", response_model=AuthorMenuPagination, summary="권한 메뉴 목록 조회")
async def get_author_menus(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    author_code: Optional[str] = Query(None, description="권한 코드"),
    menu_id: Optional[str] = Query(None, description="메뉴 ID"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    권한 메뉴 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **author_code**: 권한 코드로 필터링
    - **menu_id**: 메뉴 ID로 필터링
    """
    try:
        author_menu_service = AuthorMenuService()
        author_menus = author_menu_service.get_multi(
            db=db,
            skip=skip,
            limit=limit
        )
        
        # 필터링 적용
        if author_code or menu_id:
            filtered_menus = []
            for menu in author_menus:
                if author_code and menu.author_code != author_code:
                    continue
                if menu_id and menu.menu_id != menu_id:
                    continue
                filtered_menus.append(menu)
            author_menus = filtered_menus
        
        total_count = author_menu_service.count(db=db)
        
        return AuthorMenuPagination(
            items=author_menus,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한 메뉴 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@author_menu_router.get("/author/{author_code}", response_model=List[AuthorMenuResponse], summary="권한별 메뉴 조회")
async def get_menus_by_author(
    author_code: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 권한의 메뉴 목록을 조회합니다.
    
    - **author_code**: 권한 코드
    """
    try:
        author_menu_service = AuthorMenuService()
        menus = author_menu_service.get_by_author_code(db=db, author_code=author_code)
        return menus
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한별 메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )


@author_menu_router.get("/menu/{menu_id}", response_model=List[AuthorMenuResponse], summary="메뉴별 권한 조회")
async def get_authors_by_menu(
    menu_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 권한 목록을 조회합니다.
    
    - **menu_id**: 메뉴 ID
    """
    try:
        author_menu_service = AuthorMenuService()
        authors = author_menu_service.get_by_menu_id(db=db, menu_id=menu_id)
        return authors
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴별 권한 조회 중 오류가 발생했습니다: {str(e)}"
        )


@author_menu_router.post("/", response_model=AuthorMenuResponse, summary="권한 메뉴 생성")
async def create_author_menu(
    author_menu_data: AuthorMenuCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 권한 메뉴를 생성합니다.
    
    - **author_code**: 권한 코드
    - **menu_id**: 메뉴 ID
    - **creat_at**: 생성 권한 (Y/N)
    - **read_at**: 읽기 권한 (Y/N)
    - **updt_at**: 수정 권한 (Y/N)
    - **delete_at**: 삭제 권한 (Y/N)
    """
    try:
        author_menu_service = AuthorMenuService()
        # 중복 확인
        existing_menu = author_menu_service.check_permission(
            db=db,
            author_code=author_menu_data.author_code,
            menu_id=author_menu_data.menu_id
        )
        
        if existing_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 권한 메뉴입니다: {author_menu_data.author_code}-{author_menu_data.menu_id}"
            )
        
        author_menu = author_menu_service.create(db=db, obj_in=author_menu_data)
        return author_menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한 메뉴 생성 중 오류가 발생했습니다: {str(e)}"
        )


@author_menu_router.put("/permissions", summary="권한 부여/취소")
async def manage_permission(
    author_code: str,
    menu_id: str,
    grant: bool = True,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    권한을 부여하거나 취소합니다.
    
    - **author_code**: 권한 코드
    - **menu_id**: 메뉴 ID
    - **grant**: True면 권한 부여, False면 권한 취소
    """
    try:
        author_menu_service = AuthorMenuService()
        if grant:
            success = author_menu_service.grant_permission(
                db=db,
                author_code=author_code,
                menu_id=menu_id
            )
            message = "권한이 부여되었습니다"
        else:
            success = author_menu_service.revoke_permission(
                db=db,
                author_code=author_code,
                menu_id=menu_id
            )
            message = "권한이 취소되었습니다"
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="권한 처리에 실패했습니다"
            )
        
        return {"message": message}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한 처리 중 오류가 발생했습니다: {str(e)}"
        )


@author_menu_router.delete("/{author_code}/{menu_id}", summary="권한 메뉴 삭제")
async def delete_author_menu(
    author_code: str,
    menu_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    권한 메뉴를 삭제합니다.
    
    - **author_code**: 권한 코드
    - **menu_id**: 메뉴 ID
    """
    try:
        author_menu_service = AuthorMenuService()
        author_menu = author_menu_service.check_permission(
            db=db,
            author_code=author_code,
            menu_id=menu_id
        )
        
        if not author_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"권한 메뉴를 찾을 수 없습니다: {author_code}-{menu_id}"
            )
        
        author_menu_service.remove(db=db, id=author_menu.author_code)
        
        return {"message": f"권한 메뉴가 삭제되었습니다: {author_code}-{menu_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"권한 메뉴 삭제 중 오류가 발생했습니다: {str(e)}"
        )
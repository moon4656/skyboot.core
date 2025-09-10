"""메뉴 관리 API 라우터

메뉴 정보 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import MenuInfoService
from app.utils.auth import get_current_user_from_bearer
from app.schemas.menu_schemas import (
    MenuInfoResponse, MenuInfoCreate, MenuInfoUpdate,
    MenuInfoPagination, MenuTreeNode, MenuWithPermission,
    MenuTreeWithPermission, MenuSearchParams, MenuMoveRequest,
    MenuOrderUpdate, MenuCopyRequest, MenuStatistics,
    MenuPathResponse, MenuValidationResponse, MenuExportResponse,
    MenuImportRequest
)

# 메뉴 라우터
menu_router = APIRouter(
    prefix="/menus",
    tags=["메뉴 관리"],
    responses={404: {"description": "Not found"}}
)

# 서비스 인스턴스는 각 함수에서 생성


# ==================== 메뉴 기본 CRUD API ====================

@menu_router.get("/", response_model=MenuInfoPagination, summary="메뉴 목록 조회")
async def get_menus(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    search: Optional[str] = Query(None, description="검색어 (메뉴명)"),
    menu_ty: Optional[str] = Query(None, description="메뉴 유형"),
    upper_menu_id: Optional[str] = Query(None, description="상위 메뉴 ID"),
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **search**: 검색어 (메뉴명에서 검색)
    - **menu_ty**: 메뉴 유형으로 필터링
    - **upper_menu_id**: 상위 메뉴 ID로 필터링
    - **use_at**: 사용 여부로 필터링
    """
    try:
        menu_service = MenuInfoService()
        
        menus = menu_service.search_menus(
            db=db,
            search_term=search,
            skip=skip,
            limit=limit
        )
        
        total_count = menu_service.count(db=db)
        
        return MenuInfoPagination(
            items=menus,
            total=total_count,
            page=skip // limit + 1,
            size=limit,
            pages=(total_count + limit - 1) // limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/tree", response_model=List[MenuTreeNode], summary="메뉴 트리 조회")
async def get_menu_tree(
    use_at: Optional[str] = Query("Y", description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    계층형 메뉴 트리를 조회합니다.
    
    - **use_at**: 사용 여부로 필터링
    """
    try:
        menu_service = MenuInfoService()
        menu_tree = menu_service.get_menu_tree(db=db, use_at=use_at)
        return menu_tree
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 트리 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/root", response_model=List[MenuInfoResponse], summary="루트 메뉴 조회")
async def get_root_menus(
    use_at: Optional[str] = Query('Y', description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    루트 메뉴 목록을 조회합니다.
    
    - **use_at**: 사용 여부로 필터링
    """
    try:
        menu_service = MenuInfoService()
        root_menus = menu_service.get_root_menus(db=db, use_at=use_at)
        return root_menus
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"루트 메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/statistics", response_model=MenuStatistics, summary="메뉴 통계 조회")
async def get_menu_statistics(
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 통계 정보를 조회합니다.
    """
    try:
        menu_service = MenuInfoService()
        statistics = menu_service.get_menu_statistics(db=db)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.put("/order", summary="메뉴 순서 일괄 업데이트")
async def update_menu_order(
    order_request: dict,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴의 정렬 순서를 일괄 업데이트합니다.
    
    - **order_request**: {"menu_orders": [{"menu_id": "MENU1", "menu_ordr": 1}, ...]}
    """
    try:
        menu_service = MenuInfoService()
        
        # menu_orders 추출 및 변환
        menu_orders = order_request.get('menu_orders', [])
        converted_orders = []
        
        for order_info in menu_orders:
            converted_orders.append({
                'menu_no': order_info.get('menu_id'),
                'menu_ordr': order_info.get('menu_ordr')
            })
        
        success = menu_service.update_menu_order(
            db=db, 
            menu_orders=converted_orders,
            user_id=current_user.get('user_id', 'system')
        )
        
        if success:
            return {"message": "메뉴 순서가 업데이트되었습니다"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="메뉴 순서 업데이트에 실패했습니다"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 순서 업데이트 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/{menu_id}", response_model=MenuInfoResponse, summary="메뉴 상세 조회")
async def get_menu(
    menu_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 상세 정보를 조회합니다.
    
    - **menu_id**: 메뉴 ID
    """
    try:
        menu_service = MenuInfoService()
        menu = menu_service.get_by_menu_id(db=db, menu_id=menu_id)
        
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴를 찾을 수 없습니다: {menu_id}"
            )
        
        return menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/{menu_id}/children", response_model=List[MenuInfoResponse], summary="하위 메뉴 조회")
async def get_child_menus(
    menu_id: str,
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 하위 메뉴 목록을 조회합니다.
    
    - **menu_id**: 상위 메뉴 ID
    - **use_at**: 사용 여부로 필터링
    """
    try:
        menu_service = MenuInfoService()
        child_menus = menu_service.get_child_menus(db=db, parent_menu_id=menu_id, use_at=use_at)
        return child_menus
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"하위 메뉴 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/{menu_id}/breadcrumb", response_model=List[MenuPathResponse], summary="메뉴 경로 조회")
async def get_menu_breadcrumb(
    menu_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 메뉴의 경로(breadcrumb)를 조회합니다.
    
    - **menu_id**: 메뉴 ID
    """
    try:
        menu_service = MenuInfoService()
        menu = menu_service.get_by_menu_id(db=db, menu_id=menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴를 찾을 수 없습니다: {menu_id}"
            )
        
        breadcrumb_menus = menu_service.get_menu_breadcrumb(db=db, menu_id=menu_id)
        
        # MenuInfo 객체들을 MenuPathResponse 형식으로 변환
        breadcrumb_response = []
        for i, menu in enumerate(breadcrumb_menus):
            # 전체 경로 생성
            path_parts = [m.menu_nm for m in breadcrumb_menus[:i+1]]
            full_path = " > ".join(path_parts)
            
            # breadcrumb 정보 생성
            breadcrumb_info = [
                {"menu_id": m.menu_no, "menu_nm": m.menu_nm} 
                for m in breadcrumb_menus[:i+1]
            ]
            
            menu_path = {
                "menu_id": menu.menu_no,
                "menu_nm": menu.menu_nm,
                "menu_level": menu.menu_ordr,  # menu_level 대신 menu_ordr 사용
                "full_path": full_path,
                "breadcrumb": breadcrumb_info
            }
            breadcrumb_response.append(menu_path)
        
        return breadcrumb_response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 경로 조회 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.post("/", response_model=MenuInfoResponse, status_code=201, summary="메뉴 생성")
async def create_menu(
    menu_data: MenuInfoCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 메뉴를 생성합니다.
    
    - **menu_id**: 메뉴 ID (고유값)
    - **menu_nm**: 메뉴명
    - **upper_menu_id**: 상위 메뉴 ID (선택사항)
    - **menu_ty**: 메뉴 유형
    - **menu_url**: 메뉴 URL
    """
    try:
        menu_service = MenuInfoService()
        # 중복 확인
        existing_menu = menu_service.get_by_menu_id(db=db, menu_id=menu_data.menu_no)
        if existing_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 메뉴 번호입니다: {menu_data.menu_no}"
            )
        
        # 상위 메뉴 존재 확인
        if hasattr(menu_data, 'upper_menu_no') and menu_data.upper_menu_no:
            parent_menu = menu_service.get_by_menu_id(db=db, menu_id=menu_data.upper_menu_no)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"상위 메뉴를 찾을 수 없습니다: {menu_data.upper_menu_no}"
                )
        
        menu = menu_service.create_menu(db=db, menu_data=menu_data)
        return menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 생성 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.put("/{menu_id}", response_model=MenuInfoResponse, summary="메뉴 수정")
async def update_menu(
    menu_id: str,
    menu_data: MenuInfoUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 정보를 수정합니다.
    
    - **menu_id**: 수정할 메뉴 ID
    """
    try:
        menu_service = MenuInfoService()
        menu = menu_service.get_by_menu_id(db=db, menu_id=menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴를 찾을 수 없습니다: {menu_id}"
            )
        
        # 상위 메뉴 변경 시 검증
        if menu_data.upper_menu_no and menu_data.upper_menu_no != menu.upper_menu_no:
            if menu_data.upper_menu_no == menu_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="자기 자신을 상위 메뉴로 설정할 수 없습니다"
                )
            
            parent_menu = menu_service.get_by_menu_id(db=db, menu_id=menu_data.upper_menu_no)
            if not parent_menu:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"상위 메뉴를 찾을 수 없습니다: {menu_data.upper_menu_no}"
                )
        
        updated_menu = menu_service.update(
            db=db,
            db_obj=menu,
            obj_in=menu_data
        )
        
        return updated_menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 수정 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.delete("/{menu_id}", summary="메뉴 삭제")
async def delete_menu(
    menu_id: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴를 삭제합니다 (소프트 삭제).
    
    - **menu_id**: 삭제할 메뉴 ID
    """
    try:
        menu_service = MenuInfoService()
        menu = menu_service.get_by_menu_id(db=db, menu_id=menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴를 찾을 수 없습니다: {menu_id}"
            )
        
        # 하위 메뉴 존재 확인
        child_menus = menu_service.get_child_menus(db=db, parent_menu_id=menu_id)
        if child_menus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="하위 메뉴가 존재하는 메뉴는 삭제할 수 없습니다"
            )
        
        menu_service.soft_delete(db=db, menu_id=menu_id, user_id=current_user.get('user_id', 'system'))
        
        return {"message": f"메뉴가 삭제되었습니다: {menu_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 메뉴 고급 기능 API ====================

@menu_router.post("/move", response_model=MenuInfoResponse, summary="메뉴 이동")
async def move_menu(
    move_request: MenuMoveRequest,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴를 다른 위치로 이동합니다.
    
    - **menu_id**: 이동할 메뉴 ID
    - **new_parent_id**: 새로운 상위 메뉴 ID (None이면 루트로 이동)
    - **new_order**: 새로운 정렬 순서
    """
    try:
        menu_service = MenuInfoService()
        menu = menu_service.get_by_menu_id(db=db, menu_id=move_request.target_menu_id)
        if not menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"메뉴를 찾을 수 없습니다: {move_request.target_menu_id}"
            )
        
        success = menu_service.move_menu(
            db=db,
            menu_no=move_request.target_menu_id,
            new_parent_id=move_request.new_parent_id,
            new_order=move_request.new_order,
            user_id=current_user.get('user_id', 'system')
        )
        
        if success:
            # 이동된 메뉴 정보를 다시 조회하여 반환
            updated_menu = menu_service.get_by_menu_id(db=db, menu_id=move_request.target_menu_id)
            return updated_menu
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="메뉴 이동에 실패했습니다"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 이동 중 오류가 발생했습니다: {str(e)}"
        )


# 메뉴 순서 업데이트 엔드포인트는 /{menu_id} 앞으로 이동됨


@menu_router.post("/copy", response_model=MenuInfoResponse, summary="메뉴 복사")
async def copy_menu(
    copy_request: MenuCopyRequest,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴를 복사합니다.
    
    - **source_menu_id**: 원본 메뉴 ID
    - **new_menu_id**: 새로운 메뉴 ID
    - **new_menu_nm**: 새로운 메뉴명
    - **new_parent_id**: 새로운 상위 메뉴 ID
    - **copy_children**: 하위 메뉴도 함께 복사할지 여부
    """
    try:
        menu_service = MenuInfoService()
        source_menu = menu_service.get_by_menu_id(db=db, menu_id=copy_request.source_menu_id)
        if not source_menu:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"원본 메뉴를 찾을 수 없습니다: {copy_request.source_menu_id}"
            )
        
        # 중복 확인
        existing_menu = menu_service.get_by_menu_id(db=db, menu_id=copy_request.new_menu_id)
        if existing_menu:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 메뉴 ID입니다: {copy_request.new_menu_id}"
            )
        
        copied_menu = menu_service.copy_menu(
            db=db,
            source_menu_id=copy_request.source_menu_id,
            new_menu_id=copy_request.new_menu_id,
            new_menu_nm=copy_request.new_menu_nm,
            new_parent_id=copy_request.new_parent_id,
            copy_children=copy_request.copy_children
        )
        
        return copied_menu
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 복사 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.post("/validate", response_model=MenuValidationResponse, summary="메뉴 검증")
async def validate_menu(
    menu_data: MenuInfoCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 데이터를 검증합니다.
    
    - **menu_data**: 검증할 메뉴 데이터
    """
    try:
        menu_service = MenuInfoService()
        validation_result = menu_service.validate_menu_data(db=db, menu_data=menu_data)
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 검증 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.get("/export/json", response_model=MenuExportResponse, summary="메뉴 데이터 내보내기")
async def export_menu_data(
    format: str = Query("json", description="내보내기 형식 (json, csv)"),
    include_inactive: bool = Query(False, description="비활성 메뉴 포함 여부"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 데이터를 내보냅니다.
    
    - **format**: 내보내기 형식 (json, csv)
    - **include_inactive**: 비활성 메뉴 포함 여부
    """
    try:
        menu_service = MenuInfoService()
        export_data = menu_service.export_menu_data(
            db=db,
            format=format,
            include_inactive=include_inactive
        )
        
        return export_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 데이터 내보내기 중 오류가 발생했습니다: {str(e)}"
        )


@menu_router.post("/import", summary="메뉴 데이터 가져오기")
async def import_menu_data(
    import_request: MenuImportRequest,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    메뉴 데이터를 가져옵니다.
    
    - **data**: 가져올 메뉴 데이터
    - **format**: 데이터 형식 (json, csv)
    - **overwrite**: 기존 데이터 덮어쓰기 여부
    """
    try:
        menu_service = MenuInfoService()
        result = menu_service.import_menu_data(
            db=db,
            data=import_request.data,
            format=import_request.format,
            overwrite=import_request.overwrite
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"메뉴 데이터 가져오기 중 오류가 발생했습니다: {str(e)}"
        )
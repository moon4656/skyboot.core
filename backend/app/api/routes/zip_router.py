"""우편번호 관련 API 라우터

우편번호 정보 관련 CRUD API 엔드포인트를 제공합니다.
"""

from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schemas import (
    # Zip 스키마
    ZipCreate, ZipUpdate, ZipResponse, ZipPagination
)
from app.services.user_service import ZipService
from app.utils.auth import get_current_user_from_bearer

router = APIRouter(prefix="/zip-codes", tags=["우편번호 관리"])


@router.post("/", response_model=ZipResponse, summary="우편번호 생성")
async def create_zip_code(
    zip_data: ZipCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db),
    current_user_id: Optional[str] = None
):
    """
    새로운 우편번호를 생성합니다.
    
    - **sn**: 일련번호 (필수, 고유값)
    - **zip**: 우편번호 (선택)
    - **ctprvn_nm**: 시도명 (선택)
    - **signgu_nm**: 시군구명 (선택)
    - **emd_nm**: 읍면동명 (선택)
    - **li_buld_nm**: 리건물명 (선택)
    - **lnbr_dong_ho**: 지번동호 (선택)
    """
    service = ZipService()
    return service.create(db, zip_data, current_user_id)


@router.get("/", response_model=ZipPagination, summary="우편번호 목록 조회")
async def get_zip_codes(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    우편번호 목록을 페이지네이션으로 조회합니다.
    """
    service = ZipService()
    zip_codes, total = service.get_multi(db, skip=skip, limit=limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return ZipPagination(
        items=zip_codes,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/search", response_model=ZipPagination, summary="주소로 우편번호 검색")
async def search_zip_codes_by_address(
    address: str = Query(..., description="검색할 주소"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    주소로 우편번호를 검색합니다.
    
    - **address**: 검색할 주소 (시도명, 시군구명, 읍면동명, 리건물명에서 검색)
    """
    service = ZipService()
    zip_codes, total = service.search_by_address(db, address, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return ZipPagination(
        items=zip_codes,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{zip_code}/addresses", response_model=List[ZipResponse], summary="우편번호로 주소 검색")
async def search_addresses_by_zip_code(
    zip_code: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    우편번호로 주소를 검색합니다.
    
    - **zip_code**: 우편번호
    """
    service = ZipService()
    return service.search_by_zip_code(db, zip_code)


@router.get("/provinces", response_model=List[str], summary="시도 목록 조회")
async def get_provinces(
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    전체 시도 목록을 조회합니다.
    """
    service = ZipService()
    return service.get_provinces(db)


@router.get("/provinces/{province}/cities", response_model=List[str], summary="시도별 시군구 목록 조회")
async def get_cities_by_province(
    province: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 시도의 시군구 목록을 조회합니다.
    
    - **province**: 시도명
    """
    service = ZipService()
    return service.get_cities_by_province(db, province)


@router.get("/provinces/{province}/cities/{city}/districts", response_model=List[str], summary="시군구별 읍면동 목록 조회")
async def get_districts_by_city(
    province: str,
    city: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 시군구의 읍면동 목록을 조회합니다.
    
    - **province**: 시도명
    - **city**: 시군구명
    """
    service = ZipService()
    return service.get_districts_by_city(db, province, city)


@router.get("/{sn}", response_model=ZipResponse, summary="우편번호 상세 조회")
async def get_zip_code(
    sn: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 우편번호의 상세 정보를 조회합니다.
    
    - **sn**: 일련번호
    """
    service = ZipService()
    zip_code = service.get(db, sn)
    if not zip_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="우편번호를 찾을 수 없습니다."
        )
    return zip_code


@router.put("/{sn}", response_model=ZipResponse, summary="우편번호 정보 수정")
async def update_zip_code(
    sn: Decimal,
    zip_data: ZipUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db),
    current_user_id: Optional[str] = None
):
    """
    우편번호 정보를 수정합니다.
    
    - **sn**: 일련번호
    - **zip_data**: 수정할 우편번호 정보
    """
    service = ZipService()
    zip_code = service.get(db, sn)
    if not zip_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="우편번호를 찾을 수 없습니다."
        )
    return service.update(db, zip_code, zip_data, current_user_id)


@router.delete("/{sn}", summary="우편번호 삭제")
async def delete_zip_code(
    sn: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    우편번호를 삭제합니다.
    
    - **sn**: 일련번호
    """
    service = ZipService()
    zip_code = service.get(db, sn)
    if not zip_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="우편번호를 찾을 수 없습니다."
        )
    service.remove(db, sn)
    return {"message": "우편번호가 성공적으로 삭제되었습니다."}
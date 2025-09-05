"""프로그램 관리 API 라우터

프로그램 목록 관련 CRUD API 엔드포인트를 제공합니다.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.system_models import ProgrmList
from app.schemas.system_schemas import (
    ProgrmListCreate, ProgrmListUpdate, ProgrmListResponse, ProgrmListPagination,
    ProgrmSearchParams
)
from app.services.system_service import ProgrmListService
from app.utils.auth import get_current_user_from_bearer

router = APIRouter(prefix="/programs", tags=["프로그램 관리"])


# ==================== ProgrmList 엔드포인트 ====================

@router.post("/", response_model=ProgrmListResponse, summary="프로그램 생성")
async def create_program(
    program_data: ProgrmListCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    새로운 프로그램을 생성합니다.
    
    - **progrm_file_nm**: 프로그램파일명 (필수, 고유값)
    - **progrm_stre_path**: 프로그램저장경로 (선택)
    - **progrm_korean_nm**: 프로그램한글명 (선택)
    - **progrm_dc**: 프로그램설명 (선택)
    - **url**: URL (선택)
    """
    service = ProgrmListService()
    return service.create(db, program_data, current_user.get('user_id'))


@router.get("/", response_model=ProgrmListPagination, summary="프로그램 목록 조회")
async def get_programs(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    프로그램 목록을 페이지네이션으로 조회합니다.
    """
    service = ProgrmListService()
    programs, total = service.get_multi(db, skip=skip, limit=limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return ProgrmListPagination(
        items=programs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/search", response_model=ProgrmListPagination, summary="프로그램 검색")
async def search_programs(
    progrm_korean_nm: Optional[str] = Query(None, description="프로그램한글명"),
    progrm_file_nm: Optional[str] = Query(None, description="프로그램파일명"),
    progrm_stre_path: Optional[str] = Query(None, description="프로그램저장경로"),
    url: Optional[str] = Query(None, description="URL"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    다양한 조건으로 프로그램을 검색합니다.
    
    - **progrm_korean_nm**: 프로그램한글명 (부분 일치)
    - **progrm_file_nm**: 프로그램파일명 (부분 일치)
    - **progrm_stre_path**: 프로그램저장경로 (부분 일치)
    - **url**: URL (부분 일치)
    """
    search_params = ProgrmSearchParams(
        progrm_korean_nm=progrm_korean_nm,
        progrm_file_nm=progrm_file_nm,
        progrm_stre_path=progrm_stre_path,
        url=url
    )
    
    service = ProgrmListService()
    programs, total = service.search_programs(db, search_params, skip, limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return ProgrmListPagination(
        items=programs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/{progrm_file_nm}", response_model=ProgrmListResponse, summary="프로그램 상세 조회")
async def get_program(
    progrm_file_nm: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 프로그램의 상세 정보를 조회합니다.
    
    - **progrm_file_nm**: 프로그램파일명
    """
    service = ProgrmListService()
    program = service.get_by_file_name(db, progrm_file_nm)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로그램을 찾을 수 없습니다."
        )
    return program


@router.put("/{progrm_file_nm}", response_model=ProgrmListResponse, summary="프로그램 정보 수정")
async def update_program(
    progrm_file_nm: str,
    program_data: ProgrmListUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    프로그램 정보를 수정합니다.
    
    - **progrm_file_nm**: 프로그램파일명
    - **program_data**: 수정할 프로그램 정보
    """
    service = ProgrmListService()
    program = service.get_by_file_name(db, progrm_file_nm)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로그램을 찾을 수 없습니다."
        )
    return service.update(db, program, program_data, last_updt_user_id=current_user.get('user_id'))


@router.delete("/{progrm_file_nm}", summary="프로그램 삭제")
async def delete_program(
    progrm_file_nm: str,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    프로그램을 삭제합니다.
    
    - **progrm_file_nm**: 프로그램파일명
    """
    service = ProgrmListService()
    program = service.get_by_file_name(db, progrm_file_nm)
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로그램을 찾을 수 없습니다."
        )
    service.remove(db, progrm_file_nm)
    return {"message": "프로그램이 성공적으로 삭제되었습니다."}
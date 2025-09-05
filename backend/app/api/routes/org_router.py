"""조직 관련 API 라우터

조직 정보 관련 CRUD API 엔드포인트를 제공합니다.
"""

from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user_schemas import (
    # Org 스키마
    OrgCreate, OrgUpdate, OrgResponse, OrgPagination,
    # 검색 및 통계 스키마
    OrgTreeNode
)
from app.services.user_service import OrgService
from app.utils.auth import get_current_user_from_bearer

router = APIRouter(prefix="/organizations", tags=["조직 관리"])


@router.post("/", response_model=OrgResponse, summary="조직 생성")
async def create_organization(
    org_data: OrgCreate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db),
    current_user_id: Optional[str] = None
):
    """
    새로운 조직을 생성합니다.
    
    - **org_no**: 조직번호 (필수, 고유값)
    - **org_nm**: 조직명 (선택)
    - **parent_org_no**: 상급부서번호 (선택)
    - **org_ordr**: 조직순번 (선택)
    """
    service = OrgService()
    return service.create(db, org_data, current_user_id)


@router.get("/", response_model=OrgPagination, summary="조직 목록 조회")
async def get_organizations(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 개수"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    조직 목록을 페이지네이션으로 조회합니다.
    """
    service = OrgService()
    orgs, total = service.get_multi(db, skip=skip, limit=limit)
    
    pages = (total + limit - 1) // limit
    page = (skip // limit) + 1
    
    return OrgPagination(
        items=orgs,
        total=total,
        page=page,
        size=limit,
        pages=pages
    )


@router.get("/tree", response_model=List[OrgTreeNode], summary="조직 트리 구조 조회")
async def get_organization_tree(
    parent_org_no: Optional[Decimal] = Query(None, description="상위 조직번호"),
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    조직의 트리 구조를 조회합니다.
    
    - **parent_org_no**: 상위 조직번호 (없으면 최상위 조직부터)
    """
    service = OrgService()
    return service.get_organization_tree(db, parent_org_no)


@router.get("/{org_no}", response_model=OrgResponse, summary="조직 상세 조회")
async def get_organization(
    org_no: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 조직의 상세 정보를 조회합니다.
    
    - **org_no**: 조직번호
    """
    service = OrgService()
    org = service.get(db, org_no)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="조직을 찾을 수 없습니다."
        )
    return org


@router.put("/{org_no}", response_model=OrgResponse, summary="조직 정보 수정")
async def update_organization(
    org_no: Decimal,
    org_data: OrgUpdate,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db),
    current_user_id: Optional[str] = None
):
    """
    조직 정보를 수정합니다.
    
    - **org_no**: 조직번호
    - **org_data**: 수정할 조직 정보
    """
    service = OrgService()
    org = service.update(db, org_no, org_data, current_user.get("user_id"))
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="조직을 찾을 수 없습니다."
        )
    return org


@router.delete("/{org_no}", summary="조직 삭제")
async def delete_organization(
    org_no: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    조직을 삭제합니다.
    
    - **org_no**: 조직번호
    """
    service = OrgService()
    org = service.get(db, org_no)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="조직을 찾을 수 없습니다."
        )
    service.remove(db, org_no)
    return {"message": "조직이 성공적으로 삭제되었습니다."}


@router.get("/{org_no}/children", response_model=List[OrgResponse], summary="하위 조직 조회")
async def get_child_organizations(
    org_no: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 조직의 하위 조직 목록을 조회합니다.
    
    - **org_no**: 상위 조직번호
    """
    service = OrgService()
    return service.get_child_organizations(db, org_no)


@router.get("/{org_no}/path", response_model=List[OrgResponse], summary="조직 경로 조회")
async def get_organization_path(
    org_no: Decimal,
    current_user: dict = Depends(get_current_user_from_bearer),
    db: Session = Depends(get_db)
):
    """
    특정 조직의 경로(루트부터 현재 조직까지)를 조회합니다.
    
    - **org_no**: 조직번호
    """
    service = OrgService()
    return service.get_organization_path(db, org_no)
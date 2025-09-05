"""공통 코드 관리 API 라우터

공통 그룹 코드와 공통 코드 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.dependencies import get_current_user
from app.services import CmmnGrpCodeService, CmmnCodeService
from app.schemas.common_schemas import (
    CmmnGrpCodeResponse, CmmnGrpCodeCreate, CmmnGrpCodeUpdate,
    CmmnCodeResponse, CmmnCodeCreate, CmmnCodeUpdate,
    CmmnGrpCodePagination, CmmnCodePagination,
    CmmnGrpCodeWithCodes, CmmnCodeSearchParams,
    CmmnGrpCodeStatistics, CmmnCodeStatistics
)

# 공통 그룹 코드 라우터
grp_code_router = APIRouter(
    prefix="/group-codes",
    tags=["공통 그룹 코드 관리"],
    responses={404: {"description": "Not found"}}
)

# 공통 코드 라우터
code_router = APIRouter(
    prefix="/codes",
    tags=["공통 코드 관리"],
    responses={404: {"description": "Not found"}}
)

# 서비스 인스턴스는 각 함수 내에서 초기화됩니다


# ==================== 공통 그룹 코드 API ====================

@grp_code_router.get("/", response_model=CmmnGrpCodePagination, summary="공통 그룹 코드 목록 조회")
async def get_group_codes(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    search: Optional[str] = Query(None, description="검색어 (그룹코드명, 그룹코드설명)"),
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    공통 그룹 코드 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **search**: 검색어 (그룹코드명, 그룹코드설명에서 검색)
    - **use_at**: 사용 여부로 필터링
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        group_codes = grp_code_service.search_group_codes(
            db=db,
            search_term=search,
            use_at=use_at,
            skip=skip,
            limit=limit
        )
        
        total_count = grp_code_service.count(db=db)
        
        return CmmnGrpCodePagination(
            items=group_codes,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 그룹 코드 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.get("/active", response_model=List[CmmnGrpCodeResponse], summary="활성 그룹 코드 목록 조회")
async def get_active_group_codes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    활성화된 공통 그룹 코드 목록을 조회합니다.
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        active_codes = grp_code_service.get_active_group_codes(db=db)
        return active_codes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 그룹 코드 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.get("/statistics", response_model=CmmnGrpCodeStatistics, summary="그룹 코드 통계 조회")
async def get_group_code_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    공통 그룹 코드 통계 정보를 조회합니다.
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        statistics = grp_code_service.get_group_code_statistics(db=db)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.get("/{group_code_id}", response_model=CmmnGrpCodeWithCodes, summary="그룹 코드 상세 조회")
async def get_group_code(
    group_code_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 공통 그룹 코드의 상세 정보를 조회합니다 (하위 코드 포함).
    
    - **group_code_id**: 그룹 코드 ID
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        group_code = grp_code_service.get_by_group_code_id(db=db, group_code_id=group_code_id)
        
        if not group_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"그룹 코드를 찾을 수 없습니다: {group_code_id}"
            )
        
        # 하위 코드 조회
        code_service = CmmnCodeService()
        sub_codes = code_service.get_codes_by_group(db=db, group_code_id=group_code_id)
        
        return CmmnGrpCodeWithCodes(
            **group_code.__dict__,
            codes=sub_codes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드 조회 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.post("/", response_model=CmmnGrpCodeResponse, summary="그룹 코드 생성")
async def create_group_code(
    group_code_data: CmmnGrpCodeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 공통 그룹 코드를 생성합니다.
    
    - **group_code_id**: 그룹 코드 ID (고유값)
    - **group_code_nm**: 그룹 코드명
    - **group_code_dc**: 그룹 코드 설명
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        # 중복 확인
        existing_code = grp_code_service.get_by_group_code_id(
            db=db, 
            group_code_id=group_code_data.group_code_id
        )
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 그룹 코드 ID입니다: {group_code_data.group_code_id}"
            )
        
        group_code = grp_code_service.create(db=db, obj_in=group_code_data)
        return group_code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.post("/{group_code_id}/with-codes", response_model=CmmnGrpCodeWithCodes, summary="그룹 코드와 하위 코드 일괄 생성")
async def create_group_code_with_codes(
    group_code_id: str,
    group_code_data: CmmnGrpCodeCreate,
    codes_data: List[CmmnCodeCreate],
    db: Session = Depends(get_db)
):
    """
    공통 그룹 코드와 하위 코드를 일괄 생성합니다.
    
    - **group_code_id**: 그룹 코드 ID
    - **group_code_data**: 그룹 코드 정보
    - **codes_data**: 하위 코드 목록
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        # 중복 확인
        existing_code = grp_code_service.get_by_group_code_id(db=db, group_code_id=group_code_id)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 그룹 코드 ID입니다: {group_code_id}"
            )
        
        group_code_with_codes = grp_code_service.create_with_codes(
            db=db,
            group_code_data=group_code_data,
            codes_data=codes_data
        )
        
        return group_code_with_codes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드와 하위 코드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.put("/{group_code_id}", response_model=CmmnGrpCodeResponse, summary="그룹 코드 수정")
async def update_group_code(
    group_code_id: str,
    group_code_data: CmmnGrpCodeUpdate,
    db: Session = Depends(get_db)
):
    """
    공통 그룹 코드 정보를 수정합니다.
    
    - **group_code_id**: 수정할 그룹 코드 ID
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        group_code = grp_code_service.get_by_group_code_id(db=db, group_code_id=group_code_id)
        if not group_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"그룹 코드를 찾을 수 없습니다: {group_code_id}"
            )
        
        updated_group_code = grp_code_service.update(
            db=db,
            db_obj=group_code,
            obj_in=group_code_data
        )
        
        return updated_group_code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드 수정 중 오류가 발생했습니다: {str(e)}"
        )


@grp_code_router.delete("/{group_code_id}", summary="그룹 코드 삭제")
async def delete_group_code(
    group_code_id: str,
    db: Session = Depends(get_db)
):
    """
    공통 그룹 코드를 삭제합니다 (소프트 삭제).
    
    - **group_code_id**: 삭제할 그룹 코드 ID
    """
    try:
        grp_code_service = CmmnGrpCodeService()
        group_code = grp_code_service.get_by_group_code_id(db=db, group_code_id=group_code_id)
        if not group_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"그룹 코드를 찾을 수 없습니다: {group_code_id}"
            )
        
        grp_code_service.soft_delete(db=db, db_obj=group_code)
        
        return {"message": f"그룹 코드가 삭제되었습니다: {group_code_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹 코드 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 공통 코드 API ====================

@code_router.get("/", response_model=CmmnCodePagination, summary="공통 코드 목록 조회")
async def get_codes(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    group_code_id: Optional[str] = Query(None, description="그룹 코드 ID"),
    search: Optional[str] = Query(None, description="검색어 (코드명, 코드설명)"),
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    db: Session = Depends(get_db)
):
    """
    공통 코드 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **group_code_id**: 그룹 코드 ID로 필터링
    - **search**: 검색어 (코드명, 코드설명에서 검색)
    - **use_at**: 사용 여부로 필터링
    """
    try:
        code_service = CmmnCodeService()
        if group_code_id:
            codes = code_service.get_codes_by_group(
                db=db,
                group_code_id=group_code_id,
                skip=skip,
                limit=limit
            )
        else:
            search_params = CmmnCodeSearchParams(
                search_term=search,
                group_code_id=group_code_id,
                use_at=use_at
            )
            codes = code_service.search_codes(
                db=db,
                search_params=search_params,
                skip=skip,
                limit=limit
            )
        
        total_count = code_service.count(db=db)
        
        return CmmnCodePagination(
            items=codes,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.get("/group/{group_code_id}", response_model=List[CmmnCodeResponse], summary="그룹별 코드 조회")
async def get_codes_by_group(
    group_code_id: str,
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    db: Session = Depends(get_db)
):
    """
    특정 그룹의 공통 코드 목록을 조회합니다.
    
    - **group_code_id**: 그룹 코드 ID
    - **use_at**: 사용 여부로 필터링
    """
    try:
        code_service = CmmnCodeService()
        codes = code_service.get_codes_by_group(
            db=db,
            group_code_id=group_code_id,
            use_at=use_at
        )
        
        return codes
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"그룹별 코드 조회 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.get("/statistics", response_model=CmmnCodeStatistics, summary="공통 코드 통계 조회")
async def get_code_statistics(
    db: Session = Depends(get_db)
):
    """
    공통 코드 통계 정보를 조회합니다.
    """
    try:
        code_service = CmmnCodeService()
        statistics = code_service.get_code_statistics(db=db)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.get("/{code_id}", response_model=CmmnCodeResponse, summary="공통 코드 상세 조회")
async def get_code(
    code_id: str,
    db: Session = Depends(get_db)
):
    """
    특정 공통 코드의 상세 정보를 조회합니다.
    
    - **code_id**: 코드 ID
    """
    try:
        code_service = CmmnCodeService()
        code = code_service.get_by_code_id(db=db, code_id=code_id)
        
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공통 코드를 찾을 수 없습니다: {code_id}"
            )
        
        return code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 조회 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.post("/", response_model=CmmnCodeResponse, summary="공통 코드 생성")
async def create_code(
    code_data: CmmnCodeCreate,
    db: Session = Depends(get_db)
):
    """
    새로운 공통 코드를 생성합니다.
    
    - **group_code_id**: 그룹 코드 ID
    - **code_id**: 코드 ID (고유값)
    - **code_nm**: 코드명
    - **code_dc**: 코드 설명
    """
    try:
        # 그룹 코드 존재 확인
        grp_code_service = CmmnGrpCodeService()
        group_code = grp_code_service.get_by_group_code_id(
            db=db, 
            group_code_id=code_data.group_code_id
        )
        if not group_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"그룹 코드를 찾을 수 없습니다: {code_data.group_code_id}"
            )
        
        # 중복 확인
        code_service = CmmnCodeService()
        existing_code = code_service.get_by_code_id(db=db, code_id=code_data.code_id)
        if existing_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 코드 ID입니다: {code_data.code_id}"
            )
        
        code = code_service.create(db=db, obj_in=code_data)
        return code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.put("/{code_id}", response_model=CmmnCodeResponse, summary="공통 코드 수정")
async def update_code(
    code_id: str,
    code_data: CmmnCodeUpdate,
    db: Session = Depends(get_db)
):
    """
    공통 코드 정보를 수정합니다.
    
    - **code_id**: 수정할 코드 ID
    """
    try:
        code_service = CmmnCodeService()
        code = code_service.get_by_code_id(db=db, code_id=code_id)
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공통 코드를 찾을 수 없습니다: {code_id}"
            )
        
        updated_code = code_service.update(
            db=db,
            db_obj=code,
            obj_in=code_data
        )
        
        return updated_code
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 수정 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.delete("/{code_id}", summary="공통 코드 삭제")
async def delete_code(
    code_id: str,
    db: Session = Depends(get_db)
):
    """
    공통 코드를 삭제합니다 (소프트 삭제).
    
    - **code_id**: 삭제할 코드 ID
    """
    try:
        code_service = CmmnCodeService()
        code = code_service.get_by_code_id(db=db, code_id=code_id)
        if not code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"공통 코드를 찾을 수 없습니다: {code_id}"
            )
        
        code_service.soft_delete(db=db, db_obj=code)
        
        return {"message": f"공통 코드가 삭제되었습니다: {code_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"공통 코드 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.post("/copy", response_model=List[CmmnCodeResponse], summary="코드 복사")
async def copy_codes(
    source_group_id: str = Query(..., description="원본 그룹 코드 ID"),
    target_group_id: str = Query(..., description="대상 그룹 코드 ID"),
    db: Session = Depends(get_db)
):
    """
    한 그룹의 코드를 다른 그룹으로 복사합니다.
    
    - **source_group_id**: 원본 그룹 코드 ID
    - **target_group_id**: 대상 그룹 코드 ID
    """
    try:
        # 그룹 코드 존재 확인
        grp_code_service = CmmnGrpCodeService()
        source_group = grp_code_service.get_by_group_code_id(db=db, group_code_id=source_group_id)
        if not source_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"원본 그룹 코드를 찾을 수 없습니다: {source_group_id}"
            )
        
        target_group = grp_code_service.get_by_group_code_id(db=db, group_code_id=target_group_id)
        if not target_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"대상 그룹 코드를 찾을 수 없습니다: {target_group_id}"
            )
        
        code_service = CmmnCodeService()
        copied_codes = code_service.copy_codes_between_groups(
            db=db,
            source_group_id=source_group_id,
            target_group_id=target_group_id
        )
        
        return copied_codes
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"코드 복사 중 오류가 발생했습니다: {str(e)}"
        )


@code_router.put("/sort-order", summary="코드 정렬 순서 업데이트")
async def update_sort_order(
    sort_updates: List[dict],  # [{"code_id": "CODE01", "sort_ordr": 1}, ...]
    db: Session = Depends(get_db)
):
    """
    공통 코드의 정렬 순서를 일괄 업데이트합니다.
    
    - **sort_updates**: 정렬 순서 업데이트 목록
    """
    try:
        code_service = CmmnCodeService()
        code_service.update_sort_order(db=db, sort_updates=sort_updates)
        
        return {"message": "정렬 순서가 업데이트되었습니다"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정렬 순서 업데이트 중 오류가 발생했습니다: {str(e)}"
        )
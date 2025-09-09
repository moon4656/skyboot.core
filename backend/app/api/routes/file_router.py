"""파일 관리 API 라우터

파일 그룹과 파일 상세 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import logging
from datetime import datetime
from pathlib import Path

from app.database import get_db
from app.services import FileService, FileDetailService
from app.utils.dependencies import get_current_user
from app.schemas.file_schemas import (
    FileResponse as FileResponseSchema, FileCreate, FileUpdate, FileGroupCreate,
    FileDetailResponse, FileDetailCreate, FileDetailUpdate,
    FilePagination, FileDetailPagination,
    FileWithDetails, FileUploadResponse, FileUploadProcessResponse, FileDownloadResponse,
    FileSearchParams, FileStatistics, FileValidationResponse
)

# 파일 그룹 라우터
file_router = APIRouter(
    prefix="/files",
    tags=["파일 그룹 관리"],
    responses={404: {"description": "Not found"}}
)

# 파일 상세 라우터
file_detail_router = APIRouter(
    prefix="/file-details",
    tags=["파일 상세 관리"],
    responses={404: {"description": "Not found"}}
)

# 서비스 인스턴스
file_service = FileService()
file_detail_service = FileDetailService()

# 로거 설정
logger = logging.getLogger(__name__)

# 파일 업로드 설정
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt"}


# ==================== 파일 그룹 API ====================

@file_router.get("/", response_model=FilePagination, summary="파일 그룹 목록 조회")
async def get_file_groups(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    search: Optional[str] = Query(None, description="검색어"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 그룹 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **search**: 검색어
    """
    try:
        file_groups = file_service.search_file_groups(
            db=db,
            search_term=search,
            skip=skip,
            limit=limit
        )
        
        total_count = file_service.count(db=db)
        
        return FilePagination(
            items=file_groups,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 그룹 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@file_router.get("/statistics", response_model=FileStatistics, summary="파일 통계 조회")
async def get_file_statistics(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 통계 정보를 조회합니다.
    """
    try:
        statistics = file_service.get_file_statistics(db=db)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@file_router.get("/{atch_file_id}", response_model=FileWithDetails, summary="파일 그룹 상세 조회")
async def get_file_group(
    atch_file_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 파일 그룹의 상세 정보를 조회합니다 (파일 목록 포함).
    
    - **atch_file_id**: 첨부파일 ID
    """
    try:
        file_group = file_service.get_by_atch_file_id(db=db, atch_file_id=atch_file_id)
        
        if not file_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"파일 그룹을 찾을 수 없습니다: {atch_file_id}"
            )
        
        # 파일 목록 조회
        file_details = file_detail_service.get_files_by_group(db=db, atch_file_id=atch_file_id)
        
        return FileWithDetails(
            **file_group.__dict__,
            file_details=file_details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 그룹 조회 중 오류가 발생했습니다: {str(e)}"
        )


@file_router.post("/", response_model=FileResponseSchema, summary="파일 그룹 생성")
async def create_file_group(
    file_data: FileGroupCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 파일 그룹을 생성합니다.
    
    - **use_at**: 사용 여부 (Y/N)
    """
    try:
        # 파일 그룹 생성 (서비스에서 자동으로 UUID 생성)
        file_group = file_service.create_file_group(
            db=db, 
            file_group_data=file_data.model_dump(),
            user_id=current_user.get('user_id', 'system')
        )
        return file_group
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 그룹 생성 중 오류가 발생했습니다: {str(e)}"
        )


# @file_router.put("/{atch_file_id}", response_model=FileResponseSchema, summary="파일 그룹 수정")
# async def update_file_group(
#     atch_file_id: str,
#     file_data: FileUpdate,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     파일 그룹 정보를 수정합니다.
    
#     - **atch_file_id**: 수정할 첨부파일 ID
#     """
#     try:
#         file_group = file_service.get_by_atch_file_id(db=db, atch_file_id=atch_file_id)
#         if not file_group:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"파일 그룹을 찾을 수 없습니다: {atch_file_id}"
#             )
        
#         updated_file_group = file_service.update(
#             db=db,
#             db_obj=file_group,
#             obj_in=file_data
#         )
        
#         return updated_file_group
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"파일 그룹 수정 중 오류가 발생했습니다: {str(e)}"
#         )


@file_router.delete("/{atch_file_id}", summary="파일 그룹 삭제")
async def delete_file_group(
    atch_file_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 그룹을 삭제합니다 (소프트 삭제).
    
    - **atch_file_id**: 삭제할 첨부파일 ID
    """
    try:
        file_group = file_service.get_by_atch_file_id(db=db, atch_file_id=atch_file_id)
        if not file_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"파일 그룹을 찾을 수 없습니다: {atch_file_id}"
            )
        
        # File 모델은 atch_file_id가 기본키이므로 직접 use 필드를 'N'으로 변경
        file_group.use = 'N'
        file_group.last_updusr_id = current_user.get('user_id', 'system')
        file_group.last_updt_pnttm = datetime.now()
        
        db.add(file_group)
        db.commit()
        db.refresh(file_group)
        
        return {"message": f"파일 그룹이 삭제되었습니다: {atch_file_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 그룹 삭제 중 오류가 발생했습니다: {str(e)}"
        )

@file_router.post("/upload-process", response_model=FileUploadProcessResponse, summary="파일 업로드 프로세스 통합")
async def upload_file_process(
    files: List[UploadFile] = File(..., description="업로드할 파일 목록"),
    use_at: str = Form("Y", description="사용여부"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 업로드 프로세스를 통합하여 처리합니다.
    
    프로세스:
    1. 파일 그룹 생성 (atch_file_id 자동 생성)
    2. 파일 업로드 및 저장
    3. 파일 속성 생성
    4. 파일 상세정보 생성
    
    - **files**: 업로드할 파일 목록
    - **use_at**: 사용여부 (Y/N)
    """
    try:
        # 1. 파일 그룹 생성
        file_group_data = {"use_at": use_at}
        file_group = file_service.create_file_group(
            db=db,
            file_group_data=file_group_data,
            user_id=current_user['user_id']
        )
        
        atch_file_id = file_group.atch_file_id
        uploaded_files = []
        failed_files = []
        total_size = 0
        
        # 2-4. 각 파일에 대해 업로드 및 상세정보 생성
        for file in files:
            try:
                # 파일 업로드 및 상세정보 생성
                file_detail = file_detail_service.upload_file(
                    db=db,
                    atch_file_id=atch_file_id,
                    file_data=file.file,
                    original_filename=file.filename,
                    user_id='system'
                )
                uploaded_files.append(file_detail)
                total_size += file_detail.file_size or 0
                
            except Exception as e:
                logger.error(f"❌ 파일 업로드 실패 - 파일명: {file.filename}, 오류: {str(e)}")
                failed_files.append({
                    "filename": file.filename,
                    "error": str(e)
                })
        
        # API 사용 로그
        logger.info(f"✅ 파일 업로드 프로세스 완료 - 첨부파일ID: {atch_file_id}, 성공: {len(uploaded_files)}개, 실패: {len(failed_files)}개")
        
        return FileUploadProcessResponse(
            atch_file_id=atch_file_id,
            uploaded_files=uploaded_files,
            success_count=len(uploaded_files),
            failed_count=len(failed_files),
            total_size=total_size
        )
        
    except Exception as e:
        logger.error(f"❌ 파일 업로드 프로세스 실패 - 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 프로세스 중 오류가 발생했습니다: {str(e)}"
        )

# ==================== 파일 상세 API ====================

@file_detail_router.get("/details", response_model=FileDetailPagination, summary="파일 목록 조회")
async def get_file_details(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    atch_file_id: Optional[str] = Query(None, description="첨부파일 ID"),
    search: Optional[str] = Query(None, description="검색어 (파일명)"),
    file_extsn: Optional[str] = Query(None, description="파일 확장자"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 상세 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **atch_file_id**: 첨부파일 ID로 필터링
    - **search**: 검색어 (파일명에서 검색)
    - **file_extsn**: 파일 확장자로 필터링
    """
    try:
        if atch_file_id:
            file_details = file_detail_service.get_files_by_group(
                db=db,
                atch_file_id=atch_file_id
            )
        else:
            search_params = FileSearchParams(
                search_term=search,
                file_extsn=file_extsn,
                atch_file_id=atch_file_id
            )
            file_details = file_detail_service.search_files(
                db=db,
                search_params=search_params,
                skip=skip,
                limit=limit
            )
        
        total_count = file_detail_service.count(db=db)
        
        return FileDetailPagination(
            items=file_details,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@file_detail_router.get("/statistics", response_model=dict, summary="파일 유형별 통계 조회")
async def get_file_statistics_by_type(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일 유형별 통계 정보를 조회합니다.
    """
    try:
        statistics = file_detail_service.get_file_statistics_by_type(db=db)
        return statistics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 유형별 통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


# @file_detail_router.get("/{file_sn}", response_model=FileDetailResponse, summary="파일 상세 조회")
# async def get_file_detail(
#     file_sn: int,
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     특정 파일의 상세 정보를 조회합니다.
    
#     - **file_sn**: 파일 일련번호
#     """
#     try:
#         file_detail = file_detail_service.get_by_file_sn(db=db, file_sn=file_sn)
        
#         if not file_detail:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"파일을 찾을 수 없습니다: {file_sn}"
#             )
        
#         return file_detail
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"파일 조회 중 오류가 발생했습니다: {str(e)}"
#         )


@file_detail_router.post("/upload", response_model=FileUploadResponse, summary="파일 업로드")
async def upload_file(
    atch_file_id: str = Query(..., description="첨부파일 ID"),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일을 업로드합니다.
    
    - **atch_file_id**: 첨부파일 ID
    - **file**: 업로드할 파일
    """
    try:
        # 파일 그룹 존재 확인
        file_group = file_service.get_by_atch_file_id(db=db, atch_file_id=atch_file_id)
        if not file_group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"파일 그룹을 찾을 수 없습니다: {atch_file_id}"
            )
        
        # 파일 검증
        validation_result = file_detail_service.validate_file(
            filename=file.filename,
            file_size=file.size if hasattr(file, 'size') else 0
        )
        
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일 검증 실패: {validation_result.error_message}"
            )
        
        # 파일 업로드
        uploaded_file = file_detail_service.upload_file(
            db=db,
            atch_file_id=atch_file_id,
            file_data=file.file,
            original_filename=file.filename,
            user_id=current_user.get('user_id', 'system')
        )
        
        return FileUploadResponse(
            success=True,
            file_id=str(uploaded_file.file_sn),
            file_name=uploaded_file.orignl_file_nm,
            file_size=int(uploaded_file.file_size) if uploaded_file.file_size else 0,
            upload_url=f"/api/v1/file-details/{uploaded_file.file_sn}/download",
            message="파일이 성공적으로 업로드되었습니다"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 업로드 중 오류가 발생했습니다: {str(e)}"
        )


@file_detail_router.get("/{file_sn}/download", response_class=FileResponse, summary="파일 다운로드")
async def download_file(
    file_sn: int,
    atch_file_id: str = Query(..., description="첨부파일 ID"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일을 다운로드합니다.
    
    - **file_sn**: 파일 일련번호
    """
    try:
        file_detail = file_detail_service.get_by_file_sn(db=db, atch_file_id=atch_file_id, file_sn=file_sn)
        
        if not file_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"파일을 찾을 수 없습니다: {file_sn}"
            )
        
        file_path = Path(file_detail.file_stre_cours)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="파일이 서버에 존재하지 않습니다"
            )
        
        # 다운로드 기록
        file_detail_service.record_download(db=db, file_sn=file_sn)
        
        return FileResponse(
            path=str(file_path),
            filename=file_detail.orignl_file_nm,
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 다운로드 중 오류가 발생했습니다: {str(e)}"
        )


# @file_detail_router.put("/{file_sn}", response_model=FileDetailResponse, summary="파일 정보 수정")
# async def update_file_detail(
#     file_sn: int,
#     file_data: FileDetailUpdate,
#     atch_file_id: str = Query(..., description="첨부파일 ID"),
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     파일 정보를 수정합니다.
    
#     - **file_sn**: 수정할 파일 일련번호
#     """
#     try:
#         file_detail = file_detail_service.get_by_file_sn(db=db, atch_file_id=atch_file_id, file_sn=file_sn)
#         if not file_detail:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail=f"파일을 찾을 수 없습니다: {file_sn}"
#             )
        
#         updated_file_detail = file_detail_service.update(
#             db=db,
#             db_obj=file_detail,
#             obj_in=file_data
#         )
        
#         return updated_file_detail
        
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"파일 정보 수정 중 오류가 발생했습니다: {str(e)}"
#         )


@file_detail_router.delete("/{file_sn}", summary="파일 삭제")
async def delete_file_detail(
    file_sn: int,
    atch_file_id: str = Query(..., description="첨부파일 ID"),
    delete_physical: bool = Query(False, description="물리적 파일도 삭제할지 여부"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일을 삭제합니다.
    
    - **file_sn**: 삭제할 파일 일련번호
    - **delete_physical**: 물리적 파일도 삭제할지 여부
    """
    try:
        file_detail = file_detail_service.get_by_file_sn(db=db, atch_file_id=atch_file_id, file_sn=file_sn)
        if not file_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"파일을 찾을 수 없습니다: {file_sn}"
            )
        
        file_detail_service.delete_file(
            db=db,
            atch_file_id=atch_file_id,
            file_sn=file_sn,
            delete_physical=delete_physical
        )
        
        return {"message": f"파일이 삭제되었습니다: {file_sn}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@file_detail_router.post("/validate", response_model=FileValidationResponse, summary="파일 검증")
async def validate_file(
    filename: str = Query(..., description="파일명"),
    file_size: int = Query(..., description="파일 크기 (바이트)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    파일을 검증합니다.
    
    - **filename**: 파일명
    - **file_size**: 파일 크기 (바이트)
    """
    try:
        validation_result = file_detail_service.validate_file(
            filename=filename,
            file_size=file_size
        )
        
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"파일 검증 중 오류가 발생했습니다: {str(e)}"
        )


@file_detail_router.post("/cleanup-orphaned", summary="고아 파일 정리")
async def cleanup_orphaned_files(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    데이터베이스에 기록되지 않은 고아 파일들을 정리합니다.
    """
    try:
        cleaned_count = file_detail_service.cleanup_orphaned_files(
            db=db
        )
        
        return {"message": f"{cleaned_count}개의 고아 파일이 정리되었습니다"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"고아 파일 정리 중 오류가 발생했습니다: {str(e)}"
        )
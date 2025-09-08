"""파일 관련 Pydantic 스키마

파일, 파일상세 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field


# File 스키마
class FileBase(BaseModel):
    """파일 기본 스키마"""
    file_stre_cours: Optional[str] = Field(None, max_length=2000, description="파일저장경로")
    stre_file_nm: Optional[str] = Field(None, max_length=255, description="저장파일명")
    orignl_file_nm: Optional[str] = Field(None, max_length=255, description="원본파일명")
    file_extsn: Optional[str] = Field(None, max_length=20, description="파일확장자")
    file_cn: Optional[str] = Field(None, description="파일내용")
    file_size: Optional[Decimal] = Field(None, description="파일크기")


class FileCreate(FileBase):
    """파일 생성 스키마"""
    atch_file_id: str = Field(..., max_length=36, description="첨부파일ID")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class FileGroupCreate(BaseModel):
    """파일 그룹 생성 스키마 (atch_file_id 자동 생성)"""
    use_at: Optional[str] = Field("Y", max_length=1, description="사용여부")


class FileUpdate(BaseModel):
    """파일 수정 스키마"""
    file_stre_cours: Optional[str] = Field(None, max_length=2000, description="파일저장경로")
    stre_file_nm: Optional[str] = Field(None, max_length=255, description="저장파일명")
    orignl_file_nm: Optional[str] = Field(None, max_length=255, description="원본파일명")
    file_extsn: Optional[str] = Field(None, max_length=20, description="파일확장자")
    file_cn: Optional[str] = Field(None, description="파일내용")
    file_size: Optional[Decimal] = Field(None, description="파일크기")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class FileResponse(FileBase):
    """파일 응답 스키마"""
    atch_file_id: str = Field(..., description="첨부파일ID")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# FileDetail 스키마
class FileDetailBase(BaseModel):
    """파일상세 기본 스키마"""
    file_stre_cours: Optional[str] = Field(None, max_length=2000, description="파일저장경로")
    stre_file_nm: Optional[str] = Field(None, max_length=255, description="저장파일명")
    orignl_file_nm: Optional[str] = Field(None, max_length=255, description="원본파일명")
    file_extsn: Optional[str] = Field(None, max_length=20, description="파일확장자")
    file_cn: Optional[str] = Field(None, description="파일내용")
    file_size: Optional[Decimal] = Field(None, description="파일크기")


class FileDetailCreate(FileDetailBase):
    """파일상세 생성 스키마"""
    atch_file_id: str = Field(..., max_length=36, description="첨부파일ID")
    file_sn: Decimal = Field(..., description="파일순번")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class FileDetailUpdate(BaseModel):
    """파일상세 수정 스키마"""
    file_stre_cours: Optional[str] = Field(None, max_length=2000, description="파일저장경로")
    stre_file_nm: Optional[str] = Field(None, max_length=255, description="저장파일명")
    orignl_file_nm: Optional[str] = Field(None, max_length=255, description="원본파일명")
    file_extsn: Optional[str] = Field(None, max_length=20, description="파일확장자")
    file_cn: Optional[str] = Field(None, description="파일내용")
    file_size: Optional[Decimal] = Field(None, description="파일크기")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class FileDetailResponse(FileDetailBase):
    """파일상세 응답 스키마"""
    atch_file_id: str = Field(..., description="첨부파일ID")
    file_sn: Decimal = Field(..., description="파일순번")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# 관계 포함 스키마
class FileWithDetails(FileResponse):
    """파일과 파일상세 관계 포함 응답 스키마"""
    file_details: List[FileDetailResponse] = Field(default=[], description="파일상세 목록")


class FileDetailWithFile(FileDetailResponse):
    """파일상세와 파일 관계 포함 응답 스키마"""
    file_info: Optional[FileResponse] = Field(None, description="파일 정보")


# 페이지네이션 응답 스키마
class FileListResponse(BaseModel):
    """파일 목록 응답 스키마"""
    items: List[FileResponse] = Field(..., description="파일 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


class FileDetailListResponse(BaseModel):
    """파일상세 목록 응답 스키마"""
    items: List[FileDetailResponse] = Field(..., description="파일상세 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 파일 업로드 프로세스 응답 스키마
class FileUploadProcessResponse(BaseModel):
    """파일 업로드 프로세스 응답 스키마"""
    atch_file_id: str = Field(..., description="첨부파일ID")
    uploaded_files: List[FileDetailResponse] = Field(..., description="업로드된 파일 목록")
    success_count: int = Field(..., description="성공한 파일 수")
    failed_count: int = Field(..., description="실패한 파일 수")
    total_size: Decimal = Field(..., description="전체 파일 크기")


class FileDownloadInfo(BaseModel):
    """파일 다운로드 정보 스키마"""
    atch_file_id: str = Field(..., description="첨부파일ID")
    file_sn: Decimal = Field(..., description="파일순번")
    orignl_file_nm: str = Field(..., description="원본파일명")
    file_size: Decimal = Field(..., description="파일크기")
    file_extsn: str = Field(..., description="파일확장자")
    download_url: str = Field(..., description="다운로드 URL")


# 파일 검색 스키마
class FileSearchParams(BaseModel):
    """파일 검색 파라미터 스키마"""
    atch_file_id: Optional[str] = Field(None, description="첨부파일ID")
    orignl_file_nm: Optional[str] = Field(None, description="원본파일명")
    file_extsn: Optional[str] = Field(None, description="파일확장자")
    min_file_size: Optional[Decimal] = Field(None, description="최소 파일크기")
    max_file_size: Optional[Decimal] = Field(None, description="최대 파일크기")
    start_date: Optional[datetime] = Field(None, description="등록일 시작")
    end_date: Optional[datetime] = Field(None, description="등록일 종료")
    frst_register_id: Optional[str] = Field(None, description="등록자ID")


# 파일 통계 스키마
class FileStatistics(BaseModel):
    """파일 통계 스키마"""
    total_files: int = Field(..., description="전체 파일 수")
    total_size: Decimal = Field(..., description="전체 파일 크기")
    avg_file_size: Decimal = Field(..., description="평균 파일 크기")
    file_types: dict = Field(..., description="파일 타입별 통계")
    upload_trend: List[dict] = Field(..., description="업로드 추세")


# 파일 검증 스키마
class FileValidationResult(BaseModel):
    """파일 검증 결과 스키마"""
    is_valid: bool = Field(..., description="검증 성공 여부")
    file_name: str = Field(..., description="파일명")
    file_size: Decimal = Field(..., description="파일크기")
    file_type: str = Field(..., description="파일타입")
    errors: List[str] = Field(default=[], description="오류 메시지 목록")
    warnings: List[str] = Field(default=[], description="경고 메시지 목록")


# 페이지네이션 스키마 (라우터에서 사용)
class FilePagination(BaseModel):
    """파일 페이지네이션 응답 스키마"""
    items: List[FileResponse] = Field(..., description="파일 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


class FileDetailPagination(BaseModel):
    """파일상세 페이지네이션 응답 스키마"""
    items: List[FileDetailResponse] = Field(..., description="파일상세 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


# 관계 포함 스키마
class FileWithDetails(FileResponse):
    """파일과 상세정보 포함 응답 스키마"""
    details: List[FileDetailResponse] = Field(default=[], description="파일 상세정보 목록")


# 파일 업로드/다운로드 응답 스키마 (라우터에서 사용)
class FileUploadResponse(BaseModel):
    """파일 업로드 응답 스키마"""
    success: bool = Field(..., description="업로드 성공 여부")
    file_id: str = Field(..., description="파일 ID")
    file_name: str = Field(..., description="파일명")
    file_size: Decimal = Field(..., description="파일크기")
    upload_url: str = Field(..., description="업로드된 파일 URL")
    message: str = Field(..., description="응답 메시지")


class FileDownloadResponse(BaseModel):
    """파일 다운로드 응답 스키마"""
    success: bool = Field(..., description="다운로드 성공 여부")
    file_name: str = Field(..., description="파일명")
    file_size: Decimal = Field(..., description="파일크기")
    download_url: str = Field(..., description="다운로드 URL")
    content_type: str = Field(..., description="콘텐츠 타입")
    expires_at: Optional[datetime] = Field(None, description="URL 만료 시간")


# 파일 검증 응답 스키마 (라우터에서 사용)
class FileValidationResponse(BaseModel):
    """파일 검증 응답 스키마"""
    is_valid: bool = Field(..., description="검증 성공 여부")
    file_name: str = Field(..., description="파일명")
    file_size: Decimal = Field(..., description="파일크기")
    file_type: str = Field(..., description="파일타입")
    validation_results: List[FileValidationResult] = Field(..., description="검증 결과 목록")
    summary: str = Field(..., description="검증 요약")
    recommendations: List[str] = Field(default=[], description="권장사항 목록")
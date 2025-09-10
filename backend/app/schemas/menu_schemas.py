"""메뉴 관련 Pydantic 스키마

메뉴정보 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field


# MenuInfo 스키마
class MenuInfoBase(BaseModel):
    """메뉴정보 기본 스키마"""
    menu_nm: Optional[str] = Field(None, max_length=60, description="메뉴명")
    progrm_file_nm: Optional[str] = Field(None, max_length=60, description="프로그램파일명")
    menu_dc: Optional[str] = Field(None, max_length=250, description="메뉴설명")
    upper_menu_no: Optional[str] = Field(None, max_length=20, description="상위메뉴번호")
    menu_ordr: Optional[Decimal] = Field(None, description="메뉴순서")
    relate_image_path: Optional[str] = Field(None, max_length=100, description="관련이미지경로")
    relate_image_nm: Optional[str] = Field(None, max_length=60, description="관련이미지명")
    display_yn: Optional[str] = Field(None, max_length=1, description="메뉴표시여부")
    use_tag_yn: Optional[str] = Field(None, max_length=1, description="태그사용여부")
    menu_tag: Optional[str] = Field(None, description="메뉴태그")


class MenuInfoCreate(MenuInfoBase):
    """메뉴정보 생성 스키마"""
    menu_no: str = Field(..., max_length=20, description="메뉴번호")
    menu_nm: str = Field(..., max_length=60, description="메뉴명")
    progrm_file_nm: str = Field(..., max_length=60, description="프로그램파일명")
    menu_ordr: Decimal = Field(..., description="메뉴순서")
    display_yn: str = Field(default="Y", max_length=1, description="메뉴표시여부")
    use_tag_yn: str = Field(default="N", max_length=1, description="태그사용여부")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class MenuInfoUpdate(BaseModel):
    """메뉴정보 수정 스키마"""
    menu_nm: Optional[str] = Field(None, max_length=60, description="메뉴명")
    progrm_file_nm: Optional[str] = Field(None, max_length=60, description="프로그램파일명")
    menu_dc: Optional[str] = Field(None, max_length=250, description="메뉴설명")
    upper_menu_no: Optional[str] = Field(None, max_length=20, description="상위메뉴번호")
    menu_ordr: Optional[Decimal] = Field(None, description="메뉴순서")
    relate_image_path: Optional[str] = Field(None, max_length=100, description="관련이미지경로")
    relate_image_nm: Optional[str] = Field(None, max_length=60, description="관련이미지명")
    display_yn: Optional[str] = Field(None, max_length=1, description="메뉴표시여부")
    use_tag_yn: Optional[str] = Field(None, max_length=1, description="태그사용여부")
    menu_tag: Optional[str] = Field(None, description="메뉴태그")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class MenuInfoResponse(MenuInfoBase):
    """메뉴정보 응답 스키마"""
    menu_id: Optional[str] = Field(None, description="메뉴ID")
    menu_no: str = Field(..., description="메뉴번호")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    frst_regist_pnttm: Optional[datetime] = Field(None, description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# 계층형 메뉴 스키마
class MenuTreeNode(MenuInfoResponse):
    """메뉴 트리 노드 스키마"""
    children: List['MenuTreeNode'] = Field(default=[], description="하위 메뉴 목록")
    has_children: bool = Field(default=False, description="하위 메뉴 존재 여부")
    depth: int = Field(default=0, description="메뉴 깊이")
    path: str = Field(default="", description="메뉴 경로")
    breadcrumb: List[str] = Field(default=[], description="메뉴 경로명")


# 메뉴 권한 관련 스키마
class MenuWithPermission(MenuInfoResponse):
    """권한 정보 포함 메뉴 스키마"""
    has_read_permission: bool = Field(default=False, description="읽기 권한")
    has_write_permission: bool = Field(default=False, description="쓰기 권한")
    has_delete_permission: bool = Field(default=False, description="삭제 권한")
    is_accessible: bool = Field(default=False, description="접근 가능 여부")


class MenuTreeWithPermission(MenuTreeNode):
    """권한 정보 포함 메뉴 트리 스키마"""
    has_read_permission: bool = Field(default=False, description="읽기 권한")
    has_write_permission: bool = Field(default=False, description="쓰기 권한")
    has_delete_permission: bool = Field(default=False, description="삭제 권한")
    is_accessible: bool = Field(default=False, description="접근 가능 여부")
    children: List['MenuTreeWithPermission'] = Field(default=[], description="하위 메뉴 목록")


# 페이지네이션 응답 스키마
class MenuInfoListResponse(BaseModel):
    """메뉴정보 목록 응답 스키마"""
    items: List[MenuInfoResponse] = Field(..., description="메뉴정보 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 메뉴 검색 스키마
class MenuSearchParams(BaseModel):
    """메뉴 검색 파라미터 스키마"""
    menu_id: Optional[str] = Field(None, description="메뉴ID")
    menu_nm: Optional[str] = Field(None, description="메뉴명")
    upper_menu_id: Optional[str] = Field(None, description="상위메뉴ID")
    menu_level: Optional[Decimal] = Field(None, description="메뉴레벨")
    leaf_at: Optional[str] = Field(None, description="리프여부")
    use_at: Optional[str] = Field(None, description="사용여부")
    progrm_file_nm: Optional[str] = Field(None, description="프로그램파일명")


# 메뉴 이동 스키마
class MenuMoveRequest(BaseModel):
    """메뉴 이동 요청 스키마"""
    target_menu_id: str = Field(..., description="이동할 메뉴ID")
    new_upper_menu_id: Optional[str] = Field(None, description="새로운 상위메뉴ID")
    new_menu_ordr: Optional[Decimal] = Field(None, description="새로운 메뉴순서")


class MenuOrderUpdateRequest(BaseModel):
    """메뉴 순서 변경 요청 스키마"""
    menu_orders: List[dict] = Field(..., description="메뉴 순서 목록 [{menu_id: str, menu_ordr: Decimal}]")


# 첫 번째 MenuCopyRequest 정의 제거됨 (중복 정의 방지)


# 메뉴 통계 스키마
class MenuStatistics(BaseModel):
    """메뉴 통계 스키마"""
    total_menus: int = Field(..., description="전체 메뉴 수")
    active_menus: int = Field(..., description="활성 메뉴 수")
    inactive_menus: int = Field(..., description="비활성 메뉴 수")
    leaf_menus: int = Field(..., description="리프 메뉴 수")
    parent_menus: int = Field(..., description="부모 메뉴 수")
    max_depth: int = Field(..., description="최대 메뉴 깊이")
    menu_by_level: dict = Field(..., description="레벨별 메뉴 수")


# 메뉴 경로 스키마
class MenuPath(BaseModel):
    """메뉴 경로 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    menu_nm: str = Field(..., description="메뉴명")
    menu_level: Decimal = Field(..., description="메뉴레벨")
    full_path: str = Field(..., description="전체 경로")
    breadcrumb: List[dict] = Field(..., description="경로 정보 [{menu_id, menu_nm}]")


# 메뉴 검증 스키마
class MenuValidationResult(BaseModel):
    """메뉴 검증 결과 스키마"""
    is_valid: bool = Field(..., description="검증 성공 여부")
    menu_id: str = Field(..., description="메뉴ID")
    errors: List[str] = Field(default=[], description="오류 메시지 목록")
    warnings: List[str] = Field(default=[], description="경고 메시지 목록")
    suggestions: List[str] = Field(default=[], description="개선 제안 목록")


# 메뉴 내보내기/가져오기 스키마
class MenuExportData(BaseModel):
    """메뉴 내보내기 데이터 스키마"""
    export_date: datetime = Field(..., description="내보내기 일시")
    total_menus: int = Field(..., description="전체 메뉴 수")
    menu_tree: List[MenuTreeNode] = Field(..., description="메뉴 트리 데이터")
    metadata: dict = Field(default={}, description="메타데이터")


class MenuImportRequest(BaseModel):
    """메뉴 가져오기 요청 스키마"""
    menu_data: List[dict] = Field(..., description="메뉴 데이터")
    overwrite_existing: bool = Field(default=False, description="기존 메뉴 덮어쓰기 여부")
    validate_only: bool = Field(default=False, description="검증만 수행 여부")


class MenuImportResult(BaseModel):
    """메뉴 가져오기 결과 스키마"""
    success: bool = Field(..., description="가져오기 성공 여부")
    imported_count: int = Field(..., description="가져온 메뉴 수")
    skipped_count: int = Field(..., description="건너뛴 메뉴 수")
    error_count: int = Field(..., description="오류 메뉴 수")
    errors: List[str] = Field(default=[], description="오류 메시지 목록")
    warnings: List[str] = Field(default=[], description="경고 메시지 목록")


# 페이지네이션 스키마
class MenuInfoPagination(BaseModel):
    """메뉴정보 페이지네이션 스키마"""
    items: List[MenuInfoResponse] = Field(..., description="메뉴정보 목록")
    total: int = Field(..., description="전체 항목 수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 메뉴 트리 노드 스키마
class MenuTreeNode(BaseModel):
    """메뉴 트리 노드 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    menu_nm: str = Field(..., description="메뉴명")
    menu_level: Decimal = Field(..., description="메뉴레벨")
    menu_ordr: Optional[Decimal] = Field(None, description="메뉴순서")
    leaf_at: str = Field(..., description="리프여부")
    children: List['MenuTreeNode'] = Field(default=[], description="하위 메뉴 목록")


# 권한이 포함된 메뉴 스키마
class MenuWithPermission(BaseModel):
    """권한이 포함된 메뉴 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    menu_nm: str = Field(..., description="메뉴명")
    progrm_file_nm: Optional[str] = Field(None, description="프로그램파일명")
    has_read_permission: bool = Field(..., description="읽기 권한 여부")
    has_write_permission: bool = Field(..., description="쓰기 권한 여부")
    has_delete_permission: bool = Field(..., description="삭제 권한 여부")


# 권한이 포함된 메뉴 트리 스키마
class MenuTreeWithPermission(BaseModel):
    """권한이 포함된 메뉴 트리 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    menu_nm: str = Field(..., description="메뉴명")
    menu_level: Decimal = Field(..., description="메뉴레벨")
    has_access: bool = Field(..., description="접근 권한 여부")
    children: List['MenuTreeWithPermission'] = Field(default=[], description="하위 메뉴 목록")


# 메뉴 검색 파라미터 스키마
class MenuSearchParams(BaseModel):
    """메뉴 검색 파라미터 스키마"""
    menu_nm: Optional[str] = Field(None, description="메뉴명 검색")
    upper_menu_id: Optional[str] = Field(None, description="상위메뉴ID")
    menu_level: Optional[Decimal] = Field(None, description="메뉴레벨")
    use_at: Optional[str] = Field(None, description="사용여부")
    leaf_at: Optional[str] = Field(None, description="리프여부")


# 메뉴 이동 요청 스키마
class MenuMoveRequest(BaseModel):
    """메뉴 이동 요청 스키마"""
    target_menu_id: str = Field(..., description="이동할 메뉴ID")
    new_parent_id: Optional[str] = Field(None, description="새로운 상위메뉴ID")
    new_order: Optional[Decimal] = Field(None, description="새로운 순서")


# 메뉴 순서 업데이트 스키마
class MenuOrderUpdate(BaseModel):
    """메뉴 순서 업데이트 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    new_order: Decimal = Field(..., description="새로운 순서")


# 메뉴 복사 요청 스키마
class MenuCopyRequest(BaseModel):
    """메뉴 복사 요청 스키마"""
    source_menu_id: str = Field(..., description="원본 메뉴ID")
    new_parent_id: Optional[str] = Field(None, description="새로운 상위메뉴ID")
    new_menu_id: str = Field(..., description="새로운 메뉴ID")
    new_menu_nm: Optional[str] = Field(None, description="새로운 메뉴명")
    copy_children: bool = Field(default=True, description="하위 메뉴 포함 복사 여부")


# 메뉴 통계 스키마
class MenuStatistics(BaseModel):
    """메뉴 통계 스키마"""
    total_menus: int = Field(..., description="전체 메뉴 수")
    active_menus: int = Field(..., description="활성 메뉴 수")
    inactive_menus: int = Field(..., description="비활성 메뉴 수")
    leaf_menus: int = Field(..., description="리프 메뉴 수")
    max_depth: int = Field(..., description="최대 깊이")
    avg_children_per_menu: float = Field(..., description="메뉴당 평균 하위 메뉴 수")


# 메뉴 경로 응답 스키마
class MenuPathResponse(BaseModel):
    """메뉴 경로 응답 스키마"""
    menu_id: str = Field(..., description="메뉴ID")
    menu_nm: str = Field(..., description="메뉴명")
    menu_level: Decimal = Field(..., description="메뉴레벨")
    full_path: str = Field(..., description="전체 경로")
    breadcrumb: List[dict] = Field(..., description="경로 정보 [{menu_id, menu_nm}]")


# 메뉴 검증 응답 스키마
class MenuValidationResponse(BaseModel):
    """메뉴 검증 응답 스키마"""
    is_valid: bool = Field(..., description="검증 성공 여부")
    validation_results: List[MenuValidationResult] = Field(..., description="검증 결과 목록")
    summary: dict = Field(..., description="검증 요약 정보")


# 메뉴 내보내기 응답 스키마
class MenuExportResponse(BaseModel):
    """메뉴 내보내기 응답 스키마"""
    export_id: str = Field(..., description="내보내기 ID")
    file_name: str = Field(..., description="파일명")
    file_size: int = Field(..., description="파일 크기")
    download_url: str = Field(..., description="다운로드 URL")
    expires_at: datetime = Field(..., description="만료 시간")
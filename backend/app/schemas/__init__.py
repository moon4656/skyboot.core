"""Pydantic 스키마 모듈

FastAPI 요청/응답 검증을 위한 Pydantic 모델들을 정의합니다.
"""

# 인증 관련 스키마
from .auth_schemas import (
    AuthorInfoBase, AuthorInfoCreate, AuthorInfoUpdate, AuthorInfoResponse,
    AuthorMenuBase, AuthorMenuCreate, AuthorMenuUpdate, AuthorMenuResponse,
    AuthorInfoListResponse, AuthorMenuListResponse,
    AuthorInfoWithMenus, AuthorMenuWithAuthor
)

# 게시판 관련 스키마
from .board_schemas import (
    BbsMasterBase, BbsMasterCreate, BbsMasterUpdate, BbsMasterResponse,
    BbsBase, BbsCreate, BbsUpdate, BbsResponse,
    CommentBase, CommentCreate, CommentUpdate, CommentResponse,
    BbsMasterListResponse, BbsListResponse, CommentListResponse,
    BbsWithComments, BbsMasterWithPosts
)

# 공통 코드 관련 스키마
from .common_schemas import (
    CmmnGrpCodeBase, CmmnGrpCodeCreate, CmmnGrpCodeUpdate, CmmnGrpCodeResponse,
    CmmnCodeBase, CmmnCodeCreate, CmmnCodeUpdate, CmmnCodeResponse,
    CmmnGrpCodeListResponse, CmmnCodeListResponse,
    CmmnGrpCodeWithCodes, CmmnCodeWithGroup,
    CodeSearchParams, GroupCodeSearchParams,
    CodeOption, CodeOptionsResponse
)

# 파일 관련 스키마
from .file_schemas import (
    FileBase, FileCreate, FileUpdate, FileResponse,
    FileDetailBase, FileDetailCreate, FileDetailUpdate, FileDetailResponse,
    FileListResponse, FileDetailListResponse,
    FileWithDetails, FileDetailWithFile,
    FileUploadResponse, FileDownloadInfo,
    FileSearchParams, FileStatistics, FileValidationResult
)

# 메뉴 관련 스키마
from .menu_schemas import (
    MenuInfoBase, MenuInfoCreate, MenuInfoUpdate, MenuInfoResponse,
    MenuInfoListResponse, MenuTreeNode, MenuWithPermission, MenuTreeWithPermission,
    MenuSearchParams, MenuMoveRequest, MenuOrderUpdateRequest, MenuCopyRequest,
    MenuStatistics, MenuPath, MenuValidationResult,
    MenuExportData, MenuImportRequest, MenuImportResult
)

# 로그 관련 스키마
from .log_schemas import (
    LoginLogBase, LoginLogCreate, LoginLogUpdate, LoginLogResponse,
    LoginLogListResponse, LoginLogSearchParams,
    LoginStatistics, DailyLoginStats, HourlyLoginStats,
    SecurityAlert, SuspiciousActivity,
    ActiveSession, SessionTerminateRequest,
    LogExportRequest, LogExportResponse,
    LoginPattern, LoginTrend
)

# 사용자 관련 스키마
from .user_schemas import (
    UserInfoBase, UserInfoCreate, UserInfoUpdate, UserInfoResponse, UserInfoPagination,
    OrgBase, OrgCreate, OrgUpdate, OrgResponse, OrgPagination,
    ZipBase, ZipCreate, ZipUpdate, ZipResponse, ZipPagination,
    UserSearchParams, UserStatistics, OrgTreeNode
)

# 시스템 관련 스키마
from .system_schemas import (
    SysLogBase, SysLogCreate, SysLogUpdate, SysLogResponse, SysLogPagination,
    WebLogBase, WebLogCreate, WebLogUpdate, WebLogResponse, WebLogPagination,
    ProgrmListBase, ProgrmListCreate, ProgrmListUpdate, ProgrmListResponse, ProgrmListPagination,
    LogSearchParams, LogStatistics, ProgrmSearchParams,
    SystemHealthCheck, DashboardSummary
)

__all__ = [
    # 인증 스키마
    "AuthorInfoBase", "AuthorInfoCreate", "AuthorInfoUpdate", "AuthorInfoResponse",
    "AuthorMenuBase", "AuthorMenuCreate", "AuthorMenuUpdate", "AuthorMenuResponse",
    "AuthorInfoListResponse", "AuthorMenuListResponse",
    "AuthorInfoWithMenus", "AuthorMenuWithAuthor",
    
    # 게시판 스키마
    "BbsMasterBase", "BbsMasterCreate", "BbsMasterUpdate", "BbsMasterResponse",
    "BbsBase", "BbsCreate", "BbsUpdate", "BbsResponse",
    "CommentBase", "CommentCreate", "CommentUpdate", "CommentResponse",
    "BbsMasterListResponse", "BbsListResponse", "CommentListResponse",
    "BbsWithComments", "BbsMasterWithPosts",
    
    # 공통 코드 스키마
    "CmmnGrpCodeBase", "CmmnGrpCodeCreate", "CmmnGrpCodeUpdate", "CmmnGrpCodeResponse",
    "CmmnCodeBase", "CmmnCodeCreate", "CmmnCodeUpdate", "CmmnCodeResponse",
    "CmmnGrpCodeListResponse", "CmmnCodeListResponse",
    "CmmnGrpCodeWithCodes", "CmmnCodeWithGroup",
    "CodeSearchParams", "GroupCodeSearchParams",
    "CodeOption", "CodeOptionsResponse",
    
    # 파일 스키마
    "FileBase", "FileCreate", "FileUpdate", "FileResponse",
    "FileDetailBase", "FileDetailCreate", "FileDetailUpdate", "FileDetailResponse",
    "FileListResponse", "FileDetailListResponse",
    "FileWithDetails", "FileDetailWithFile",
    "FileUploadResponse", "FileDownloadInfo",
    "FileSearchParams", "FileStatistics", "FileValidationResult",
    
    # 메뉴 스키마
    "MenuInfoBase", "MenuInfoCreate", "MenuInfoUpdate", "MenuInfoResponse",
    "MenuInfoListResponse", "MenuTreeNode", "MenuWithPermission", "MenuTreeWithPermission",
    "MenuSearchParams", "MenuMoveRequest", "MenuOrderUpdateRequest", "MenuCopyRequest",
    "MenuStatistics", "MenuPath", "MenuValidationResult",
    "MenuExportData", "MenuImportRequest", "MenuImportResult",
    
    # 로그 스키마
    "LoginLogBase", "LoginLogCreate", "LoginLogUpdate", "LoginLogResponse",
    "LoginLogListResponse", "LoginLogSearchParams",
    "LoginStatistics", "DailyLoginStats", "HourlyLoginStats",
    "SecurityAlert", "SuspiciousActivity",
    "ActiveSession", "SessionTerminateRequest",
    "LogExportRequest", "LogExportResponse",
    "LoginPattern", "LoginTrend",
    
    # 사용자 스키마
    "UserInfoBase", "UserInfoCreate", "UserInfoUpdate", "UserInfoResponse", "UserInfoPagination",
    "OrgBase", "OrgCreate", "OrgUpdate", "OrgResponse", "OrgPagination",
    "ZipBase", "ZipCreate", "ZipUpdate", "ZipResponse", "ZipPagination",
    "UserSearchParams", "UserStatistics", "OrgTreeNode",
    
    # 시스템 스키마
    "SysLogBase", "SysLogCreate", "SysLogUpdate", "SysLogResponse", "SysLogPagination",
    "WebLogBase", "WebLogCreate", "WebLogUpdate", "WebLogResponse", "WebLogPagination",
    "ProgrmListBase", "ProgrmListCreate", "ProgrmListUpdate", "ProgrmListResponse", "ProgrmListPagination",
    "LogSearchParams", "LogStatistics", "ProgrmSearchParams",
    "SystemHealthCheck", "DashboardSummary"
]
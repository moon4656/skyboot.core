"""게시판 관련 Pydantic 스키마

게시판마스터, 게시판, 댓글 API 요청/응답을 위한 스키마를 정의합니다.
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field
from fastapi import UploadFile


# BbsMaster 스키마
class BbsMasterBase(BaseModel):
    """게시판마스터 기본 스키마"""
    bbs_nm: str = Field(..., max_length=255, description="게시판명")
    bbs_intrcn: Optional[str] = Field(None, max_length=2400, description="게시판소개")
    bbs_ty_code: str = Field(..., max_length=6, description="게시판유형코드")
    reply_posbl_at: str = Field(default="N", max_length=1, description="답장가능여부")
    file_atch_posbl_at: str = Field(default="N", max_length=1, description="파일첨부가능여부")
    atch_posbl_file_size: Optional[Decimal] = Field(None, description="첨부가능파일사이즈")
    use_at: str = Field(default="Y", max_length=1, description="사용여부")
    delete_at: str = Field(default="N", max_length=1, description="삭제여부")


class BbsMasterCreate(BbsMasterBase):
    """게시판마스터 생성 스키마"""
    bbs_id: str = Field(..., max_length=30, description="게시판ID")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class BbsMasterUpdate(BaseModel):
    """게시판마스터 수정 스키마"""
    bbs_nm: Optional[str] = Field(None, max_length=255, description="게시판명")
    bbs_intrcn: Optional[str] = Field(None, max_length=2400, description="게시판소개")
    bbs_ty_code: Optional[str] = Field(None, max_length=6, description="게시판유형코드")
    reply_posbl_at: Optional[str] = Field(None, max_length=1, description="답장가능여부")
    file_atch_posbl_at: Optional[str] = Field(None, max_length=1, description="파일첨부가능여부")
    atch_posbl_file_size: Optional[Decimal] = Field(None, description="첨부가능파일사이즈")
    use_at: Optional[str] = Field(None, max_length=1, description="사용여부")
    delete_at: Optional[str] = Field(None, max_length=1, description="삭제여부")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class BbsMasterResponse(BbsMasterBase):
    """게시판마스터 응답 스키마"""
    bbs_id: str = Field(..., description="게시판ID")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")

    class Config:
        from_attributes = True


# Bbs 스키마
class BbsBase(BaseModel):
    """게시판 기본 스키마"""
    ntt_no: Optional[Decimal] = Field(None, description="게시물번호")
    ntt_sj: Optional[str] = Field(None, max_length=2000, description="게시물제목")
    ntt_cn: Optional[str] = Field(None, description="게시물내용")
    answer_at: Optional[str] = Field(None, max_length=1, description="댓글여부")
    parntsctt_no: Optional[Decimal] = Field(None, description="부모글번호")
    answer_lc: Optional[Decimal] = Field(None, description="댓글위치")
    sort_ordr: Optional[Decimal] = Field(None, description="정렬순서")
    rdcnt: Optional[Decimal] = Field(default=0, description="조회수")
    use_at: str = Field(default="Y", max_length=1, description="사용여부")
    ntce_bgnde: Optional[str] = Field(None, max_length=20, description="게시시작일")
    ntce_endde: Optional[str] = Field(None, max_length=20, description="게시종료일")
    ntcr_id: Optional[str] = Field(None, max_length=20, description="게시자ID")
    ntcr_nm: Optional[str] = Field(None, max_length=20, description="게시자명")
    password: Optional[str] = Field(None, max_length=200, description="비밀번호")
    atch_file_id: Optional[str] = Field(None, max_length=20, description="첨부파일ID")
    notice_at: Optional[str] = Field(None, max_length=1, description="공지사항여부")
    sj_bold_at: Optional[str] = Field(None, max_length=1, description="제목볼드여부")
    secret_at: Optional[str] = Field(None, max_length=1, description="비밀글여부")
    blog_id: Optional[str] = Field(None, max_length=20, description="블로그 ID")
    delete_at: Optional[str] = Field(None, max_length=1, description="삭제여부")


class BbsCreate(BbsBase):
    """게시판 생성 스키마"""
    ntt_id: Decimal = Field(..., description="게시물ID")
    bbs_id: str = Field(..., max_length=30, description="게시판ID")
    frst_register_id: str = Field(..., max_length=20, description="최초등록자ID")


class BbsUpdate(BaseModel):
    """게시판 수정 스키마"""
    ntt_sj: Optional[str] = Field(None, max_length=2000, description="게시물제목")
    ntt_cn: Optional[str] = Field(None, description="게시물내용")
    use_at: Optional[str] = Field(None, max_length=1, description="사용여부")
    ntce_bgnde: Optional[str] = Field(None, max_length=20, description="게시시작일")
    ntce_endde: Optional[str] = Field(None, max_length=20, description="게시종료일")
    atch_file_id: Optional[str] = Field(None, max_length=20, description="첨부파일ID")
    notice_at: Optional[str] = Field(None, max_length=1, description="공지사항여부")
    sj_bold_at: Optional[str] = Field(None, max_length=1, description="제목볼드여부")
    secret_at: Optional[str] = Field(None, max_length=1, description="비밀글여부")
    delete_at: Optional[str] = Field(None, max_length=1, description="삭제여부")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class BbsResponse(BbsBase):
    """게시판 응답 스키마"""
    ntt_id: Decimal = Field(..., description="게시물ID")
    bbs_id: str = Field(..., description="게시판ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: str = Field(..., description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


# Comment 스키마
class CommentBase(BaseModel):
    """댓글 기본 스키마"""
    wrter_id: Optional[str] = Field(None, max_length=20, description="작성자ID")
    wrter_nm: Optional[str] = Field(None, max_length=20, description="작성자명")
    answer: Optional[str] = Field(None, max_length=2000, description="댓글")
    use_at: str = Field(default="Y", max_length=1, description="사용여부")
    password: Optional[str] = Field(None, max_length=200, description="비밀번호")


class CommentCreate(CommentBase):
    """댓글 생성 스키마"""
    ntt_id: Decimal = Field(..., description="게시물ID")
    bbs_id: str = Field(..., max_length=30, description="게시판ID")
    answer_no: Decimal = Field(..., description="댓글번호")
    frst_register_id: Optional[str] = Field(None, max_length=20, description="최초등록자ID")


class CommentUpdate(BaseModel):
    """댓글 수정 스키마"""
    answer: Optional[str] = Field(None, max_length=2000, description="댓글")
    use_at: Optional[str] = Field(None, max_length=1, description="사용여부")
    last_updusr_id: Optional[str] = Field(None, max_length=20, description="최종수정자ID")


class CommentResponse(CommentBase):
    """댓글 응답 스키마"""
    ntt_id: Decimal = Field(..., description="게시물ID")
    bbs_id: str = Field(..., description="게시판ID")
    answer_no: Decimal = Field(..., description="댓글번호")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
    frst_register_id: Optional[str] = Field(None, description="최초등록자ID")
    last_updt_pnttm: Optional[datetime] = Field(None, description="최종수정시점")
    last_updusr_id: Optional[str] = Field(None, description="최종수정자ID")

    class Config:
        from_attributes = True


# 파일 업로드 관련 스키마
class BbsCreateWithFiles(BaseModel):
    """파일 업로드와 함께 게시글 생성 스키마"""
    bbs_id: str = Field(..., description="게시판 ID")
    ntt_sj: str = Field(..., min_length=1, max_length=200, description="게시글 제목")
    ntt_cn: str = Field(..., min_length=1, description="게시글 내용")
    ntcrNm: Optional[str] = Field(None, max_length=50, description="작성자명")
    password: Optional[str] = Field(None, max_length=100, description="비밀번호")
    
    class Config:
        from_attributes = True


class BbsUpdateWithFiles(BaseModel):
    """파일 업로드와 함께 게시글 수정 스키마"""
    ntt_sj: Optional[str] = Field(None, min_length=1, max_length=200, description="게시글 제목")
    ntt_cn: Optional[str] = Field(None, min_length=1, description="게시글 내용")
    ntcrNm: Optional[str] = Field(None, max_length=50, description="작성자명")
    password: Optional[str] = Field(None, max_length=100, description="비밀번호")
    delete_file_sns: Optional[List[int]] = Field(None, description="삭제할 파일 일련번호 목록")
    
    class Config:
        from_attributes = True


class FileInfo(BaseModel):
    """첨부파일 정보 스키마"""
    file_sn: int = Field(..., description="파일 일련번호")
    orignl_file_nm: str = Field(..., description="원본 파일명")
    file_size: int = Field(..., description="파일 크기")
    file_extsn: str = Field(..., description="파일 확장자")
    dwld_co: Optional[int] = Field(0, description="다운로드 수")
    frst_regist_pnttm: datetime = Field(..., description="등록일시")
    
    class Config:
        from_attributes = True


class BbsResponseWithFiles(BbsResponse):
    """첨부파일 정보를 포함한 게시글 응답 스키마"""
    attached_files: Optional[List[FileInfo]] = Field(None, description="첨부파일 목록")
    
    class Config:
        from_attributes = True


# 관계 포함 스키마
class BbsWithComments(BbsResponse):
    """게시판과 댓글 관계 포함 응답 스키마"""
    comments: List[CommentResponse] = Field(default=[], description="댓글 목록")


class BbsMasterWithPosts(BbsMasterResponse):
    """게시판마스터와 게시물 관계 포함 응답 스키마"""
    bbs_posts: List[BbsResponse] = Field(default=[], description="게시물 목록")


# 페이지네이션 응답 스키마
class BbsMasterListResponse(BaseModel):
    """게시판마스터 목록 응답 스키마"""
    items: List[BbsMasterResponse] = Field(..., description="게시판마스터 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


class BbsListResponse(BaseModel):
    """게시판 목록 응답 스키마"""
    items: List[BbsResponse] = Field(..., description="게시판 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


class CommentListResponse(BaseModel):
    """댓글 목록 응답 스키마"""
    items: List[CommentResponse] = Field(..., description="댓글 목록")
    total: int = Field(..., description="전체 개수")
    page: int = Field(..., description="현재 페이지")
    size: int = Field(..., description="페이지 크기")
    pages: int = Field(..., description="전체 페이지 수")


# 페이지네이션 스키마 (라우터에서 사용)
class BbsMasterPagination(BaseModel):
    """게시판마스터 페이지네이션 응답 스키마"""
    items: List[BbsMasterResponse] = Field(..., description="게시판마스터 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


class BbsPagination(BaseModel):
    """게시판 페이지네이션 응답 스키마"""
    items: List[BbsResponse] = Field(..., description="게시판 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


class CommentPagination(BaseModel):
    """댓글 페이지네이션 응답 스키마"""
    items: List[CommentResponse] = Field(..., description="댓글 목록")
    total: int = Field(..., description="전체 개수")
    skip: int = Field(..., description="건너뛴 개수")
    limit: int = Field(..., description="조회 개수")


# 인기 게시물 응답 스키마
class PopularPostResponse(BaseModel):
    """인기 게시물 응답 스키마"""
    bbs_id: str = Field(..., description="게시판ID")
    ntt_id: int = Field(..., description="게시물ID")
    ntt_sj: str = Field(..., description="게시물제목")
    ntt_cn: Optional[str] = Field(None, description="게시물내용")
    view_count: int = Field(default=0, description="조회수")
    like_count: int = Field(default=0, description="좋아요수")
    comment_count: int = Field(default=0, description="댓글수")
    popularity_score: float = Field(..., description="인기도점수")
    frst_register_id: str = Field(..., description="최초등록자ID")
    frst_regist_pnttm: datetime = Field(..., description="최초등록시점")
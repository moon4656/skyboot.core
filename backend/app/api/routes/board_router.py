"""게시판 관련 API 라우터

게시판 마스터, 게시글, 댓글 관리를 위한 FastAPI 라우터를 정의합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.services import BbsMasterService, BbsService, CommentService
from app.utils.dependencies import get_current_user
from app.schemas.board_schemas import (
    BbsMasterResponse, BbsMasterCreate, BbsMasterUpdate,
    BbsResponse, BbsCreate, BbsUpdate,
    CommentResponse, CommentCreate, CommentUpdate,
    BbsMasterPagination, BbsPagination, CommentPagination,
    BbsWithComments, PopularPostResponse
)

# 게시판 마스터 라우터
bbs_master_router = APIRouter(
    prefix="/bbs-master",
    tags=["게시판 마스터 관리"],
    responses={404: {"description": "Not found"}}
)

# 게시글 라우터
bbs_router = APIRouter(
    prefix="/bbs",
    tags=["게시글 관리"],
    responses={404: {"description": "Not found"}}
)

# 댓글 라우터
comment_router = APIRouter(
    prefix="/comments",
    tags=["댓글 관리"],
    responses={404: {"description": "Not found"}}
)

# 서비스 인스턴스는 각 함수에서 생성


# ==================== 게시판 마스터 API ====================

@bbs_master_router.get("/", response_model=BbsMasterPagination, summary="게시판 마스터 목록 조회")
async def get_bbs_masters(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    search: Optional[str] = Query(None, description="검색어 (게시판명)"),
    use_at: Optional[str] = Query(None, description="사용 여부 (Y/N)"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시판 마스터 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **search**: 검색어 (게시판명에서 검색)
    - **use_at**: 사용 여부로 필터링
    """
    try:
        bbs_master_service = BbsMasterService()
        bbs_masters = bbs_master_service.search_boards(
            db=db,
            search_term=search,
            use_at=use_at,
            skip=skip,
            limit=limit
        )
        
        total_count = bbs_master_service.count(db=db)
        
        return BbsMasterPagination(
            items=bbs_masters,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 마스터 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_master_router.get("/active", response_model=List[BbsMasterResponse], summary="활성 게시판 목록 조회")
async def get_active_bbs_masters(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    활성화된 게시판 마스터 목록을 조회합니다.
    """
    try:
        bbs_master_service = BbsMasterService()
        active_boards = bbs_master_service.get_active_boards(db=db)
        return active_boards
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"활성 게시판 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_master_router.get("/{bbs_id}", response_model=BbsMasterResponse, summary="게시판 마스터 상세 조회")
async def get_bbs_master(
    bbs_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 게시판 마스터의 상세 정보를 조회합니다.
    
    - **bbs_id**: 게시판 ID
    """
    try:
        bbs_master_service = BbsMasterService()
        bbs_master = bbs_master_service.get_by_bbs_id(db=db, bbs_id=bbs_id)
        
        if not bbs_master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시판을 찾을 수 없습니다: {bbs_id}"
            )
        
        return bbs_master
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 마스터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_master_router.post("/", response_model=BbsMasterResponse, summary="게시판 마스터 생성")
async def create_bbs_master(
    bbs_master_data: BbsMasterCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 게시판 마스터를 생성합니다.
    
    - **bbs_id**: 게시판 ID (고유값)
    - **bbs_nm**: 게시판명
    - **bbs_intrcn**: 게시판 소개
    - **bbs_ty_code**: 게시판 유형 코드
    """
    try:
        # 중복 확인
        bbs_master_service = BbsMasterService()
        existing_board = bbs_master_service.get_by_bbs_id(db=db, bbs_id=bbs_master_data.bbs_id)
        if existing_board:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 존재하는 게시판 ID입니다: {bbs_master_data.bbs_id}"
            )
        
        bbs_master = bbs_master_service.create(db=db, obj_in=bbs_master_data)
        return bbs_master
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 마스터 생성 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_master_router.put("/{bbs_id}", response_model=BbsMasterResponse, summary="게시판 마스터 수정")
async def update_bbs_master(
    bbs_id: str,
    bbs_master_data: BbsMasterUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시판 마스터 정보를 수정합니다.
    
    - **bbs_id**: 수정할 게시판 ID
    """
    try:
        bbs_master_service = BbsMasterService()
        bbs_master = bbs_master_service.get_by_bbs_id(db=db, bbs_id=bbs_id)
        if not bbs_master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시판을 찾을 수 없습니다: {bbs_id}"
            )
        
        updated_bbs_master = bbs_master_service.update(
            db=db,
            db_obj=bbs_master,
            obj_in=bbs_master_data
        )
        
        return updated_bbs_master
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 마스터 수정 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_master_router.delete("/{bbs_id}", summary="게시판 마스터 삭제")
async def delete_bbs_master(
    bbs_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시판 마스터를 삭제합니다 (소프트 삭제).
    
    - **bbs_id**: 삭제할 게시판 ID
    """
    try:
        bbs_master_service = BbsMasterService()
        bbs_master = bbs_master_service.get_by_bbs_id(db=db, bbs_id=bbs_id)
        if not bbs_master:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시판을 찾을 수 없습니다: {bbs_id}"
            )
        
        # BbsMaster 모델은 bbs_id가 기본키이므로 직접 delete_at 필드를 'Y'로 변경
        bbs_master.delete_at = 'Y'
        bbs_master.last_updusr_id = current_user.get('user_id', 'system')
        bbs_master.last_updt_pnttm = datetime.now()
        
        db.add(bbs_master)
        db.commit()
        db.refresh(bbs_master)
        
        return {"message": f"게시판이 삭제되었습니다: {bbs_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시판 마스터 삭제 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 게시글 API ====================

@bbs_router.get("/", response_model=BbsPagination, summary="게시글 목록 조회")
async def get_posts(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    bbs_id: Optional[str] = Query(None, description="게시판 ID"),
    search: Optional[str] = Query(None, description="검색어 (제목, 내용)"),
    author: Optional[str] = Query(None, description="작성자"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시글 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **bbs_id**: 게시판 ID로 필터링
    - **search**: 검색어 (제목, 내용에서 검색)
    - **author**: 작성자로 필터링
    """
    try:
        bbs_service = BbsService()
        if bbs_id:
            posts = bbs_service.get_board_posts(
                db=db,
                bbs_id=bbs_id,
                skip=skip,
                limit=limit
            )
        else:
            posts = bbs_service.search_posts(
                db=db,
                search_term=search,
                author=author,
                skip=skip,
                limit=limit
            )
        
        total_count = bbs_service.count(db=db)
        
        # posts가 None인 경우 빈 리스트로 처리
        if posts is None:
            posts = []
        
        return BbsPagination(
            items=posts,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.get("/popular", response_model=List[PopularPostResponse], summary="인기 게시글 조회")
async def get_popular_posts(
    days: int = Query(7, ge=1, le=30, description="조회 기간 (일)"),
    limit: int = Query(10, ge=1, le=50, description="조회할 최대 레코드 수"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    인기 게시글 목록을 조회합니다.
    
    - **days**: 조회 기간 (일)
    - **limit**: 조회할 최대 레코드 수
    """
    try:
        bbs_service = BbsService()
        popular_posts = bbs_service.get_popular_posts(
            db=db,
            days=days,
            limit=limit
        )
        
        return popular_posts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"인기 게시글 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.get("/{ntt_id}", response_model=BbsWithComments, summary="게시글 상세 조회")
async def get_post(
    ntt_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 게시글의 상세 정보를 조회합니다 (댓글 포함).
    
    - **ntt_id**: 게시글 ID
    """
    try:
        bbs_service = BbsService()
        post = bbs_service.get_by_ntt_id(db=db, ntt_id=ntt_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시글을 찾을 수 없습니다: {ntt_id}"
            )
        
        # 조회수 증가
        bbs_service.increase_view_count(db=db, ntt_id=ntt_id)
        
        # 댓글 조회
        comment_service = CommentService()
        comments = comment_service.get_post_comments(db=db, ntt_id=ntt_id)
        
        return BbsWithComments(
            **post.__dict__,
            comments=comments
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 조회 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.post("/", response_model=BbsResponse, summary="게시글 생성")
async def create_post(
    post_data: BbsCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 게시글을 생성합니다.
    
    - **bbs_id**: 게시판 ID
    - **ntt_sj**: 게시글 제목
    - **ntt_cn**: 게시글 내용
    - **ntcr_id**: 작성자 ID
    """
    try:
        # 게시판 존재 확인
        bbs_master_service = BbsMasterService()
        board = bbs_master_service.get_by_bbs_id(db=db, bbs_id=post_data.bbs_id)
        if not board:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시판을 찾을 수 없습니다: {post_data.bbs_id}"
            )
        
        bbs_service = BbsService()
        post = bbs_service.create(db=db, obj_in=post_data)
        return post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 생성 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.put("/{ntt_id}", response_model=BbsResponse, summary="게시글 수정")
async def update_post(
    ntt_id: int,
    post_data: BbsUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시글 정보를 수정합니다.
    
    - **ntt_id**: 수정할 게시글 ID
    """
    try:
        bbs_service = BbsService()
        post = bbs_service.get_by_ntt_id(db=db, ntt_id=ntt_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시글을 찾을 수 없습니다: {ntt_id}"
            )
        
        updated_post = bbs_service.update(
            db=db,
            db_obj=post,
            obj_in=post_data
        )
        
        return updated_post
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 수정 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.delete("/{ntt_id}", summary="게시글 삭제")
async def delete_post(
    ntt_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시글을 삭제합니다 (소프트 삭제).
    
    - **ntt_id**: 삭제할 게시글 ID
    """
    try:
        bbs_service = BbsService()
        post = bbs_service.get_by_ntt_id(db=db, ntt_id=ntt_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시글을 찾을 수 없습니다: {ntt_id}"
            )
        
        # Bbs 모델은 복합 기본키를 사용하므로 직접 delete_at 필드를 'Y'로 변경
        post.delete_at = 'Y'
        post.last_updusr_id = current_user.get('user_id', 'system')
        post.last_updt_pnttm = datetime.now()
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return {"message": f"게시글이 삭제되었습니다: {ntt_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@bbs_router.post("/{ntt_id}/recommend", summary="게시글 추천")
async def recommend_post(
    ntt_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    게시글을 추천합니다.
    
    - **ntt_id**: 추천할 게시글 ID
    """
    try:
        bbs_service = BbsService()
        post = bbs_service.get_by_ntt_id(db=db, ntt_id=ntt_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시글을 찾을 수 없습니다: {ntt_id}"
            )
        
        bbs_service.increase_recommend_count(db=db, ntt_id=ntt_id)
        
        return {"message": f"게시글을 추천했습니다: {ntt_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"게시글 추천 중 오류가 발생했습니다: {str(e)}"
        )


# ==================== 댓글 API ====================

@comment_router.get("/post/{ntt_id}", response_model=List[CommentResponse], summary="게시글 댓글 조회")
async def get_post_comments(
    ntt_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 게시글의 댓글 목록을 조회합니다.
    
    - **ntt_id**: 게시글 ID
    """
    try:
        comments = comment_service.get_post_comments(db=db, ntt_id=ntt_id)
        return comments
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 조회 중 오류가 발생했습니다: {str(e)}"
        )


@comment_router.get("/", response_model=CommentPagination, summary="댓글 목록 조회")
async def get_comments(
    skip: int = Query(0, ge=0, description="건너뛸 레코드 수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 최대 레코드 수"),
    search: Optional[str] = Query(None, description="검색어 (댓글 내용)"),
    author: Optional[str] = Query(None, description="작성자"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    댓글 목록을 조회합니다.
    
    - **skip**: 건너뛸 레코드 수 (페이징)
    - **limit**: 조회할 최대 레코드 수
    - **search**: 검색어 (댓글 내용에서 검색)
    - **author**: 작성자로 필터링
    """
    try:
        comment_service = CommentService()
        comments = comment_service.search_comments(
            db=db,
            search_term=search,
            author=author,
            skip=skip,
            limit=limit
        )
        
        total_count = comment_service.count(db=db)
        
        return CommentPagination(
            items=comments,
            total=total_count,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@comment_router.post("/", response_model=CommentResponse, summary="댓글 생성")
async def create_comment(
    comment_data: CommentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    새로운 댓글을 생성합니다.
    
    - **ntt_id**: 게시글 ID
    - **comment_cn**: 댓글 내용
    - **commentr_id**: 댓글 작성자 ID
    """
    try:
        # 게시글 존재 확인
        bbs_service = BbsService()
        post = bbs_service.get_by_ntt_id(db=db, ntt_id=comment_data.ntt_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"게시글을 찾을 수 없습니다: {comment_data.ntt_id}"
            )
        
        comment_service = CommentService()
        comment = comment_service.create(db=db, obj_in=comment_data)
        return comment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 생성 중 오류가 발생했습니다: {str(e)}"
        )


@comment_router.put("/{comment_id}", response_model=CommentResponse, summary="댓글 수정")
async def update_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    댓글 정보를 수정합니다.
    
    - **comment_id**: 수정할 댓글 ID
    """
    try:
        comment_service = CommentService()
        comment = comment_service.get(db=db, id=comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"댓글을 찾을 수 없습니다: {comment_id}"
            )
        
        updated_comment = comment_service.update(
            db=db,
            db_obj=comment,
            obj_in=comment_data
        )
        
        return updated_comment
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 수정 중 오류가 발생했습니다: {str(e)}"
        )


@comment_router.delete("/{comment_id}", summary="댓글 삭제")
async def delete_comment(
    comment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    댓글을 삭제합니다 (소프트 삭제).
    
    - **comment_id**: 삭제할 댓글 ID
    """
    try:
        comment_service = CommentService()
        comment = comment_service.get(db=db, id=comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"댓글을 찾을 수 없습니다: {comment_id}"
            )
        
        # Comment 모델은 복합 기본키를 사용하므로 직접 use_at 필드를 'N'으로 변경
        comment.use_at = 'N'
        comment.last_updusr_id = current_user.get('user_id', 'system')
        comment.last_updt_pnttm = datetime.now()
        
        db.add(comment)
        db.commit()
        db.refresh(comment)
        
        return {"message": f"댓글이 삭제되었습니다: {comment_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"댓글 삭제 중 오류가 발생했습니다: {str(e)}"
        )
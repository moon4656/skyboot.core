"""게시판 관련 서비스

게시판 마스터, 게시글, 댓글 관리를 위한 서비스 클래스들을 정의합니다.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime
import logging

from app.models.board_models import BbsMaster, Bbs, Comment
from app.schemas.board_schemas import (
    BbsMasterCreate, BbsMasterUpdate,
    BbsCreate, BbsUpdate,
    CommentCreate, CommentUpdate
)
from .base_service import BaseService

logger = logging.getLogger(__name__)


class BbsMasterService(BaseService[BbsMaster, BbsMasterCreate, BbsMasterUpdate]):
    """게시판 마스터 서비스
    
    게시판 설정 및 관리를 위한 서비스입니다.
    """
    
    def __init__(self):
        super().__init__(BbsMaster)
    
    def get_by_bbs_id(self, db: Session, bbs_id: str) -> Optional[BbsMaster]:
        """
        게시판 ID로 게시판 마스터 조회
        
        Args:
            db: 데이터베이스 세션
            bbs_id: 게시판 ID
            
        Returns:
            게시판 마스터 정보 또는 None
        """
        try:
            return db.query(BbsMaster).filter(
                and_(
                    BbsMaster.bbs_id == bbs_id,
                    BbsMaster.use_at == 'Y',
                    BbsMaster.delete_at == 'N'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 게시판 마스터 조회 실패 - bbs_id: {bbs_id}, 오류: {str(e)}")
            raise
    
    def get_active_boards(self, db: Session) -> List[BbsMaster]:
        """
        활성화된 게시판 목록 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            활성화된 게시판 목록
        """
        try:
            return db.query(BbsMaster).filter(
                and_(
                    BbsMaster.use_at == 'Y',
                    BbsMaster.delete_at == 'N'
                )
            ).order_by(BbsMaster.frst_regist_pnttm).all()
        except Exception as e:
            logger.error(f"❌ 활성 게시판 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_boards(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        bbs_ty_code: Optional[str] = None,
        use_at: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[BbsMaster]:
        """
        게시판 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어 (게시판명, 설명)
            bbs_ty_code: 게시판 유형 코드
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 게시판 목록
        """
        try:
            query = db.query(BbsMaster)
            
            # 기본 조건 (삭제되지 않은 게시판)
            query = query.filter(BbsMaster.delete_at == 'N')
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    BbsMaster.bbs_nm.like(f"%{search_term}%"),
                    BbsMaster.bbs_dc.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # 게시판 유형 조건
            if bbs_ty_code:
                query = query.filter(BbsMaster.bbs_ty_code == bbs_ty_code)
            
            # 사용 여부 조건
            if use_at:
                query = query.filter(BbsMaster.use_at == use_at)
            
            return query.order_by(BbsMaster.frst_regist_pnttm).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 게시판 검색 실패 - 오류: {str(e)}")
            raise


class BbsService(BaseService[Bbs, BbsCreate, BbsUpdate]):
    """게시글 서비스
    
    게시글 작성, 수정, 삭제, 조회 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(Bbs)
    
    def get_by_ntt_id(self, db: Session, ntt_id: int) -> Optional[Bbs]:
        """
        게시글 ID로 게시글 조회
        
        Args:
            db: 데이터베이스 세션
            ntt_id: 게시글 ID
            
        Returns:
            게시글 정보 또는 None
        """
        try:
            return db.query(Bbs).filter(
                and_(
                    Bbs.ntt_id == ntt_id,
                    Bbs.delete_at == 'N'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 게시글 조회 실패 - ntt_id: {ntt_id}, 오류: {str(e)}")
            raise
    
    def get_board_posts(
        self, 
        db: Session, 
        bbs_id: str,
        skip: int = 0,
        limit: int = 20,
        order_by: str = 'latest'
    ) -> List[Bbs]:
        """
        게시판별 게시글 목록 조회
        
        Args:
            db: 데이터베이스 세션
            bbs_id: 게시판 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            order_by: 정렬 방식 (latest, oldest, views, likes)
            
        Returns:
            게시글 목록
        """
        try:
            query = db.query(Bbs).filter(
                and_(
                    Bbs.bbs_id == bbs_id,
                    Bbs.delete_at == 'N'
                )
            )
            
            # 정렬 조건
            if order_by == 'latest':
                query = query.order_by(desc(Bbs.frst_regist_pnttm))
            elif order_by == 'oldest':
                query = query.order_by(asc(Bbs.frst_regist_pnttm))
            elif order_by == 'views':
                query = query.order_by(desc(Bbs.rdcnt))
            elif order_by == 'likes':
                query = query.order_by(desc(Bbs.recomend_cnt))
            else:
                query = query.order_by(desc(Bbs.frst_regist_pnttm))
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 게시판 게시글 목록 조회 실패 - bbs_id: {bbs_id}, 오류: {str(e)}")
            raise
    
    def search_posts(
        self, 
        db: Session, 
        bbs_id: Optional[str] = None,
        search_term: Optional[str] = None,
        search_type: str = 'all',
        author: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> List[Bbs]:
        """
        게시글 검색
        
        Args:
            db: 데이터베이스 세션
            bbs_id: 게시판 ID
            search_term: 검색어
            search_type: 검색 유형 (all, title, content, author)
            author: 작성자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 게시글 목록
        """
        try:
            query = db.query(Bbs).filter(Bbs.delete_at == 'N')
            
            # 게시판 조건
            if bbs_id:
                query = query.filter(Bbs.bbs_id == bbs_id)
            
            # 작성자 조건
            if author:
                query = query.filter(Bbs.frst_register_id == author)
                
                # 검색어 조건
                if search_term:
                    if search_type == 'title':
                        query = query.filter(Bbs.ntt_sj.like(f"%{search_term}%"))
                    elif search_type == 'content':
                        query = query.filter(Bbs.ntt_cn.like(f"%{search_term}%"))
                    elif search_type == 'author':
                        query = query.filter(Bbs.ntcrNm.like(f"%{search_term}%"))
                    else:  # all
                        search_filter = or_(
                            Bbs.ntt_sj.like(f"%{search_term}%"),
                            Bbs.ntt_cn.like(f"%{search_term}%"),
                            Bbs.ntcrNm.like(f"%{search_term}%")
                        )
                        query = query.filter(search_filter)
                
                return query.order_by(desc(Bbs.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 게시글 검색 실패 - 오류: {str(e)}")
            return []
    
    def increase_view_count(self, db: Session, ntt_id: int) -> bool:
        """
        게시글 조회수 증가
        
        Args:
            db: 데이터베이스 세션
            ntt_id: 게시글 ID
            
        Returns:
            조회수 증가 성공 여부
        """
        try:
            post = self.get_by_ntt_id(db, ntt_id)
            if not post:
                return False
            
            post.rdcnt = (post.rdcnt or 0) + 1
            post.last_updt_pnttm = datetime.now()
            
            db.add(post)
            db.commit()
            
            logger.info(f"✅ 조회수 증가 완료 - ntt_id: {ntt_id}, 조회수: {post.rdcnt}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 조회수 증가 실패 - ntt_id: {ntt_id}, 오류: {str(e)}")
            raise
    
    def increase_recommend_count(self, db: Session, ntt_id: int) -> bool:
        """
        게시글 추천수 증가
        
        Args:
            db: 데이터베이스 세션
            ntt_id: 게시글 ID
            
        Returns:
            추천수 증가 성공 여부
        """
        try:
            post = self.get_by_ntt_id(db, ntt_id)
            if not post:
                return False
            
            post.recomend_cnt = (post.recomend_cnt or 0) + 1
            post.last_updt_pnttm = datetime.now()
            
            db.add(post)
            db.commit()
            
            logger.info(f"✅ 추천수 증가 완료 - ntt_id: {ntt_id}, 추천수: {post.recomend_cnt}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 추천수 증가 실패 - ntt_id: {ntt_id}, 오류: {str(e)}")
            raise
    
    def get_popular_posts(
        self, 
        db: Session, 
        bbs_id: Optional[str] = None,
        days: int = 7,
        limit: int = 10
    ) -> List[Bbs]:
        """
        인기 게시글 조회
        
        Args:
            db: 데이터베이스 세션
            bbs_id: 게시판 ID (None이면 전체)
            days: 기간 (일)
            limit: 조회할 최대 레코드 수
            
        Returns:
            인기 게시글 목록
        """
        try:
            from datetime import timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            query = db.query(Bbs).filter(
                and_(
                    Bbs.delete_at == 'N',
                    Bbs.frst_regist_pnttm >= start_date
                )
            )
            
            if bbs_id:
                query = query.filter(Bbs.bbs_id == bbs_id)
            
            # 조회수와 추천수를 합산하여 정렬
            query = query.order_by(
                desc((func.coalesce(Bbs.rdcnt, 0) + func.coalesce(Bbs.recomend_cnt, 0) * 2))
            )
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 인기 게시글 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_user_posts(
        self, 
        db: Session, 
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Bbs]:
        """
        사용자 작성 게시글 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            사용자 작성 게시글 목록
        """
        try:
            return db.query(Bbs).filter(
                and_(
                    Bbs.frst_register_id == user_id,
                    Bbs.delete_at == 'N'
                )
            ).order_by(desc(Bbs.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 사용자 게시글 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise


class CommentService(BaseService[Comment, CommentCreate, CommentUpdate]):
    """댓글 서비스
    
    댓글 작성, 수정, 삭제, 조회 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(Comment)
    
    def get_post_comments(
        self, 
        db: Session, 
        ntt_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[Comment]:
        """
        게시글의 댓글 목록 조회
        
        Args:
            db: 데이터베이스 세션
            ntt_id: 게시글 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            댓글 목록
        """
        try:
            return db.query(Comment).filter(
                and_(
                    Comment.ntt_id == ntt_id,
                    Comment.delete_at == 'N'
                )
            ).order_by(Comment.frst_regist_pnttm).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 게시글 댓글 조회 실패 - ntt_id: {ntt_id}, 오류: {str(e)}")
            raise
    
    def get_comment_count(self, db: Session, ntt_id: int) -> int:
        """
        게시글의 댓글 수 조회
        
        Args:
            db: 데이터베이스 세션
            ntt_id: 게시글 ID
            
        Returns:
            댓글 수
        """
        try:
            return db.query(Comment).filter(
                and_(
                    Comment.ntt_id == ntt_id,
                    Comment.delete_at == 'N'
                )
            ).count()
            
        except Exception as e:
            logger.error(f"❌ 댓글 수 조회 실패 - ntt_id: {ntt_id}, 오류: {str(e)}")
            raise
    
    def get_user_comments(
        self, 
        db: Session, 
        user_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Comment]:
        """
        사용자 작성 댓글 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            사용자 작성 댓글 목록
        """
        try:
            return db.query(Comment).filter(
                and_(
                    Comment.frst_register_id == user_id,
                    Comment.delete_at == 'N'
                )
            ).order_by(desc(Comment.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 사용자 댓글 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def search_comments(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        author_id: Optional[str] = None,
        ntt_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Comment]:
        """
        댓글 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어
            author_id: 작성자 ID
            ntt_id: 게시글 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 댓글 목록
        """
        try:
            query = db.query(Comment).filter(Comment.delete_at == 'N')
            
            # 게시글 조건
            if ntt_id:
                query = query.filter(Comment.ntt_id == ntt_id)
            
            # 작성자 조건
            if author_id:
                query = query.filter(Comment.frst_register_id == author_id)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    Comment.comment_cn.like(f"%{search_term}%"),
                    Comment.commentr_nm.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            return query.order_by(desc(Comment.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 댓글 검색 실패 - 오류: {str(e)}")
            raise
    
    def get_recent_comments(
        self, 
        db: Session, 
        days: int = 7,
        limit: int = 10
    ) -> List[Comment]:
        """
        최근 댓글 조회
        
        Args:
            db: 데이터베이스 세션
            days: 기간 (일)
            limit: 조회할 최대 레코드 수
            
        Returns:
            최근 댓글 목록
        """
        try:
            from datetime import timedelta
            
            start_date = datetime.now() - timedelta(days=days)
            
            return db.query(Comment).filter(
                and_(
                    Comment.delete_at == 'N',
                    Comment.frst_regist_pnttm >= start_date
                )
            ).order_by(desc(Comment.frst_regist_pnttm)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 최근 댓글 조회 실패 - 오류: {str(e)}")
            raise
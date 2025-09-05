"""게시판 관련 SQLAlchemy 모델

게시판, 게시판마스터, 댓글 테이블에 대응하는 모델을 정의합니다.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Numeric, ForeignKey, Index, and_, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from ..database.database import Base


class BbsMaster(Base):
    """게시판마스터 테이블 모델
    
    게시판의 기본 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_bbsmaster"
    __table_args__ = {
        'schema': 'skybootcore',
        'comment': '게시판마스터'
    }
    
    # 기본 필드
    bbs_id = Column(String(30), primary_key=True, comment="게시판ID")
    bbs_nm = Column(String(255), nullable=False, comment="게시판명")
    bbs_intrcn = Column(String(2400), nullable=True, comment="게시판소개")
    bbs_ty_code = Column(String(6), nullable=False, comment="게시판유형코드")
    reply_posbl_at = Column(String(1), nullable=False, default='N', comment="답장가능여부")
    file_atch_posbl_at = Column(String(1), nullable=False, default='N', comment="파일첨부가능여부")
    atch_posbl_file_size = Column(Numeric(8), nullable=True, comment="첨부가능파일사이즈")
    use_at = Column(String(1), nullable=False, default='Y', comment="사용여부")
    delete_at = Column(String(1), nullable=False, default='N', comment="삭제여부")
    
    # 공통 필드
    frst_register_id = Column(String(20), nullable=False, comment="최초등록자ID")
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    
    # 관계 설정
    bbs_posts = relationship("Bbs", back_populates="bbs_master")
    
    def __repr__(self):
        return f"<BbsMaster(bbs_id='{self.bbs_id}', bbs_nm='{self.bbs_nm}')>"


class Bbs(Base):
    """게시판 테이블 모델
    
    게시판의 게시물 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_bbs"
    __table_args__ = (
        Index('ix_bbs_01', 'bbs_id'),
        {
            'schema': 'skybootcore',
            'comment': '게시판'
        }
    )
    
    # 기본 필드 (복합 기본키)
    ntt_id = Column(Numeric(20), primary_key=True, comment="게시물ID")
    bbs_id = Column(String(30), ForeignKey('skybootcore.tb_bbsmaster.bbs_id'), 
                   primary_key=True, comment="게시판ID")
    ntt_no = Column(Numeric(20), nullable=True, comment="게시물번호")
    ntt_sj = Column(String(2000), nullable=True, comment="게시물제목")
    ntt_cn = Column(Text, nullable=True, comment="게시물내용")
    answer_at = Column(String(1), nullable=True, comment="댓글여부")
    parntsctt_no = Column(Numeric(10), nullable=True, comment="부모글번호")
    answer_lc = Column(Numeric(8), nullable=True, comment="댓글위치")
    sort_ordr = Column(Numeric(8), nullable=True, comment="정렬순서")
    rdcnt = Column(Numeric(10), nullable=True, default=0, comment="조회수")
    use_at = Column(String(1), nullable=False, default='Y', comment="사용여부")
    ntce_bgnde = Column(String(20), nullable=True, comment="게시시작일")
    ntce_endde = Column(String(20), nullable=True, comment="게시종료일")
    ntcr_id = Column(String(20), nullable=True, comment="게시자ID")
    ntcr_nm = Column(String(20), nullable=True, comment="게시자명")
    password = Column(String(200), nullable=True, comment="비밀번호")
    atch_file_id = Column(String(20), nullable=True, comment="첨부파일ID")
    notice_at = Column(String(1), nullable=True, comment="공지사항여부")
    sj_bold_at = Column(String(1), nullable=True, comment="제목볼드여부")
    secret_at = Column(String(1), nullable=True, comment="비밀글여부")
    blog_id = Column(String(20), nullable=True, comment="블로그 ID")
    delete_at = Column(String(1), nullable=True, comment="삭제여부")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=False, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    bbs_master = relationship("BbsMaster", back_populates="bbs_posts")
    comments = relationship("Comment", back_populates="bbs_post",
                          primaryjoin="and_(Bbs.ntt_id==Comment.ntt_id, Bbs.bbs_id==Comment.bbs_id)")
    
    def __repr__(self):
        return f"<Bbs(ntt_id={self.ntt_id}, bbs_id='{self.bbs_id}', ntt_sj='{self.ntt_sj}')>"


class Comment(Base):
    """댓글 테이블 모델
    
    게시물의 댓글 정보를 관리하는 테이블입니다.
    """
    __tablename__ = "tb_comment"
    __table_args__ = (
        Index('ix_comment_01', 'ntt_id', 'bbs_id'),
        ForeignKeyConstraint(['ntt_id', 'bbs_id'], ['skybootcore.tb_bbs.ntt_id', 'skybootcore.tb_bbs.bbs_id']),
        {
            'schema': 'skybootcore',
            'comment': '댓글'
        }
    )
    
    # 기본 필드 (복합 기본키)
    ntt_id = Column(Numeric(20), primary_key=True, comment="게시물ID")
    bbs_id = Column(String(30), primary_key=True, comment="게시판ID")
    answer_no = Column(Numeric(20), primary_key=True, comment="댓글번호")
    wrter_id = Column(String(20), nullable=True, comment="작성자ID")
    wrter_nm = Column(String(20), nullable=True, comment="작성자명")
    answer = Column(String(2000), nullable=True, comment="댓글")
    use_at = Column(String(1), nullable=False, default='Y', comment="사용여부")
    password = Column(String(200), nullable=True, comment="비밀번호")
    
    # 공통 필드
    frst_regist_pnttm = Column(DateTime, nullable=False, default=datetime.now, comment="최초등록시점")
    frst_register_id = Column(String(20), nullable=True, comment="최초등록자ID")
    last_updt_pnttm = Column(DateTime, nullable=True, comment="최종수정시점")
    last_updusr_id = Column(String(20), nullable=True, comment="최종수정자ID")
    
    # 관계 설정
    bbs_post = relationship("Bbs", back_populates="comments",
                          primaryjoin="and_(Comment.ntt_id==Bbs.ntt_id, Comment.bbs_id==Bbs.bbs_id)")
    
    def __repr__(self):
        return f"<Comment(ntt_id={self.ntt_id}, bbs_id='{self.bbs_id}', answer_no={self.answer_no})>"
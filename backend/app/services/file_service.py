"""파일 관련 서비스

파일 및 파일 상세 정보 관리를 위한 서비스 클래스들을 정의합니다.
"""

from typing import List, Optional, Dict, Any, BinaryIO
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime
import logging
import os
import uuid
import mimetypes
from pathlib import Path

from app.models.file_models import File, FileDetail
from app.schemas.file_schemas import (
    FileCreate, FileUpdate,
    FileDetailCreate, FileDetailUpdate
)
from .base_service import BaseService

logger = logging.getLogger(__name__)


class FileService(BaseService[File, FileCreate, FileUpdate]):
    """파일 서비스
    
    파일 업로드, 다운로드, 관리 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(File)
        self.upload_path = "uploads"  # 기본 업로드 경로
    
    def get_by_atch_file_id(self, db: Session, atch_file_id: str) -> Optional[File]:
        """
        첨부파일 ID로 파일 정보 조회
        
        Args:
            db: 데이터베이스 세션
            atch_file_id: 첨부파일 ID
            
        Returns:
            파일 정보 또는 None
        """
        try:
            return db.query(File).filter(
                and_(
                    File.atch_file_id == atch_file_id,
                    File.delete_at == 'N'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 파일 조회 실패 - atch_file_id: {atch_file_id}, 오류: {str(e)}")
            raise
    
    def create_file_group(
        self, 
        db: Session, 
        file_group_data: Dict[str, Any],
        user_id: str = 'system'
    ) -> File:
        """
        파일 그룹 생성
        
        Args:
            db: 데이터베이스 세션
            file_group_data: 파일 그룹 데이터
            user_id: 생성자 ID
            
        Returns:
            생성된 파일 그룹 정보
        """
        try:
            # 새로운 첨부파일 ID 생성
            atch_file_id = str(uuid.uuid4())
            
            file_data = {
                'atch_file_id': atch_file_id,
                'creat_dt': datetime.now(),
                'use_at': file_group_data.get('use_at', 'Y'),
                'frst_register_id': user_id
            }
            
            file_group = self.create(db, file_data)
            logger.info(f"✅ 파일 그룹 생성 완료 - atch_file_id: {atch_file_id}")
            return file_group
            
        except Exception as e:
            logger.error(f"❌ 파일 그룹 생성 실패 - 오류: {str(e)}")
            raise
    
    def get_file_statistics(self, db: Session) -> Dict[str, Any]:
        """
        파일 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            파일 통계 정보
        """
        try:
            # 전체 파일 그룹 수
            total_groups = db.query(File).filter(File.delete_at == 'N').count()
            
            # 활성 파일 그룹 수
            active_groups = db.query(File).filter(
                and_(
                    File.use_at == 'Y',
                    File.delete_at == 'N'
                )
            ).count()
            
            # 전체 파일 수 (FileDetail 기준)
            total_files = db.query(FileDetail).filter(
                FileDetail.delete_at == 'N'
            ).count()
            
            # 전체 파일 크기
            total_size = db.query(
                func.sum(FileDetail.file_size)
            ).filter(
                FileDetail.delete_at == 'N'
            ).scalar() or 0
            
            return {
                'total_groups': total_groups,
                'active_groups': active_groups,
                'inactive_groups': total_groups - active_groups,
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"❌ 파일 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_file_groups(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """
        파일 그룹 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어
            start_date: 시작 날짜
            end_date: 종료 날짜
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 파일 그룹 목록
        """
        try:
            query = db.query(File).filter(File.delete_at == 'N')
            
            # 날짜 범위 조건
            if start_date:
                query = query.filter(File.creat_dt >= start_date)
            if end_date:
                query = query.filter(File.creat_dt <= end_date)
            
            # 검색어 조건 (첨부파일 ID 또는 생성자)
            if search_term:
                search_filter = or_(
                    File.atch_file_id.like(f"%{search_term}%"),
                    File.frst_register_id.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            return query.order_by(desc(File.creat_dt)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 파일 그룹 검색 실패 - 오류: {str(e)}")
            raise


class FileDetailService(BaseService[FileDetail, FileDetailCreate, FileDetailUpdate]):
    """파일 상세 서비스
    
    개별 파일의 상세 정보 관리를 위한 서비스입니다.
    """
    
    def __init__(self):
        super().__init__(FileDetail)
        self.upload_path = "uploads"
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'],
            'archive': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg']
        }
        self.max_file_size = 100 * 1024 * 1024  # 100MB
    
    def get_by_file_sn(self, db: Session, file_sn: int) -> Optional[FileDetail]:
        """
        파일 일련번호로 파일 상세 정보 조회
        
        Args:
            db: 데이터베이스 세션
            file_sn: 파일 일련번호
            
        Returns:
            파일 상세 정보 또는 None
        """
        try:
            return db.query(FileDetail).filter(
                and_(
                    FileDetail.file_sn == file_sn,
                    FileDetail.delete_at == 'N'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 파일 상세 조회 실패 - file_sn: {file_sn}, 오류: {str(e)}")
            raise
    
    def get_files_by_group(
        self, 
        db: Session, 
        atch_file_id: str
    ) -> List[FileDetail]:
        """
        첨부파일 ID로 파일 목록 조회
        
        Args:
            db: 데이터베이스 세션
            atch_file_id: 첨부파일 ID
            
        Returns:
            해당 그룹의 파일 목록
        """
        try:
            return db.query(FileDetail).filter(
                and_(
                    FileDetail.atch_file_id == atch_file_id,
                    FileDetail.delete_at == 'N'
                )
            ).order_by(FileDetail.file_sn).all()
        except Exception as e:
            logger.error(f"❌ 그룹별 파일 목록 조회 실패 - atch_file_id: {atch_file_id}, 오류: {str(e)}")
            raise
    
    def upload_file(
        self, 
        db: Session, 
        atch_file_id: str,
        file_data: BinaryIO,
        original_filename: str,
        user_id: str = 'system'
    ) -> FileDetail:
        """
        파일 업로드
        
        Args:
            db: 데이터베이스 세션
            atch_file_id: 첨부파일 ID
            file_data: 파일 데이터
            original_filename: 원본 파일명
            user_id: 업로드 사용자 ID
            
        Returns:
            업로드된 파일 상세 정보
        """
        try:
            # 파일 확장자 및 크기 검증
            file_ext = Path(original_filename).suffix.lower()
            if not self._is_allowed_extension(file_ext):
                raise ValueError(f"허용되지 않는 파일 확장자입니다: {file_ext}")
            
            # 파일 크기 확인
            file_data.seek(0, 2)  # 파일 끝으로 이동
            file_size = file_data.tell()
            file_data.seek(0)  # 파일 시작으로 이동
            
            if file_size > self.max_file_size:
                raise ValueError(f"파일 크기가 너무 큽니다. 최대 {self.max_file_size // (1024*1024)}MB")
            
            # 저장할 파일명 생성
            stored_filename = f"{uuid.uuid4()}{file_ext}"
            file_path = os.path.join(self.upload_path, stored_filename)
            
            # 디렉토리 생성
            os.makedirs(self.upload_path, exist_ok=True)
            
            # 파일 저장
            with open(file_path, 'wb') as f:
                f.write(file_data.read())
            
            # MIME 타입 추정
            mime_type, _ = mimetypes.guess_type(original_filename)
            
            # 다음 파일 일련번호 조회
            max_sn = db.query(func.max(FileDetail.file_sn)).filter(
                FileDetail.atch_file_id == atch_file_id
            ).scalar() or 0
            
            # 파일 상세 정보 생성
            file_detail_data = {
                'atch_file_id': atch_file_id,
                'file_sn': max_sn + 1,
                'file_stre_cours': file_path,
                'stre_file_nm': stored_filename,
                'orignl_file_nm': original_filename,
                'file_extsn': file_ext,
                'file_size': file_size,
                'file_mime_type': mime_type,
                'frst_register_id': user_id
            }
            
            file_detail = self.create(db, file_detail_data)
            logger.info(f"✅ 파일 업로드 완료 - 파일명: {original_filename}, 크기: {file_size}bytes")
            return file_detail
            
        except Exception as e:
            # 업로드 실패 시 파일 삭제
            if 'file_path' in locals() and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
            
            logger.error(f"❌ 파일 업로드 실패 - 파일명: {original_filename}, 오류: {str(e)}")
            raise
    
    def download_file(self, db: Session, file_sn: int) -> Optional[Dict[str, Any]]:
        """
        파일 다운로드 정보 조회
        
        Args:
            db: 데이터베이스 세션
            file_sn: 파일 일련번호
            
        Returns:
            파일 다운로드 정보 또는 None
        """
        try:
            file_detail = self.get_by_file_sn(db, file_sn)
            if not file_detail:
                return None
            
            # 파일 존재 확인
            if not os.path.exists(file_detail.file_stre_cours):
                logger.error(f"❌ 파일이 존재하지 않음 - 경로: {file_detail.file_stre_cours}")
                return None
            
            # 다운로드 수 증가
            file_detail.dwld_co = (file_detail.dwld_co or 0) + 1
            file_detail.last_updt_pnttm = datetime.now()
            db.add(file_detail)
            db.commit()
            
            return {
                'file_path': file_detail.file_stre_cours,
                'original_filename': file_detail.orignl_file_nm,
                'file_size': file_detail.file_size,
                'mime_type': file_detail.file_mime_type
            }
            
        except Exception as e:
            logger.error(f"❌ 파일 다운로드 정보 조회 실패 - file_sn: {file_sn}, 오류: {str(e)}")
            raise
    
    def delete_file(self, db: Session, file_sn: int, user_id: str = 'system') -> bool:
        """
        파일 삭제 (물리적 파일도 함께 삭제)
        
        Args:
            db: 데이터베이스 세션
            file_sn: 파일 일련번호
            user_id: 삭제 사용자 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            file_detail = self.get_by_file_sn(db, file_sn)
            if not file_detail:
                return False
            
            # 물리적 파일 삭제
            if os.path.exists(file_detail.file_stre_cours):
                try:
                    os.remove(file_detail.file_stre_cours)
                    logger.info(f"✅ 물리적 파일 삭제 완료 - 경로: {file_detail.file_stre_cours}")
                except Exception as e:
                    logger.warning(f"⚠️ 물리적 파일 삭제 실패 - 경로: {file_detail.file_stre_cours}, 오류: {str(e)}")
            
            # 논리적 삭제
            file_detail.delete_at = 'Y'
            file_detail.last_updusr_id = user_id
            file_detail.last_updt_pnttm = datetime.now()
            
            db.add(file_detail)
            db.commit()
            
            logger.info(f"✅ 파일 삭제 완료 - file_sn: {file_sn}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 파일 삭제 실패 - file_sn: {file_sn}, 오류: {str(e)}")
            raise
    
    def search_files(
        self, 
        db: Session, 
        atch_file_id: Optional[str] = None,
        search_term: Optional[str] = None,
        file_type: Optional[str] = None,
        min_size: Optional[int] = None,
        max_size: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[FileDetail]:
        """
        파일 검색
        
        Args:
            db: 데이터베이스 세션
            atch_file_id: 첨부파일 ID
            search_term: 검색어 (파일명)
            file_type: 파일 유형 (image, document, archive, video, audio)
            min_size: 최소 파일 크기
            max_size: 최대 파일 크기
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 파일 목록
        """
        try:
            query = db.query(FileDetail).filter(FileDetail.delete_at == 'N')
            
            # 첨부파일 ID 조건
            if atch_file_id:
                query = query.filter(FileDetail.atch_file_id == atch_file_id)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    FileDetail.orignl_file_nm.like(f"%{search_term}%"),
                    FileDetail.stre_file_nm.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # 파일 유형 조건
            if file_type and file_type in self.allowed_extensions:
                extensions = self.allowed_extensions[file_type]
                ext_filter = or_(*[FileDetail.file_extsn == ext for ext in extensions])
                query = query.filter(ext_filter)
            
            # 파일 크기 조건
            if min_size:
                query = query.filter(FileDetail.file_size >= min_size)
            if max_size:
                query = query.filter(FileDetail.file_size <= max_size)
            
            return query.order_by(desc(FileDetail.frst_regist_pnttm)).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 파일 검색 실패 - 오류: {str(e)}")
            raise
    
    def get_file_statistics_by_type(self, db: Session) -> Dict[str, Any]:
        """
        파일 유형별 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            파일 유형별 통계 정보
        """
        try:
            statistics = {}
            
            for file_type, extensions in self.allowed_extensions.items():
                # 해당 유형의 파일 수와 총 크기 조회
                ext_filter = or_(*[FileDetail.file_extsn == ext for ext in extensions])
                
                count = db.query(FileDetail).filter(
                    and_(
                        FileDetail.delete_at == 'N',
                        ext_filter
                    )
                ).count()
                
                total_size = db.query(
                    func.sum(FileDetail.file_size)
                ).filter(
                    and_(
                        FileDetail.delete_at == 'N',
                        ext_filter
                    )
                ).scalar() or 0
                
                statistics[file_type] = {
                    'count': count,
                    'total_size_bytes': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2)
                }
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ 파일 유형별 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def _is_allowed_extension(self, file_ext: str) -> bool:
        """
        허용된 파일 확장자인지 확인
        
        Args:
            file_ext: 파일 확장자
            
        Returns:
            허용 여부
        """
        for extensions in self.allowed_extensions.values():
            if file_ext in extensions:
                return True
        return False
    
    def cleanup_orphaned_files(self, db: Session) -> Dict[str, int]:
        """
        고아 파일 정리 (DB에는 없지만 물리적으로 존재하는 파일들)
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            정리 결과 통계
        """
        try:
            if not os.path.exists(self.upload_path):
                return {'deleted_files': 0, 'total_size_freed': 0}
            
            # DB에 등록된 파일명 목록 조회
            db_files = set(
                db.query(FileDetail.stre_file_nm).filter(
                    FileDetail.delete_at == 'N'
                ).all()
            )
            db_filenames = {item[0] for item in db_files}
            
            # 물리적으로 존재하는 파일 목록
            physical_files = set(os.listdir(self.upload_path))
            
            # 고아 파일 찾기
            orphaned_files = physical_files - db_filenames
            
            deleted_count = 0
            total_size_freed = 0
            
            for filename in orphaned_files:
                file_path = os.path.join(self.upload_path, filename)
                try:
                    file_size = os.path.getsize(file_path)
                    os.remove(file_path)
                    deleted_count += 1
                    total_size_freed += file_size
                    logger.info(f"✅ 고아 파일 삭제 - {filename}")
                except Exception as e:
                    logger.warning(f"⚠️ 고아 파일 삭제 실패 - {filename}: {str(e)}")
            
            logger.info(f"✅ 고아 파일 정리 완료 - 삭제된 파일: {deleted_count}개, 확보된 용량: {total_size_freed}bytes")
            
            return {
                'deleted_files': deleted_count,
                'total_size_freed': total_size_freed,
                'total_size_freed_mb': round(total_size_freed / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"❌ 고아 파일 정리 실패 - 오류: {str(e)}")
            raise
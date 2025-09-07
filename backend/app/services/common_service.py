"""공통 코드 관련 서비스

공통 그룹 코드 및 공통 코드 관리를 위한 서비스 클래스들을 정의합니다.
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_, desc, asc
from datetime import datetime
import logging

from app.models.common_models import CmmnGrpCode, CmmnCode
from app.schemas.common_schemas import (
    CmmnGrpCodeCreate, CmmnGrpCodeUpdate,
    CmmnCodeCreate, CmmnCodeUpdate
)
from .base_service import BaseService

logger = logging.getLogger(__name__)


class CmmnGrpCodeService(BaseService[CmmnGrpCode, CmmnGrpCodeCreate, CmmnGrpCodeUpdate]):
    """공통 그룹 코드 서비스
    
    공통 코드의 그룹 관리를 위한 서비스입니다.
    """
    
    def __init__(self):
        super().__init__(CmmnGrpCode)
    
    def get_by_group_id(self, db: Session, group_id: str) -> Optional[CmmnGrpCode]:
        """
        그룹 ID로 공통 그룹 코드 조회
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            
        Returns:
            공통 그룹 코드 정보 또는 None
        """
        try:
            return db.query(CmmnGrpCode).filter(
                and_(
                    CmmnGrpCode.group_id == group_id,
                    CmmnGrpCode.use_at == 'Y',
                    CmmnGrpCode.delete_at == 'N'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 공통 그룹 코드 조회 실패 - group_id: {group_id}, 오류: {str(e)}")
            raise
    
    def get_active_group_codes(self, db: Session) -> List[CmmnGrpCode]:
        """
        활성화된 공통 그룹 코드 목록 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            활성화된 공통 그룹 코드 목록
        """
        try:
            return db.query(CmmnGrpCode).filter(
                CmmnGrpCode.use_yn == 'Y'
            ).order_by(CmmnGrpCode.code_id).all()
        except Exception as e:
            logger.error(f"❌ 활성 공통 그룹 코드 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_group_codes(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        use_yn: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CmmnGrpCode]:
        """
        공통 그룹 코드 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어 (그룹ID, 그룹명)
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 공통 그룹 코드 목록
        """
        try:
            query = db.query(CmmnGrpCode)
            
            # 기본 조건 (활성 그룹만)
            query = query.filter(CmmnGrpCode.use_yn == 'Y')
            
            # 사용 여부 조건
            if use_yn:
                query = query.filter(CmmnGrpCode.use_yn == use_yn)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    CmmnGrpCode.code_id.like(f"%{search_term}%"),
                    CmmnGrpCode.code_id_nm.like(f"%{search_term}%"),
                    CmmnGrpCode.code_id_dc.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            return query.order_by(CmmnGrpCode.code_id).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 공통 그룹 코드 검색 실패 - 오류: {str(e)}")
            raise
    
    def get_by_group_code_id(self, db: Session, group_code_id: str) -> Optional[CmmnGrpCode]:
        """
        그룹 코드 ID로 공통 그룹 코드 조회
        
        Args:
            db: 데이터베이스 세션
            group_code_id: 그룹 코드 ID
            
        Returns:
            공통 그룹 코드 정보 또는 None
        """
        try:
            return db.query(CmmnGrpCode).filter(
                CmmnGrpCode.code_id == group_code_id
            ).first()
        except Exception as e:
            logger.error(f"❌ 공통 그룹 코드 조회 실패 - group_code_id: {group_code_id}, 오류: {str(e)}")
            raise
    
    def get_group_code_statistics(self, db: Session) -> Dict[str, Any]:
        """
        공통 그룹 코드 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            그룹 코드 통계 정보
        """
        try:
            total_groups = db.query(CmmnGrpCode).count()
            active_groups = db.query(CmmnGrpCode).filter(
                CmmnGrpCode.use_yn == 'Y'
            ).count()
            inactive_groups = total_groups - active_groups
            
            # 전체 코드 수 계산
            total_codes = db.query(CmmnCode).count()
            avg_codes_per_group = total_codes / total_groups if total_groups > 0 else 0
            
            return {
                "total_groups": total_groups,
                "active_groups": active_groups,
                "inactive_groups": inactive_groups,
                "total_codes": total_codes,
                "avg_codes_per_group": round(avg_codes_per_group, 2)
            }
        except Exception as e:
            logger.error(f"❌ 공통 그룹 코드 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def create_group_code(self, db: Session, group_data: dict, user_id: str) -> CmmnGrpCode:
        """
        새로운 공통 그룹 코드 생성
        
        Args:
            db: 데이터베이스 세션
            group_data: 그룹 코드 생성 데이터
            user_id: 생성자 ID
            
        Returns:
            생성된 공통 그룹 코드
        """
        try:
            new_group = CmmnGrpCode(
                code_id=group_data['code_id'],
                code_id_nm=group_data.get('code_id_nm', ''),
                code_id_dc=group_data.get('code_id_dc', ''),
                use_yn=group_data.get('use_yn', 'Y'),
                cl_code=group_data.get('cl_code', ''),
                frst_register_id=user_id,
                frst_regist_pnttm=datetime.now(),
                last_updusr_id=user_id,
                last_updt_pnttm=datetime.now()
            )
            
            db.add(new_group)
            db.commit()
            db.refresh(new_group)
            
            logger.info(f"✅ 공통 그룹 코드 생성 완료 - code_id: {new_group.code_id}")
            return new_group
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 그룹 코드 생성 실패 - 오류: {str(e)}")
            raise
    
    def update_group_code(self, db: Session, group_code_id: str, update_data: dict, user_id: str) -> Optional[CmmnGrpCode]:
        """
        공통 그룹 코드 수정
        
        Args:
            db: 데이터베이스 세션
            group_code_id: 그룹 코드 ID
            update_data: 수정할 데이터
            user_id: 수정자 ID
            
        Returns:
            수정된 공통 그룹 코드 또는 None
        """
        try:
            group = self.get_by_group_code_id(db, group_code_id)
            if not group:
                return None
            
            # 수정 가능한 필드만 업데이트
            if 'code_id_nm' in update_data:
                group.code_id_nm = update_data['code_id_nm']
            if 'code_id_dc' in update_data:
                group.code_id_dc = update_data['code_id_dc']
            if 'use_yn' in update_data:
                group.use_yn = update_data['use_yn']
            if 'cl_code' in update_data:
                group.cl_code = update_data['cl_code']
            
            group.last_updusr_id = user_id
            group.last_updt_pnttm = datetime.now()
            
            db.commit()
            db.refresh(group)
            
            logger.info(f"✅ 공통 그룹 코드 수정 완료 - group_code: {group_code_id}")
            return group
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 그룹 코드 수정 실패 - group_code: {group_code_id}, 오류: {str(e)}")
            raise
    
    def delete_group_code(self, db: Session, group_code_id: str, user_id: str) -> bool:
        """
        공통 그룹 코드 삭제 (논리 삭제)
        
        Args:
            db: 데이터베이스 세션
            group_code_id: 그룹 코드 ID
            user_id: 삭제자 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            group = self.get_by_group_code_id(db, group_code_id)
            if not group:
                return False
            
            group.use_yn = 'N'
            group.last_updusr_id = user_id
            group.last_updt_pnttm = datetime.now()
            
            db.commit()
            
            logger.info(f"✅ 공통 그룹 코드 삭제 완료 - group_code: {group_code_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 그룹 코드 삭제 실패 - group_code: {group_code_id}, 오류: {str(e)}")
            raise
    
    def create_group_with_codes(
        self, 
        db: Session, 
        group_data: CmmnGrpCodeCreate,
        codes_data: List[CmmnCodeCreate]
    ) -> Tuple[CmmnGrpCode, List[CmmnCode]]:
        """
        공통 그룹 코드와 하위 코드들을 함께 생성
        
        Args:
            db: 데이터베이스 세션
            group_data: 그룹 생성 데이터
            codes_data: 하위 코드 생성 데이터 목록
            
        Returns:
            생성된 그룹과 코드들의 튜플
        """
        try:
            # 그룹 생성
            group = self.create_group_code(db, group_data.dict(), group_data.frst_register_id)
            
            # 하위 코드들 생성
            code_service = CmmnCodeService()
            
            created_codes = []
            for code_data in codes_data:
                code_dict = code_data.dict()
                code_dict['code_id'] = group.code_id
                created_code = code_service.create_code(db, code_dict, group_data.frst_register_id)
                created_codes.append(created_code)
            
            logger.info(f"✅ 그룹과 코드 생성 완료 - code_id: {group.code_id}, 코드 수: {len(created_codes)}")
            return group, created_codes
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 그룹과 코드 생성 실패 - code_id: {group_data.code_id}, 오류: {str(e)}")
            raise
    
    def get_group_statistics(self, db: Session) -> Dict[str, Any]:
        """
        공통 그룹 코드 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            통계 정보 딕셔너리
        """
        try:
            from sqlalchemy import func
            
            # 전체 그룹 수
            total_groups = db.query(CmmnGrpCode).filter(
                CmmnGrpCode.delete_at == 'N'
            ).count()
            
            # 활성 그룹 수
            active_groups = db.query(CmmnGrpCode).filter(
                CmmnGrpCode.use_at == 'Y'
            ).count()
            
            # 그룹별 코드 수
            group_code_counts = db.query(
                CmmnGrpCode.group_id,
                CmmnGrpCode.group_nm,
                func.count(CmmnCode.code_id).label('code_count')
            ).outerjoin(
                CmmnCode, 
                and_(
                    CmmnGrpCode.group_id == CmmnCode.group_id,
                    CmmnCode.use_at == 'Y'
                )
            ).group_by(
                CmmnGrpCode.group_id, 
                CmmnGrpCode.group_nm
            ).all()
            
            return {
                'total_groups': total_groups,
                'active_groups': active_groups,
                'inactive_groups': total_groups - active_groups,
                'group_code_counts': [
                    {
                        'group_id': item.group_id,
                        'group_nm': item.group_nm,
                        'code_count': item.code_count
                    }
                    for item in group_code_counts
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ 공통 그룹 코드 통계 조회 실패 - 오류: {str(e)}")
            raise


class CmmnCodeService(BaseService[CmmnCode, CmmnCodeCreate, CmmnCodeUpdate]):
    """공통 코드 서비스
    
    공통 코드 관리를 위한 서비스입니다.
    """
    
    def __init__(self):
        super().__init__(CmmnCode)
    
    def get_by_code_id(self, db: Session, group_id: str, code_id: str) -> Optional[CmmnCode]:
        """
        그룹 ID와 코드 ID로 공통 코드 조회
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            code_id: 코드 ID
            
        Returns:
            공통 코드 정보 또는 None
        """
        try:
            return db.query(CmmnCode).filter(
                and_(
                    CmmnCode.code_id == group_id,
                    CmmnCode.code == code_id,
                    CmmnCode.use_yn == 'Y'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 공통 코드 조회 실패 - group_id: {group_id}, code_id: {code_id}, 오류: {str(e)}")
            raise
    
    def get_codes_by_group(self, db: Session, group_code_id: str) -> List[CmmnCode]:
        """
        그룹 ID로 공통 코드 목록 조회
        
        Args:
            db: 데이터베이스 세션
            group_code_id: 그룹 코드 ID
            
        Returns:
            해당 그룹의 공통 코드 목록
        """
        try:
            return db.query(CmmnCode).filter(
                and_(
                    CmmnCode.code_id == group_code_id,
                    CmmnCode.use_yn == 'Y'
                )
            ).order_by(CmmnCode.code_ordr, CmmnCode.code).all()
        except Exception as e:
            logger.error(f"❌ 그룹별 공통 코드 조회 실패 - group_code_id: {group_code_id}, 오류: {str(e)}")
            raise
    
    def get_active_codes(self, db: Session) -> List[CmmnCode]:
        """
        활성화된 공통 코드 목록 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            활성화된 공통 코드 목록
        """
        try:
            return db.query(CmmnCode).filter(
                CmmnCode.use_yn == 'Y'
            ).order_by(CmmnCode.code_id, CmmnCode.code_ordr, CmmnCode.code).all()
        except Exception as e:
            logger.error(f"❌ 활성 공통 코드 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def search_codes(
        self, 
        db: Session, 
        group_id: Optional[str] = None,
        search_term: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CmmnCode]:
        """
        공통 코드 검색
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            search_term: 검색어 (코드ID, 코드명)
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 공통 코드 목록
        """
        try:
            query = db.query(CmmnCode)
            
            # 기본 조건 (활성 코드만)
            query = query.filter(CmmnCode.use_yn == 'Y')
            
            # 그룹 조건
            if group_id:
                query = query.filter(CmmnCode.code_id == group_id)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    CmmnCode.code.like(f"%{search_term}%"),
                    CmmnCode.code_nm.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            return query.order_by(
                CmmnCode.code_id, 
                CmmnCode.code_ordr, 
                CmmnCode.code
            ).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 공통 코드 검색 실패 - 오류: {str(e)}")
            raise
    
    def get_code_value(self, db: Session, group_id: str, code_id: str) -> Optional[str]:
        """
        공통 코드의 코드명 조회
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            code_id: 코드 ID
            
        Returns:
            코드명 또는 None
        """
        try:
            code = self.get_by_code_id(db, group_id, code_id)
            return code.code_nm if code else None
        except Exception as e:
            logger.error(f"❌ 공통 코드 값 조회 실패 - group_id: {group_id}, code_id: {code_id}, 오류: {str(e)}")
            raise
    
    def get_codes_as_dict(self, db: Session, group_id: str) -> Dict[str, str]:
        """
        그룹의 공통 코드를 딕셔너리 형태로 조회
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            
        Returns:
            {code_id: code_nm} 형태의 딕셔너리
        """
        try:
            codes = self.get_codes_by_group(db, group_id)
            return {code.code_id: code.code_nm for code in codes}
        except Exception as e:
            logger.error(f"❌ 공통 코드 딕셔너리 조회 실패 - group_id: {group_id}, 오류: {str(e)}")
            raise
    
    def update_sort_order(
        self, 
        db: Session, 
        group_id: str, 
        code_orders: List[Dict[str, int]]
    ) -> bool:
        """
        공통 코드 정렬 순서 업데이트
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            code_orders: [{"code_id": "CODE1", "sort_ordr": 1}, ...]
            
        Returns:
            업데이트 성공 여부
        """
        try:
            for order_info in code_orders:
                code_id = order_info.get('code_id')
                sort_ordr = order_info.get('sort_ordr')
                
                if not code_id or sort_ordr is None:
                    continue
                
                code = db.query(CmmnCode).filter(
                    and_(
                        CmmnCode.code_id == group_id,
                        CmmnCode.code == code_id
                    )
                ).first()
                
                if code:
                    code.code_ordr = sort_ordr
                    code.last_updt_pnttm = datetime.now()
                    db.add(code)
            
            db.commit()
            logger.info(f"✅ 공통 코드 정렬 순서 업데이트 완료 - group_id: {group_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 코드 정렬 순서 업데이트 실패 - group_id: {group_id}, 오류: {str(e)}")
            raise
    
    def get_code_statistics(self, db: Session, group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        공통 코드 통계 조회
        
        Args:
            db: 데이터베이스 세션
            group_id: 특정 그룹 ID (선택사항)
            
        Returns:
            코드 통계 정보
        """
        try:
            query = db.query(CmmnCode)
            
            if group_id:
                query = query.filter(CmmnCode.code_id == group_id)
            
            total_codes = query.count()
            active_codes = query.filter(CmmnCode.use_yn == 'Y').count()
            inactive_codes = total_codes - active_codes
            
            # 그룹별 코드 수
            group_stats = db.query(
                CmmnCode.code_id,
                func.count(CmmnCode.code).label('code_count')
            ).group_by(CmmnCode.code_id).all()
            
            # 그룹별 코드 수를 딕셔너리로 변환
            codes_by_group = {
                stat.code_id: stat.code_count for stat in group_stats
            }
            
            # 가장 많이 사용된 그룹 찾기
            most_used_group = None
            if group_stats:
                most_used_group = max(group_stats, key=lambda x: x.code_count).code_id
            
            result = {
                "total_codes": total_codes,
                "active_codes": active_codes,
                "inactive_codes": inactive_codes,
                "codes_by_group": codes_by_group,
                "most_used_group": most_used_group
            }
            print(f"📊 DEBUG - 통계 조회 결과: {result}")
            print(f"📊 DEBUG - codes_by_group 타입: {type(codes_by_group)}")
            print(f"📊 DEBUG - codes_by_group 값: {codes_by_group}")
            logger.info(f"📊 통계 조회 결과: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ 공통 코드 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def create_code(self, db: Session, code_data: dict, user_id: str) -> CmmnCode:
        """
        새로운 공통 코드 생성
        
        Args:
            db: 데이터베이스 세션
            code_data: 코드 생성 데이터
            user_id: 생성자 ID
            
        Returns:
            생성된 공통 코드
        """
        try:
            new_code = CmmnCode(
                code_id=code_data['code_id'],
                code=code_data['code'],
                code_nm=code_data['code_nm'],
                code_dc=code_data.get('code_dc', ''),
                code_ordr=code_data.get('code_ordr', 1),
                use_yn=code_data.get('use_yn', 'Y'),
                frst_register_id=user_id,
                frst_regist_pnttm=func.now(),
                last_updusr_id=user_id,
                last_updt_pnttm=func.now()
            )
            
            db.add(new_code)
            db.commit()
            db.refresh(new_code)
            
            logger.info(f"✅ 공통 코드 생성 완료 - group_id: {code_data['code_id']}, code: {new_code.code}")
            return new_code
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 코드 생성 실패 - 오류: {str(e)}")
            raise
    
    def update_code(self, db: Session, group_id: str, code_id: str, update_data: dict, user_id: str) -> Optional[CmmnCode]:
        """
        공통 코드 수정
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            code_id: 코드 ID
            update_data: 수정할 데이터
            user_id: 수정자 ID
            
        Returns:
            수정된 공통 코드 또는 None
        """
        try:
            code = db.query(CmmnCode).filter(
                and_(
                    CmmnCode.code_id == group_id,
                    CmmnCode.code == code_id
                )
            ).first()
            
            if not code:
                return None
            
            # 수정 가능한 필드만 업데이트
            if 'code_nm' in update_data:
                code.code_nm = update_data['code_nm']
            if 'code_dc' in update_data:
                code.code_dc = update_data['code_dc']
            if 'code_ordr' in update_data:
                code.code_ordr = update_data['code_ordr']
            if 'use_yn' in update_data:
                code.use_yn = update_data['use_yn']
            
            code.last_updusr_id = user_id
            code.last_updt_pnttm = func.now()
            
            db.commit()
            db.refresh(code)
            
            logger.info(f"✅ 공통 코드 수정 완료 - group_id: {group_id}, code_id: {code_id}")
            return code
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 코드 수정 실패 - group_id: {group_id}, code_id: {code_id}, 오류: {str(e)}")
            raise
    
    def delete_code(self, db: Session, group_id: str, code_id: str, user_id: str) -> bool:
        """
        공통 코드 삭제 (논리 삭제)
        
        Args:
            db: 데이터베이스 세션
            group_id: 그룹 ID
            code_id: 코드 ID
            user_id: 삭제자 ID
            
        Returns:
            삭제 성공 여부
        """
        try:
            code = db.query(CmmnCode).filter(
                and_(
                    CmmnCode.code_id == group_id,
                    CmmnCode.code == code_id
                )
            ).first()
            
            if not code:
                return False
            
            code.use_yn = 'N'
            code.last_updusr_id = user_id
            code.last_updt_pnttm = func.now()
            
            db.commit()
            
            logger.info(f"✅ 공통 코드 삭제 완료 - group_id: {group_id}, code_id: {code_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 공통 코드 삭제 실패 - group_id: {group_id}, code_id: {code_id}, 오류: {str(e)}")
            raise
    
    def copy_codes_to_group(
        self, 
        db: Session, 
        source_group_id: str, 
        target_group_id: str,
        user_id: str = 'system'
    ) -> List[CmmnCode]:
        """
        한 그룹의 코드들을 다른 그룹으로 복사
        
        Args:
            db: 데이터베이스 세션
            source_group_id: 원본 그룹 ID
            target_group_id: 대상 그룹 ID
            user_id: 복사 실행자 ID
            
        Returns:
            복사된 코드 목록
        """
        try:
            source_codes = self.get_codes_by_group(db, source_group_id)
            copied_codes = []
            
            for source_code in source_codes:
                # 대상 그룹에 동일한 코드 ID가 있는지 확인
                existing_code = self.get_by_code_id(db, target_group_id, source_code.code_id)
                if existing_code:
                    logger.warning(f"⚠️ 코드 복사 건너뜀 (이미 존재) - code_id: {source_code.code_id}")
                    continue
                
                # 새 코드 생성
                code_data = {
                    'code_id': target_group_id,
                    'code': source_code.code,
                    'code_nm': source_code.code_nm,
                    'code_dc': source_code.code_dc,
                    'code_ordr': source_code.code_ordr,
                    'use_yn': source_code.use_yn,
                    'frst_register_id': user_id
                }
                
                copied_code = self.create(db, code_data)
                copied_codes.append(copied_code)
            
            logger.info(f"✅ 코드 복사 완료 - {source_group_id} → {target_group_id}, 복사된 코드 수: {len(copied_codes)}")
            return copied_codes
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 코드 복사 실패 - {source_group_id} → {target_group_id}, 오류: {str(e)}")
            raise
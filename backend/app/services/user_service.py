"""사용자 관련 서비스 로직

사용자 정보, 조직, 우편번호 관련 CRUD 및 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
import uuid
import logging
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.exc import SQLAlchemyError
from app.models.user_models import UserInfo
from app.models.org_models import Org
from app.models.zip_models import Zip
from app.schemas.user_schemas import (
    UserInfoCreate, UserInfoUpdate, UserSearchParams, UserInfoBasicBase,
    OrgCreate, OrgUpdate,
    ZipCreate, ZipUpdate,
    UserStatistics, OrgTreeNode
)
from app.services.base_service import BaseService

# 비밀번호 암호화 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 로거 설정
logger = logging.getLogger(__name__)


class UserInfoService(BaseService[UserInfo, UserInfoCreate, UserInfoUpdate]):
    """사용자 정보 서비스 클래스"""
    
    def __init__(self):
        super().__init__(UserInfo)
    
    def create(self, db: Session, obj_in: Union[UserInfoCreate, UserInfoBasicBase], current_user_id: Optional[str] = None) -> UserInfo:
        """사용자 정보 생성"""
        # 중복 사용자 ID 확인
        existing_user = db.query(UserInfo).filter(UserInfo.user_id == obj_in.user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 사용자 ID입니다."
            )
        
        # 이메일 중복 확인 (UserInfoCreate의 경우에만)
        if hasattr(obj_in, 'email_adres') and obj_in.email_adres:
            existing_email = db.query(UserInfo).filter(UserInfo.email_adres == obj_in.email_adres).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 이메일 주소입니다."
                )
        
        # 비밀번호 암호화
        obj_data = obj_in.model_dump()
        if obj_data.get("password"):
            obj_data["password"] = pwd_context.hash(obj_data["password"])
        
        # 주민등록번호 암호화 (실제 환경에서는 더 강력한 암호화 필요)
        if obj_data.get("ihidnum"):
            obj_data["ihidnum"] = pwd_context.hash(obj_data["ihidnum"])
        
        # 기본값 설정
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        obj_data["sbscrb_de"] = datetime.now()
        obj_data["lock_at"] = "N"
        obj_data["lock_cnt"] = Decimal(0)
        
        # esntl_id가 없거나 비어있는 경우 UUID 자동 생성
        if not obj_data.get("esntl_id"):
            obj_data["esntl_id"] = str(uuid.uuid4())[:20]  # UUID 생성 후 20자로 제한
        
        # UserInfoBasicBase의 경우 필수 필드 기본값 설정
        if isinstance(obj_in, UserInfoBasicBase):
            obj_data["emplyr_sttus_code"] = "P"  # 기본 상태코드 설정
        
        db_obj = UserInfo(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        db_obj: UserInfo,
        obj_in: UserInfoUpdate,
        current_user_id: Optional[str] = None
    ) -> UserInfo:
        """사용자 정보 수정"""
        obj_data = obj_in.model_dump(exclude_unset=True)
        
        # 이메일 중복 확인 (다른 사용자와 중복되지 않는지)
        if "email_adres" in obj_data and obj_data["email_adres"]:
            existing_email = db.query(UserInfo).filter(
                and_(
                    UserInfo.email_adres == obj_data["email_adres"],
                    UserInfo.user_id != db_obj.user_id
                )
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 존재하는 이메일 주소입니다."
                )
        
        # 비밀번호 변경 시 암호화
        if "password" in obj_data and obj_data["password"]:
            obj_data["password"] = pwd_context.hash(obj_data["password"])
            obj_data["chg_pwd_last_pnttm"] = datetime.now()
        
        # 주민등록번호 변경 시 암호화
        if "ihidnum" in obj_data and obj_data["ihidnum"]:
            obj_data["ihidnum"] = pwd_context.hash(obj_data["ihidnum"])
        
        # 수정 정보 업데이트
        obj_data["last_updt_pnttm"] = datetime.now()
        obj_data["last_updusr_id"] = current_user_id
        
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, user_id: str) -> Optional[UserInfo]:
        """
        사용자 정보 삭제 (물리적 삭제)
        
        Args:
            db: 데이터베이스 세션
            user_id: 삭제할 사용자 ID
            
        Returns:
            삭제된 사용자 인스턴스 또는 None
        """
        try:
            obj = db.query(UserInfo).filter(UserInfo.user_id == user_id).first()
            if obj:
                db.delete(obj)
                db.commit()
                return obj
            return None
            
        except Exception as e:
            db.rollback()
            raise
    
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[UserInfo]:
        """사용자 ID로 사용자 정보 조회"""
        return db.query(UserInfo).filter(UserInfo.user_id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[UserInfo]:
        """이메일로 사용자 정보 조회"""
        return db.query(UserInfo).filter(UserInfo.email_adres == email).first()
    
    def search_users(self, db: Session, search_params: UserSearchParams, skip: int = 0, limit: int = 100) -> tuple[List[UserInfo], int]:
        """사용자 검색"""
        query = db.query(UserInfo)
        
        # 검색 조건 적용
        if search_params.user_nm:
            query = query.filter(UserInfo.user_nm.ilike(f"%{search_params.user_nm}%"))
        
        if search_params.orgnzt_id:
            query = query.filter(UserInfo.orgnzt_id == search_params.orgnzt_id)
        
        if search_params.emplyr_sttus_code:
            query = query.filter(UserInfo.emplyr_sttus_code == search_params.emplyr_sttus_code)
        
        if search_params.email_adres:
            query = query.filter(UserInfo.email_adres.ilike(f"%{search_params.email_adres}%"))
        
        if search_params.group_id:
            query = query.filter(UserInfo.group_id == search_params.group_id)
        
        if search_params.lock_at:
            query = query.filter(UserInfo.lock_at == search_params.lock_at)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        users = query.order_by(desc(UserInfo.frst_regist_pnttm)).offset(skip).limit(limit).all()
        
        return users, total
    
    def search_users_by_keyword(self, db: Session, keyword: str, skip: int = 0, limit: int = 100) -> tuple[List[UserInfo], int]:
        """키워드로 사용자 검색 (OR 조건)"""
        query = db.query(UserInfo)
        
        if keyword:
            # OR 조건으로 여러 필드에서 검색
            search_filter = or_(
                UserInfo.user_id.ilike(f"%{keyword}%"),
                UserInfo.user_nm.ilike(f"%{keyword}%"),
                UserInfo.email_adres.ilike(f"%{keyword}%"),
                UserInfo.empl_no.ilike(f"%{keyword}%")
            )
            query = query.filter(search_filter)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        users = query.order_by(desc(UserInfo.frst_regist_pnttm)).offset(skip).limit(limit).all()
        
        return users, total
    
    def get_user_statistics(self, db: Session) -> UserStatistics:
        """사용자 통계 조회"""
        # 전체 사용자 수
        total_users = db.query(func.count(UserInfo.user_id)).scalar()
        
        # 활성 사용자 수 (상태코드가 'A'인 사용자)
        active_users = db.query(func.count(UserInfo.user_id)).filter(
            UserInfo.emplyr_sttus_code == 'A'
        ).scalar()
        
        # 잠금된 사용자 수
        locked_users = db.query(func.count(UserInfo.user_id)).filter(
            UserInfo.lock_at == 'Y'
        ).scalar()
        
        # 상태별 사용자 수
        status_stats = db.query(
            UserInfo.emplyr_sttus_code,
            func.count(UserInfo.user_id)
        ).group_by(UserInfo.emplyr_sttus_code).all()
        users_by_status = {status: count for status, count in status_stats}
        
        # 조직별 사용자 수
        org_stats = db.query(
            UserInfo.orgnzt_id,
            func.count(UserInfo.user_id)
        ).filter(UserInfo.orgnzt_id.isnot(None)).group_by(UserInfo.orgnzt_id).all()
        users_by_organization = {org_id: count for org_id, count in org_stats}
        
        # 최근 30일 가입자 수
        thirty_days_ago = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        recent_registrations = db.query(func.count(UserInfo.user_id)).filter(
            UserInfo.sbscrb_de >= thirty_days_ago
        ).scalar()
        
        return UserStatistics(
            total_users=total_users or 0,
            active_users=active_users or 0,
            locked_users=locked_users or 0,
            users_by_status=users_by_status,
            users_by_organization=users_by_organization,
            recent_registrations=recent_registrations or 0
        )
    
    def lock_user(self, db: Session, user_id: str, current_user_id: Optional[str] = None) -> UserInfo:
        """사용자 계정 잠금"""
        user = self.get_by_user_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        user.lock_at = "Y"
        user.lock_last_pnttm = datetime.now()
        user.lock_cnt = (user.lock_cnt or Decimal(0)) + Decimal(1)
        user.last_updt_pnttm = datetime.now()
        user.last_updusr_id = current_user_id
        
        db.commit()
        db.refresh(user)
        return user
    
    def unlock_user(self, db: Session, user_id: str, current_user_id: Optional[str] = None) -> UserInfo:
        """사용자 계정 잠금 해제"""
        user = self.get_by_user_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다."
            )
        
        user.lock_at = "N"
        user.last_updt_pnttm = datetime.now()
        user.last_updusr_id = current_user_id
        
        db.commit()
        db.refresh(user)
        return user
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return pwd_context.verify(plain_password, hashed_password)


class OrgService(BaseService[Org, OrgCreate, OrgUpdate]):
    """조직 서비스 클래스"""
    
    def __init__(self):
        super().__init__(Org)
    
    def get(self, db: Session, org_no: Any) -> Optional[Org]:
        """
        조직번호로 단일 조직 조회
        
        Args:
            db: 데이터베이스 세션
            org_no: 조회할 조직번호
            
        Returns:
            조회된 조직 인스턴스 또는 None
        """
        try:
            return db.query(Org).filter(Org.org_no == org_no).first()
        except SQLAlchemyError as e:
            logger.error(f"❌ 조직 조회 실패 - org_no: {org_no}, 오류: {str(e)}")
            raise
    
    def create(self, db: Session, obj_in: OrgCreate, current_user_id: Optional[str] = None) -> Org:
        """조직 생성"""
        # 중복 조직번호 확인
        existing_org = db.query(Org).filter(Org.org_no == obj_in.org_no).first()
        if existing_org:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 조직번호입니다."
            )
        
        # 상위 조직 존재 확인
        if obj_in.parent_org_no:
            parent_org = db.query(Org).filter(Org.org_no == obj_in.parent_org_no).first()
            if not parent_org:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="상위 조직이 존재하지 않습니다."
                )
        
        obj_data = obj_in.model_dump()
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        
        db_obj = Org(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_organization_tree(self, db: Session, parent_org_no: Optional[Decimal] = None) -> List[OrgTreeNode]:
        """조직 트리 구조 조회"""
        # 모든 조직 조회
        orgs = db.query(Org).order_by(asc(Org.org_ordr)).all()
        
        # 조직별 사용자 수 조회
        user_counts = db.query(
            UserInfo.orgnzt_id,
            func.count(UserInfo.user_id)
        ).filter(UserInfo.orgnzt_id.isnot(None)).group_by(UserInfo.orgnzt_id).all()
        user_count_dict = {str(org_id): count for org_id, count in user_counts}
        
        # 조직 딕셔너리 생성
        org_dict = {}
        for org in orgs:
            org_dict[org.org_no] = OrgTreeNode(
                org_no=org.org_no,
                org_nm=org.org_nm,
                parent_org_no=org.parent_org_no,
                org_ordr=org.org_ordr,
                children=[],
                user_count=user_count_dict.get(str(org.org_no), 0)
            )
        
        # 트리 구조 생성
        root_nodes = []
        for org in orgs:
            if org.parent_org_no == parent_org_no:
                root_nodes.append(org_dict[org.org_no])
            elif org.parent_org_no in org_dict:
                org_dict[org.parent_org_no].children.append(org_dict[org.org_no])
        
        return root_nodes
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> tuple[List[Org], int]:
        """
        조직 목록 조회 (페이지네이션 지원)
        
        Returns:
            tuple: (조직 리스트, 전체 개수)
        """
        try:
            query = db.query(Org)
            
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if hasattr(Org, key) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            # LIKE 검색
                            query = query.filter(getattr(Org, key).like(value))
                        else:
                            # 정확한 매치
                            query = query.filter(getattr(Org, key) == value)
            
            # 정렬 적용 (기본: org_ordr 오름차순)
            if order_by and hasattr(Org, order_by):
                order_column = getattr(Org, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            else:
                query = query.order_by(asc(Org.org_ordr))
            
            # 전체 개수 조회
            total = query.count()
            
            # 페이지네이션 적용
            orgs = query.offset(skip).limit(limit).all()
            
            return orgs, total
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 조직 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_child_organizations(self, db: Session, parent_org_no: Decimal) -> List[Org]:
        """하위 조직 목록 조회"""
        return db.query(Org).filter(
            Org.parent_org_no == parent_org_no
        ).order_by(asc(Org.org_ordr)).all()
    
    def get_organization_path(self, db: Session, org_no: Decimal) -> List[Org]:
        """조직 경로 조회 (루트부터 현재 조직까지)"""
        path = []
        current_org = self.get(db, org_no)
        
        while current_org:
            path.insert(0, current_org)
            if current_org.parent_org_no:
                current_org = self.get(db, current_org.parent_org_no)
            else:
                break
        
        return path
    
    def update(self, db: Session, org_no: Any, obj_in: OrgUpdate, current_user_id: Optional[str] = None) -> Optional[Org]:
        """
        조직 정보 수정
        
        Args:
            db: 데이터베이스 세션
            org_no: 수정할 조직번호
            obj_in: 수정할 데이터
            current_user_id: 현재 사용자 ID
            
        Returns:
            수정된 조직 인스턴스 또는 None
        """
        try:
            db_obj = self.get(db, org_no)
            if not db_obj:
                return None
            
            obj_data = obj_in.model_dump(exclude_unset=True)
            obj_data["last_updt_pnttm"] = datetime.now()
            obj_data["last_updusr_id"] = current_user_id
            
            for field, value in obj_data.items():
                setattr(db_obj, field, value)
            
            db.commit()
            db.refresh(db_obj)
            return db_obj
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 조직 수정 실패 - org_no: {org_no}, 오류: {str(e)}")
            db.rollback()
            raise
    
    def remove(self, db: Session, org_no: Any) -> Optional[Org]:
        """
        조직 삭제
        
        Args:
            db: 데이터베이스 세션
            org_no: 삭제할 조직번호
            
        Returns:
            삭제된 조직 인스턴스 또는 None
        """
        try:
            db_obj = self.get(db, org_no)
            if not db_obj:
                return None
            
            # 하위 조직이 있는지 확인
            child_orgs = db.query(Org).filter(Org.parent_org_no == org_no).first()
            if child_orgs:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="하위 조직이 존재하여 삭제할 수 없습니다."
                )
            
            db.delete(db_obj)
            db.commit()
            return db_obj
            
        except SQLAlchemyError as e:
            logger.error(f"❌ 조직 삭제 실패 - org_no: {org_no}, 오류: {str(e)}")
            db.rollback()
            raise


class ZipService(BaseService[Zip, ZipCreate, ZipUpdate]):
    """우편번호 서비스 클래스"""
    
    def __init__(self):
        super().__init__(Zip)
    
    def create(self, db: Session, obj_in: ZipCreate, current_user_id: Optional[str] = None) -> Zip:
        """우편번호 생성"""
        # 중복 일련번호 확인
        existing_zip = db.query(Zip).filter(Zip.sn == obj_in.sn).first()
        if existing_zip:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 존재하는 일련번호입니다."
            )
        
        obj_data = obj_in.model_dump()
        obj_data["frst_regist_pnttm"] = datetime.now()
        obj_data["frst_register_id"] = current_user_id
        
        db_obj = Zip(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def search_by_address(self, db: Session, address: str, skip: int = 0, limit: int = 100) -> tuple[List[Zip], int]:
        """주소로 우편번호 검색"""
        query = db.query(Zip)
        
        # 주소 검색 (시도명, 시군구명, 읍면동명, 리건물명에서 검색)
        if address:
            search_filter = or_(
                Zip.ctprvn_nm.ilike(f"%{address}%"),
                Zip.signgu_nm.ilike(f"%{address}%"),
                Zip.emd_nm.ilike(f"%{address}%"),
                Zip.li_buld_nm.ilike(f"%{address}%")
            )
            query = query.filter(search_filter)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        zip_codes = query.order_by(asc(Zip.ctprvn_nm), asc(Zip.signgu_nm), asc(Zip.emd_nm)).offset(skip).limit(limit).all()
        
        return zip_codes, total
    
    def search_by_zip_code(self, db: Session, zip_code: str) -> List[Zip]:
        """우편번호로 주소 검색"""
        return db.query(Zip).filter(Zip.zip == zip_code).all()
    
    def get_provinces(self, db: Session) -> List[str]:
        """시도 목록 조회"""
        provinces = db.query(Zip.ctprvn_nm).distinct().filter(
            Zip.ctprvn_nm.isnot(None)
        ).order_by(asc(Zip.ctprvn_nm)).all()
        return [province[0] for province in provinces]
    
    def get_cities_by_province(self, db: Session, province: str) -> List[str]:
        """시도별 시군구 목록 조회"""
        cities = db.query(Zip.signgu_nm).distinct().filter(
            and_(
                Zip.ctprvn_nm == province,
                Zip.signgu_nm.isnot(None)
            )
        ).order_by(asc(Zip.signgu_nm)).all()
        return [city[0] for city in cities]
    
    def get_districts_by_city(self, db: Session, province: str, city: str) -> List[str]:
        """시군구별 읍면동 목록 조회"""
        districts = db.query(Zip.emd_nm).distinct().filter(
            and_(
                Zip.ctprvn_nm == province,
                Zip.signgu_nm == city,
                Zip.emd_nm.isnot(None)
            )
        ).order_by(asc(Zip.emd_nm)).all()
        return [district[0] for district in districts]
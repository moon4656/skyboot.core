"""인증 관련 서비스

사용자 정보 및 권한 관리를 위한 서비스 클래스들을 정의합니다.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
import logging
import bcrypt

from app.models.user_models import UserInfo
from app.models.auth_models import AuthorMenu
from app.schemas.user_schemas import (
    UserInfoCreate, UserInfoUpdate
)
from app.schemas.auth_schemas import (
    AuthorMenuCreate, AuthorMenuUpdate
)
from app.utils.jwt_utils import create_token_pair, verify_token
from .base_service import BaseService

logger = logging.getLogger(__name__)


class AuthorInfoService(BaseService[UserInfo, UserInfoCreate, UserInfoUpdate]):
    """사용자 정보 서비스
    
    사용자 계정 관리, 인증, 권한 검증 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(UserInfo)
    
    def get_by_user_id(self, db: Session, user_id: str) -> Optional[UserInfo]:
        """
        사용자 ID로 사용자 정보 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            사용자 정보 또는 None
        """
        try:
            return db.query(UserInfo).filter(
                UserInfo.user_id == user_id
            ).first()
        except Exception as e:
            logger.error(f"❌ 사용자 ID로 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_by_email(self, db: Session, email: str) -> Optional[UserInfo]:
        """
        이메일로 사용자 정보 조회
        
        Args:
            db: 데이터베이스 세션
            email: 이메일 주소
            
        Returns:
            사용자 정보 또는 None
        """
        try:
            return db.query(UserInfo).filter(
                UserInfo.email_adres == email
            ).first()
        except Exception as e:
            logger.error(f"❌ 이메일로 조회 실패 - email: {email}, 오류: {str(e)}")
            raise
    
    def authenticate(self, db: Session, user_id: str, password: str) -> Optional[UserInfo]:
        """
        사용자 인증
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            password: 비밀번호
            
        Returns:
            인증된 사용자 정보 또는 None
        """
        try:
            user = self.get_by_user_id(db, user_id)
            if not user:
                logger.warning(f"🔍 사용자를 찾을 수 없음 - user_id: {user_id}")
                return None
            
            # 비밀번호 검증
            if not self.verify_password(password, user.password):
                logger.warning(f"🔒 비밀번호 불일치 - user_id: {user_id}")
                return None
            
            # 계정 상태 확인 (활성 상태: '1')
            if user.emplyr_sttus_code != '1':
                logger.warning(f"🚫 비활성 계정 - user_id: {user_id}")
                return None
            
            logger.info(f"✅ 사용자 인증 성공 - user_id: {user_id}")
            return user
            
        except Exception as e:
            logger.error(f"❌ 사용자 인증 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def create_user(self, db: Session, user_data: UserInfoCreate) -> UserInfo:
        """
        새 사용자 생성
        
        Args:
            db: 데이터베이스 세션
            user_data: 사용자 생성 데이터
            
        Returns:
            생성된 사용자 정보
        """
        try:
            # 중복 확인
            if self.get_by_user_id(db, user_data.user_id):
                raise ValueError(f"이미 존재하는 사용자 ID입니다: {user_data.user_id}")
            
            if user_data.email_adres and self.get_by_email(db, user_data.email_adres):
                raise ValueError(f"이미 존재하는 이메일입니다: {user_data.email_adres}")
            
            # 비밀번호 해시화
            hashed_password = self.hash_password(user_data.password)
            
            # 사용자 생성
            user_dict = user_data.dict()
            user_dict['password'] = hashed_password
            
            return self.create(db, user_dict)
            
        except Exception as e:
            logger.error(f"❌ 사용자 생성 실패 - user_id: {user_data.user_id}, 오류: {str(e)}")
            raise
    
    def update_password(self, db: Session, user_id: str, new_password: str) -> bool:
        """
        사용자 비밀번호 변경
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            new_password: 새 비밀번호
            
        Returns:
            변경 성공 여부
        """
        try:
            user = self.get_by_user_id(db, user_id)
            if not user:
                return False
            
            # 비밀번호 해시화 및 업데이트
            hashed_password = self.hash_password(new_password)
            user.password = hashed_password
            user.last_updt_pnttm = datetime.now()
            
            db.add(user)
            db.commit()
            
            logger.info(f"✅ 비밀번호 변경 완료 - user_id: {user_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 비밀번호 변경 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_user_permissions(self, db: Session, user_id: str) -> List[str]:
        """
        사용자 권한 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            
        Returns:
            권한 코드 목록
        """
        try:
            user = self.get_by_user_id(db, user_id)
            if not user:
                return []
            
            # 사용자의 권한 그룹에서 권한 목록 조회 (UserInfo에는 author_code가 없으므로 group_id 사용)
            permissions = db.query(AuthorMenu.menu_no).filter(
                AuthorMenu.author_code == user.group_id
            ).all()
            
            return [perm.menu_no for perm in permissions]
            
        except Exception as e:
            logger.error(f"❌ 사용자 권한 조회 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def search_users(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        group_id: Optional[str] = None,
        emplyr_sttus_code: Optional[str] = None,
        author_code: Optional[str] = None,
        use_at: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserInfo]:
        """
        사용자 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어 (사용자ID, 이름, 이메일)
            group_id: 그룹 ID
            emplyr_sttus_code: 사용자 상태 코드
            author_code: 권한 코드
            use_at: 사용 여부
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 사용자 목록
        """
        try:
            query = db.query(UserInfo)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    UserInfo.user_id.like(f"%{search_term}%"),
                    UserInfo.user_nm.like(f"%{search_term}%"),
                    UserInfo.email_adres.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # 그룹 ID 조건
            if group_id:
                query = query.filter(UserInfo.group_id == group_id)
            
            # 사용자 상태 조건
            if emplyr_sttus_code:
                query = query.filter(UserInfo.emplyr_sttus_code == emplyr_sttus_code)
            
            # 권한 코드 조건
            if author_code:
                query = query.filter(UserInfo.author_code == author_code)
            
            # 사용 여부 조건
            if use_at:
                query = query.filter(UserInfo.use_at == use_at)
            
            return query.offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 사용자 검색 실패 - 오류: {str(e)}")
            raise
    
    def count(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        group_id: Optional[str] = None,
        emplyr_sttus_code: Optional[str] = None,
        author_code: Optional[str] = None,
        use_at: Optional[str] = None
    ) -> int:
        """
        사용자 검색 조건에 맞는 총 개수 조회
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어 (사용자ID, 이름, 이메일)
            group_id: 그룹 ID
            emplyr_sttus_code: 사용자 상태 코드
            author_code: 권한 코드
            use_at: 사용 여부
            
        Returns:
            조건에 맞는 사용자 총 개수
        """
        try:
            query = db.query(UserInfo)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    UserInfo.user_id.like(f"%{search_term}%"),
                    UserInfo.user_nm.like(f"%{search_term}%"),
                    UserInfo.email_adres.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # 그룹 ID 조건
            if group_id:
                query = query.filter(UserInfo.group_id == group_id)
            
            # 사용자 상태 조건
            if emplyr_sttus_code:
                query = query.filter(UserInfo.emplyr_sttus_code == emplyr_sttus_code)
            
            # 권한 코드 조건
            if author_code:
                query = query.filter(UserInfo.author_code == author_code)
            
            # 사용 여부 조건
            if use_at:
                query = query.filter(UserInfo.use_at == use_at)
            
            return query.count()
            
        except Exception as e:
            logger.error(f"❌ 사용자 개수 조회 실패 - 오류: {str(e)}")
            raise
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        비밀번호 해시화
        
        Args:
            password: 원본 비밀번호
            
        Returns:
            해시화된 비밀번호
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        비밀번호 검증
        
        Args:
            password: 입력된 비밀번호
            hashed_password: 저장된 해시 비밀번호
            
        Returns:
            비밀번호 일치 여부
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def authenticate_and_create_tokens(self, db: Session, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        사용자 인증 후 JWT 토큰 쌍을 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            password: 비밀번호
            
        Returns:
            토큰 정보와 사용자 정보 또는 None
        """
        try:
            # 사용자 인증
            user = self.authenticate(db, user_id, password)
            if not user:
                logger.warning(f"⚠️ 인증 실패 - user_id: {user_id}")
                return None
            
            # 사용자 데이터 준비
            user_data = {
                "user_id": user.user_id,
                "email_adres": user.email_adres,
                "group_id": user.group_id,
                "user_nm": user.user_nm,
                "orgnzt_id": user.orgnzt_id
            }
            
            # JWT 토큰 쌍 생성
            token_info = create_token_pair(user_data)
            
            # 사용자 정보 구성
            user_info = {
                "user_id": user.user_id,
                "orgnzt_id": user.orgnzt_id,
                "user_nm": user.user_nm,
                "empl_no": user.empl_no,
                "ihidnum": user.ihidnum,
                "sexdstn_code": user.sexdstn_code,
                "brthdy": user.brthdy,
                "fxnum": user.fxnum,
                "house_adres": user.house_adres,
                "password_hint": user.password_hint,
                "password_cnsr": user.password_cnsr,
                "house_end_telno": user.house_end_telno,
                "area_no": user.area_no,
                "detail_adres": user.detail_adres,
                "zip": user.zip,
                "offm_telno": user.offm_telno,
                "mbtlnum": user.mbtlnum,
                "email_adres": user.email_adres,
                "ofcps_nm": user.ofcps_nm,
                "house_middle_telno": user.house_middle_telno,
                "group_id": user.group_id,
                "pstinst_code": user.pstinst_code,
                "emplyr_sttus_code": user.emplyr_sttus_code,
                "esntl_id": user.esntl_id,
                "crtfc_dn_value": user.crtfc_dn_value,
                "sbscrb_de": user.sbscrb_de,
                "lock_at": user.lock_at,
                "lock_cnt": user.lock_cnt,
                "lock_last_pnttm": user.lock_last_pnttm,
                "chg_pwd_last_pnttm": user.chg_pwd_last_pnttm,
                "frst_regist_pnttm": user.frst_regist_pnttm,
                "frst_register_id": user.frst_register_id,
                "last_updt_pnttm": user.last_updt_pnttm,
                "last_updusr_id": user.last_updusr_id
            }
            
            # 결과 반환
            result = {
                "access_token": token_info["access_token"],
                "refresh_token": token_info["refresh_token"],
                "token_type": token_info["token_type"],
                "expires_in": token_info["expires_in"],
                "user_info": user_info
            }
            
            logger.info(f"✅ 인증 및 토큰 생성 완료 - user_id: {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 인증 및 토큰 생성 실패 - user_id: {user_id}, 오류: {str(e)}")
            raise
    
    def get_current_user_from_token(self, db: Session, token: str) -> Optional[Dict[str, Any]]:
        """
        JWT 토큰에서 현재 사용자 정보를 추출합니다.
        
        Args:
            db: 데이터베이스 세션
            token: JWT 액세스 토큰
            
        Returns:
            사용자 정보 또는 None
        """
        try:
            # 토큰 검증 및 페이로드 추출
            payload = verify_token(token)
            if not payload:
                logger.warning("⚠️ 토큰 검증 실패")
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                logger.warning("⚠️ 토큰에서 user_id를 찾을 수 없음")
                return None
            
            # 데이터베이스에서 사용자 정보 조회
            user = self.get_by_user_id(db, user_id)
            if not user:
                logger.warning(f"⚠️ 사용자를 찾을 수 없음 - user_id: {user_id}")
                return None
            
            # 계정 상태 확인 (활성 상태: '1')
            if user.emplyr_sttus_code != '1':
                logger.warning(f"🚫 비활성 계정 - user_id: {user_id}")
                return None
            
            # 사용자 정보 반환
            user_info = {
                "user_id": user.user_id,
                "email_adres": user.email_adres,
                "group_id": user.group_id,
                "user_nm": user.user_nm,
                "orgnzt_id": user.orgnzt_id,
                "emplyr_sttus_code": user.emplyr_sttus_code
            }
            
            logger.info(f"✅ 토큰에서 사용자 정보 추출 완료 - user_id: {user_id}")
            return user_info
            
        except Exception as e:
            logger.error(f"❌ 토큰에서 사용자 정보 추출 실패 - 오류: {str(e)}")
            return None
    
    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        리프레시 토큰을 사용하여 새로운 액세스 토큰을 생성합니다.
        
        Args:
            db: 데이터베이스 세션
            refresh_token: 리프레시 토큰
            
        Returns:
            새로운 토큰 정보 또는 None
        """
        try:
            logger.info(f"🔄 리프레시 토큰 검증 시작 - token length: {len(refresh_token) if refresh_token else 0}")
            logger.debug(f"🔍 받은 리프레시 토큰: {refresh_token[:50] if refresh_token else 'None'}...")
            
            # 리프레시 토큰 검증
            payload = verify_token(refresh_token, "refresh")
            if not payload:
                logger.warning("⚠️ 리프레시 토큰 검증 실패")
                return None
            
            # 사용자 데이터 추출
            user_data = {
                "user_id": payload.get("user_id"),
                "email_adres": payload.get("email"),
                "group_id": payload.get("group_id")
            }
            
            # 새로운 액세스 토큰 생성
            from app.utils.jwt_utils import create_access_token, get_token_expiry_time
            
            token_data = {
                "sub": user_data["user_id"],
                "user_id": user_data["user_id"],
                "email": user_data["email_adres"],
                "group_id": user_data["group_id"]
            }
            
            new_access_token = create_access_token(token_data)
            
            result = {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": get_token_expiry_time("access")
            }
            
            logger.info(f"✅ 액세스 토큰 갱신 완료 - user_id: {user_data['user_id']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ 액세스 토큰 갱신 실패: {str(e)}")
            return None
    
    def verify_access_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        액세스 토큰을 검증합니다.
        
        Args:
            access_token: 액세스 토큰
            
        Returns:
            토큰 페이로드 또는 None
        """
        try:
            payload = verify_token(access_token, "access")
            if payload:
                logger.info(f"✅ 액세스 토큰 검증 성공 - user_id: {payload.get('user_id')}")
            return payload
        except Exception as e:
            logger.error(f"❌ 액세스 토큰 검증 실패: {str(e)}")
            return None


class AuthorMenuService(BaseService[AuthorMenu, AuthorMenuCreate, AuthorMenuUpdate]):
    """권한 메뉴 서비스
    
    사용자 권한과 메뉴 접근 권한 관리를 위한 서비스입니다.
    """
    
    def __init__(self):
        super().__init__(AuthorMenu)
    
    def get_by_author_code(self, db: Session, author_code: str) -> List[AuthorMenu]:
        """
        권한 코드로 메뉴 권한 목록 조회
        
        Args:
            db: 데이터베이스 세션
            author_code: 권한 코드
            
        Returns:
            메뉴 권한 목록
        """
        try:
            return db.query(AuthorMenu).filter(
                and_(
                    AuthorMenu.author_code == author_code,
                    AuthorMenu.use_at == 'Y',
                    AuthorMenu.delete_at == 'N'
                )
            ).all()
        except Exception as e:
            logger.error(f"❌ 권한별 메뉴 조회 실패 - author_code: {author_code}, 오류: {str(e)}")
            raise
    
    def get_by_menu_id(self, db: Session, menu_id: str) -> List[AuthorMenu]:
        """
        메뉴 ID로 권한 목록 조회
        
        Args:
            db: 데이터베이스 세션
            menu_id: 메뉴 ID
            
        Returns:
            해당 메뉴에 대한 권한 목록
        """
        try:
            return db.query(AuthorMenu).filter(
                AuthorMenu.menu_no == menu_id
            ).all()
        except Exception as e:
            logger.error(f"❌ 메뉴별 권한 조회 실패 - menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def check_permission(
        self, 
        db: Session, 
        author_code: str, 
        menu_id: str,
        permission_type: str = 'read'
    ) -> bool:
        """
        권한 확인
        
        Args:
            db: 데이터베이스 세션
            author_code: 권한 코드
            menu_id: 메뉴 ID
            permission_type: 권한 유형 (read, write, delete)
            
        Returns:
            권한 보유 여부
        """
        try:
            permission = db.query(AuthorMenu).filter(
                and_(
                    AuthorMenu.author_code == author_code,
                    AuthorMenu.menu_no == menu_id
                )
            ).first()
            
            if not permission:
                return False
            
            # 권한 유형별 확인
            if permission_type == 'read':
                return permission.read_at == 'Y'
            elif permission_type == 'write':
                return permission.write_at == 'Y'
            elif permission_type == 'delete':
                return permission.delete_at == 'Y'
            
            return False
            
        except Exception as e:
            logger.error(f"❌ 권한 확인 실패 - author_code: {author_code}, menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def grant_permission(
        self, 
        db: Session, 
        author_code: str, 
        menu_id: str,
        read_at: str = 'Y',
        write_at: str = 'N',
        delete_at: str = 'N',
        user_id: str = 'system'
    ) -> AuthorMenu:
        """
        권한 부여
        
        Args:
            db: 데이터베이스 세션
            author_code: 권한 코드
            menu_id: 메뉴 ID
            read_at: 읽기 권한
            write_at: 쓰기 권한
            delete_at: 삭제 권한
            user_id: 권한 부여자 ID
            
        Returns:
            생성된 권한 정보
        """
        try:
            # 기존 권한 확인
            existing = db.query(AuthorMenu).filter(
                and_(
                    AuthorMenu.author_code == author_code,
                    AuthorMenu.menu_no == menu_id
                )
            ).first()
            
            if existing:
                # 기존 권한 업데이트
                existing.read_at = read_at
                existing.write_at = write_at
                existing.delete_at = delete_at
                existing.use_at = 'Y'
                existing.last_updusr_id = user_id
                existing.last_updt_pnttm = datetime.now()
                
                db.add(existing)
                db.commit()
                db.refresh(existing)
                
                logger.info(f"✅ 권한 업데이트 완료 - author_code: {author_code}, menu_id: {menu_id}")
                return existing
            else:
                # 새 권한 생성
                permission_data = {
                    'author_code': author_code,
                    'menu_no': menu_id,
                    'read_at': read_at,
                    'write_at': write_at,
                    'delete_at': delete_at,
                    'use_at': 'Y',
                    'frst_register_id': user_id
                }
                
                new_permission = self.create(db, permission_data)
                logger.info(f"✅ 권한 생성 완료 - author_code: {author_code}, menu_id: {menu_id}")
                return new_permission
                
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 권한 부여 실패 - author_code: {author_code}, menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def revoke_permission(
        self, 
        db: Session, 
        author_code: str, 
        menu_id: str,
        user_id: str = 'system'
    ) -> bool:
        """
        권한 회수
        
        Args:
            db: 데이터베이스 세션
            author_code: 권한 코드
            menu_id: 메뉴 ID
            user_id: 권한 회수자 ID
            
        Returns:
            권한 회수 성공 여부
        """
        try:
            permission = db.query(AuthorMenu).filter(
                and_(
                    AuthorMenu.author_code == author_code,
                    AuthorMenu.menu_no == menu_id
                )
            ).first()
            
            if permission:
                permission.use_at = 'N'
                permission.last_updusr_id = user_id
                permission.last_updt_pnttm = datetime.now()
                
                db.add(permission)
                db.commit()
                
                logger.info(f"✅ 권한 회수 완료 - author_code: {author_code}, menu_id: {menu_id}")
                return True
            
            return False
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 권한 회수 실패 - author_code: {author_code}, menu_id: {menu_id}, 오류: {str(e)}")
            raise
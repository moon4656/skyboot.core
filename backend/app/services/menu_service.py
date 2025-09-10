"""메뉴 관련 서비스

메뉴 정보 관리를 위한 서비스 클래스를 정의합니다.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from datetime import datetime
from decimal import Decimal
import logging

from app.models.menu_models import MenuInfo
from app.schemas.menu_schemas import MenuInfoCreate, MenuInfoUpdate
from .base_service import BaseService

logger = logging.getLogger(__name__)


class MenuInfoService(BaseService[MenuInfo, MenuInfoCreate, MenuInfoUpdate]):
    """메뉴 정보 서비스
    
    메뉴 구조 관리, 계층형 메뉴 처리 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        super().__init__(MenuInfo)
    
    def get_by_menu_id(self, db: Session, menu_id: str) -> Optional[MenuInfo]:
        """
        메뉴 ID로 메뉴 정보 조회
        
        Args:
            db: 데이터베이스 세션
            menu_id: 메뉴 ID
            
        Returns:
            메뉴 정보 또는 None
        """
        try:
            return db.query(MenuInfo).filter(
                and_(
                    MenuInfo.menu_no == menu_id,
                    MenuInfo.display_yn == 'Y'
                )
            ).first()
        except Exception as e:
            logger.error(f"❌ 메뉴 조회 실패 - menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def get_root_menus(self, db: Session, use_at: Optional[str] = None) -> List[MenuInfo]:
        """
        최상위 메뉴 목록 조회
        
        Args:
            db: 데이터베이스 세션
            use_at: 사용 여부 필터
            
        Returns:
            최상위 메뉴 목록
        """
        try:
            query = db.query(MenuInfo).filter(
                MenuInfo.upper_menu_no.is_(None)
            )
            
            if use_at:
                query = query.filter(MenuInfo.display_yn == use_at)
            else:
                query = query.filter(MenuInfo.display_yn == 'Y')
            
            return query.order_by(MenuInfo.menu_ordr).all()
        except Exception as e:
            logger.error(f"❌ 최상위 메뉴 조회 실패 - 오류: {str(e)}")
            raise
    
    def get_child_menus(self, db: Session, parent_menu_id: str, use_at: Optional[str] = None) -> List[MenuInfo]:
        """
        하위 메뉴 목록 조회
        
        Args:
            db: 데이터베이스 세션
            parent_menu_id: 상위 메뉴 ID
            use_at: 사용 여부 필터
            
        Returns:
            하위 메뉴 목록
        """
        try:
            query = db.query(MenuInfo).filter(
                MenuInfo.upper_menu_no == parent_menu_id
            )
            
            if use_at:
                query = query.filter(MenuInfo.display_yn == use_at)
            else:
                query = query.filter(MenuInfo.display_yn == 'Y')
            
            return query.order_by(MenuInfo.menu_ordr).all()
        except Exception as e:
            logger.error(f"❌ 하위 메뉴 조회 실패 - parent_menu_id: {parent_menu_id}, 오류: {str(e)}")
            raise
    
    def get_menu_tree(self, db: Session, parent_menu_id: Optional[str] = None, use_at: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        계층형 메뉴 트리 조회
        
        Args:
            db: 데이터베이스 세션
            parent_menu_id: 상위 메뉴 ID (None이면 전체 트리)
            use_at: 사용 여부 필터
            
        Returns:
            계층형 메뉴 트리
        """
        try:
            def build_menu_tree(parent_id: Optional[str]) -> List[Dict[str, Any]]:
                if parent_id is None:
                    menus = self.get_root_menus(db, use_at)
                else:
                    menus = self.get_child_menus(db, parent_id, use_at)
                
                menu_tree = []
                for menu in menus:
                    children = build_menu_tree(menu.menu_no)
                    menu_dict = {
                        'id': int(menu.menu_no) if menu.menu_no.isdigit() else menu.menu_no,  # 프론트엔드가 기대하는 id 필드
                        'name': menu.menu_nm,  # 프론트엔드가 기대하는 name 필드
                        'menu_id': menu.menu_no,  # 기존 호환성을 위해 유지
                        'menu_no': menu.menu_no,
                        'menu_nm': menu.menu_nm,
                        'path': getattr(menu, 'menu_url', None),  # 메뉴 URL이 있다면 path로 설정
                        'icon': getattr(menu, 'menu_icon', None),  # 메뉴 아이콘이 있다면 설정
                        'parent_id': int(menu.upper_menu_no) if menu.upper_menu_no and menu.upper_menu_no.isdigit() else menu.upper_menu_no,
                        'order_num': menu.menu_ordr,
                        'is_active': getattr(menu, 'use_at', 'Y') == 'Y',  # 사용 여부를 boolean으로 변환
                        'menu_level': Decimal('1') if menu.upper_menu_no is None else Decimal('2'),
                        'menu_ordr': menu.menu_ordr,
                        'leaf_at': 'Y' if not children else 'N',
                        'children': children
                    }
                    menu_tree.append(menu_dict)
                
                return menu_tree
            
            return build_menu_tree(parent_menu_id)
            
        except Exception as e:
            logger.error(f"❌ 메뉴 트리 조회 실패 - parent_menu_id: {parent_menu_id}, 오류: {str(e)}")
            raise
    
    def get_menu_breadcrumb(self, db: Session, menu_id: str) -> List[MenuInfo]:
        """
        메뉴 경로(breadcrumb) 조회
        
        Args:
            db: 데이터베이스 세션
            menu_id: 메뉴 ID
            
        Returns:
            메뉴 경로 목록 (최상위부터 현재 메뉴까지)
        """
        try:
            breadcrumb = []
            current_menu_id = menu_id
            
            while current_menu_id:
                # 매번 새로운 쿼리로 메뉴 조회
                menu_obj = db.query(MenuInfo).filter(MenuInfo.menu_no == current_menu_id).first()
                if not menu_obj:
                    break
                
                # 세션 바인딩 문제를 방지하기 위해 객체를 새로 생성
                detached_menu = MenuInfo(
                    menu_no=menu_obj.menu_no,
                    menu_nm=menu_obj.menu_nm,
                    progrm_file_nm=menu_obj.progrm_file_nm,
                    upper_menu_no=menu_obj.upper_menu_no,
                    menu_ordr=menu_obj.menu_ordr,
                    menu_dc=menu_obj.menu_dc,
                    relate_image_path=menu_obj.relate_image_path,
                    relate_image_nm=menu_obj.relate_image_nm,
                    display_yn=menu_obj.display_yn,
                    use_tag_yn=menu_obj.use_tag_yn,
                    menu_tag=menu_obj.menu_tag,
                    frst_regist_pnttm=menu_obj.frst_regist_pnttm,
                    frst_register_id=menu_obj.frst_register_id,
                    last_updt_pnttm=menu_obj.last_updt_pnttm,
                    last_updusr_id=menu_obj.last_updusr_id
                )
                
                breadcrumb.insert(0, detached_menu)
                
                # 상위 메뉴 ID로 이동
                current_menu_id = menu_obj.upper_menu_no
            
            return breadcrumb
            
        except Exception as e:
            logger.error(f"❌ 메뉴 경로 조회 실패 - menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def search_menus(
        self, 
        db: Session, 
        search_term: Optional[str] = None,
        menu_level: Optional[int] = None,
        parent_menu_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[MenuInfo]:
        """
        메뉴 검색
        
        Args:
            db: 데이터베이스 세션
            search_term: 검색어 (메뉴명, 설명)
            menu_level: 메뉴 레벨
            parent_menu_id: 상위 메뉴 ID
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            
        Returns:
            검색된 메뉴 목록
        """
        try:
            query = db.query(MenuInfo)
            
            # 검색어 조건
            if search_term:
                search_filter = or_(
                    MenuInfo.menu_nm.like(f"%{search_term}%"),
                    MenuInfo.menu_dc.like(f"%{search_term}%")
                )
                query = query.filter(search_filter)
            
            # 상위 메뉴 조건
            if parent_menu_id:
                query = query.filter(MenuInfo.upper_menu_no == parent_menu_id)
            
            return query.order_by(MenuInfo.menu_ordr).offset(skip).limit(limit).all()
            
        except Exception as e:
            logger.error(f"❌ 메뉴 검색 실패 - 오류: {str(e)}")
            raise
    
    def create_menu(
        self, 
        db: Session, 
        menu_data: MenuInfoCreate,
        user_id: str = 'system'
    ) -> MenuInfo:
        """
        새 메뉴 생성
        
        Args:
            db: 데이터베이스 세션
            menu_data: 메뉴 생성 데이터
            user_id: 생성자 ID
            
        Returns:
            생성된 메뉴 정보
        """
        try:
            # 중복 메뉴 번호 확인
            existing_menu = db.query(MenuInfo).filter(
                MenuInfo.menu_no == menu_data.menu_no
            ).first()
            if existing_menu:
                raise ValueError(f"이미 존재하는 메뉴 번호입니다: {menu_data.menu_no}")
            
            # 메뉴 순서 계산 (같은 레벨에서 마지막 순서 + 1)
            upper_menu_no = getattr(menu_data, 'upper_menu_no', None)
            max_order = db.query(MenuInfo.menu_ordr).filter(
                MenuInfo.upper_menu_no == upper_menu_no
            ).order_by(desc(MenuInfo.menu_ordr)).first()
            
            menu_order = (max_order[0] if max_order else 0) + 1
            
            # 메뉴 생성
            menu = self.create(db, menu_data, menu_ordr=menu_order, frst_register_id=user_id)
            logger.info(f"✅ 메뉴 생성 완료 - menu_no: {menu.menu_no}")
            return menu
            
        except Exception as e:
            logger.error(f"❌ 메뉴 생성 실패 - menu_no: {menu_data.menu_no}, 오류: {str(e)}")
            raise
    
    def move_menu(
        self, 
        db: Session, 
        menu_no: str, 
        new_parent_id: Optional[str],
        new_order: Optional[int] = None,
        user_id: str = 'system'
    ) -> bool:
        """
        메뉴 이동
        
        Args:
            db: 데이터베이스 세션
            menu_no: 이동할 메뉴 번호
            new_parent_id: 새로운 상위 메뉴 ID
            new_order: 새로운 순서
            user_id: 수정자 ID
            
        Returns:
            이동 성공 여부
        """
        try:
            menu = self.get_by_menu_id(db, menu_no)
            if not menu:
                return False
            
            # 자기 자신을 상위 메뉴로 설정하는 것 방지
            if new_parent_id == menu_no:
                raise ValueError("자기 자신을 상위 메뉴로 설정할 수 없습니다")
            
            # 하위 메뉴를 상위 메뉴로 설정하는 것 방지
            if new_parent_id and self._is_descendant(db, menu_no, new_parent_id):
                raise ValueError("하위 메뉴를 상위 메뉴로 설정할 수 없습니다")
            
            # 순서 계산
            if new_order is None:
                max_order = db.query(MenuInfo.menu_ordr).filter(
                    MenuInfo.upper_menu_no == new_parent_id
                ).order_by(desc(MenuInfo.menu_ordr)).first()
                new_order = (max_order[0] if max_order else 0) + 1
            
            # 메뉴 업데이트
            menu.upper_menu_no = new_parent_id
            menu.menu_ordr = new_order
            menu.last_updusr_id = user_id
            menu.last_updt_pnttm = datetime.now()
            
            db.add(menu)
            db.commit()
            
            logger.info(f"✅ 메뉴 이동 완료 - menu_no: {menu.menu_no}, 새 상위: {new_parent_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 메뉴 이동 실패 - menu_no: {menu.menu_no}, 오류: {str(e)}")
            raise
    
    def update_menu_order(
        self, 
        db: Session, 
        menu_orders: List[Dict[str, int]],
        user_id: str = 'system'
    ) -> bool:
        """
        메뉴 순서 일괄 업데이트
        
        Args:
            db: 데이터베이스 세션
            menu_orders: [{"menu_id": "MENU1", "menu_ordr": 1}, ...]
            user_id: 수정자 ID
            
        Returns:
            업데이트 성공 여부
        """
        try:
            for order_info in menu_orders:
                menu_no = order_info.get('menu_no')
                menu_ordr = order_info.get('menu_ordr')
                
                if not menu_no or menu_ordr is None:
                    continue
                
                menu = db.query(MenuInfo).filter(
                    MenuInfo.menu_no == menu_no
                ).first()
                
                if menu:
                    menu.menu_ordr = menu_ordr
                    menu.last_updusr_id = user_id
                    menu.last_updt_pnttm = datetime.now()
                    db.add(menu)
            
            db.commit()
            logger.info(f"✅ 메뉴 순서 업데이트 완료 - 업데이트된 메뉴 수: {len(menu_orders)}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 메뉴 순서 업데이트 실패 - 오류: {str(e)}")
            raise
    
    def get_menu_statistics(self, db: Session) -> Dict[str, Any]:
        """
        메뉴 통계 조회
        
        Args:
            db: 데이터베이스 세션
            
        Returns:
            메뉴 통계 정보
        """
        try:
            from sqlalchemy import func
            
            # 전체 메뉴 수
            total_menus = db.query(MenuInfo).count()
            
            # 활성 메뉴 수
            active_menus = db.query(MenuInfo).filter(
                MenuInfo.display_yn == 'Y'
            ).count()
            
            # 최상위 메뉴 수
            root_menus = db.query(MenuInfo).filter(
                MenuInfo.upper_menu_no.is_(None)
            ).count()
            
            # 하위 메뉴 수
            child_menus = db.query(MenuInfo).filter(
                MenuInfo.upper_menu_no.is_not(None)
            ).count()
            
            # 리프 메뉴 수 (하위 메뉴가 없는 메뉴)
            leaf_menus = db.query(MenuInfo).filter(
                ~db.query(MenuInfo.menu_no).filter(
                    MenuInfo.upper_menu_no == MenuInfo.menu_no
                ).exists()
            ).count()
            
            # 최대 깊이 계산 (간단히 2로 설정)
            max_depth = 2 if child_menus > 0 else 1
            
            # 메뉴당 평균 하위 메뉴 수
            avg_children_per_menu = child_menus / root_menus if root_menus > 0 else 0.0
            
            return {
                'total_menus': total_menus,
                'active_menus': active_menus,
                'inactive_menus': total_menus - active_menus,
                'leaf_menus': leaf_menus,
                'max_depth': max_depth,
                'avg_children_per_menu': avg_children_per_menu
            }
            
        except Exception as e:
            logger.error(f"❌ 메뉴 통계 조회 실패 - 오류: {str(e)}")
            raise
    
    def _is_descendant(self, db: Session, ancestor_id: str, descendant_id: str) -> bool:
        """
        특정 메뉴가 다른 메뉴의 하위 메뉴인지 확인
        
        Args:
            db: 데이터베이스 세션
            ancestor_id: 상위 메뉴 ID
            descendant_id: 확인할 메뉴 ID
            
        Returns:
            하위 메뉴 여부
        """
        current_menu = self.get_by_menu_id(db, descendant_id)
        
        while current_menu and current_menu.upper_menu_no:
            if current_menu.upper_menu_no == ancestor_id:
                return True
            current_menu = self.get_by_menu_id(db, current_menu.upper_menu_no)
        
        return False
    

    
    def validate_menu_data(self, db: Session, menu_data: MenuInfoCreate) -> Dict[str, Any]:
        """메뉴 데이터 검증
        
        Args:
            db: 데이터베이스 세션
            menu_data: 검증할 메뉴 데이터
            
        Returns:
            검증 결과
        """
        try:
            validation_result = {
                "is_valid": True,
                "errors": [],
                "warnings": []
            }
            
            # 메뉴 번호 중복 확인
            existing_menu = self.get(db, menu_data.menu_no)
            if existing_menu:
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"메뉴 번호가 이미 존재합니다: {menu_data.menu_no}")
            
            # 상위 메뉴 존재 확인
            if menu_data.upper_menu_no:
                parent_menu = self.get(db, menu_data.upper_menu_no)
                if not parent_menu:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"상위 메뉴를 찾을 수 없습니다: {menu_data.upper_menu_no}")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ 메뉴 데이터 검증 실패: {str(e)}")
            raise
    
    def _get_max_child_depth(self, db: Session, menu_id: str, current_depth: int = 0) -> int:
        """
        메뉴의 최대 하위 깊이를 계산합니다.
        
        Args:
            db: 데이터베이스 세션
            menu_id: 메뉴 ID
            current_depth: 현재 깊이
            
        Returns:
            최대 하위 깊이
        """
        children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == menu_id).all()
        
        if not children:
            return current_depth
        
        max_depth = current_depth
        for child in children:
            child_depth = self._get_max_child_depth(db, child.menu_no, current_depth + 1)
            max_depth = max(max_depth, child_depth)
        
        return max_depth
    
    def copy_menu(
        self, 
        db: Session, 
        source_menu_id: str, 
        new_menu_id: str,
        new_menu_nm: Optional[str] = None,
        new_parent_id: Optional[str] = None,
        copy_children: bool = False,
        user_id: str = 'system',
        _depth: int = 0,
        _copied_menus: Optional[set] = None
    ) -> MenuInfo:
        """
        메뉴 복사
        
        Args:
            db: 데이터베이스 세션
            source_menu_id: 원본 메뉴 ID
            new_menu_id: 새로운 메뉴 ID
            new_menu_nm: 새로운 메뉴명 (None이면 원본 메뉴명 사용)
            new_parent_id: 새로운 상위 메뉴 ID
            copy_children: 하위 메뉴 포함 복사 여부
            user_id: 생성자 ID
            _depth: 재귀 깊이 (내부 사용)
            _copied_menus: 복사된 메뉴 추적 (내부 사용)
            
        Returns:
            복사된 메뉴 객체
        """
        try:
            # 실제 메뉴 트리 깊이 계산
            if _depth == 0:  # 최초 호출 시에만 전체 깊이 체크
                # 새로운 부모 메뉴의 깊이 계산
                parent_depth = 0
                if new_parent_id:
                    current_parent = new_parent_id
                    while current_parent:
                        parent_menu = self.get_by_menu_id(db, current_parent)
                        if parent_menu and parent_menu.upper_menu_no:
                            parent_depth += 1
                            current_parent = parent_menu.upper_menu_no
                        else:
                            break
                
                # 복사할 메뉴의 최대 하위 깊이 계산
                max_child_depth = self._get_max_child_depth(db, source_menu_id)
                total_depth = parent_depth + 1 + max_child_depth  # 부모깊이 + 현재메뉴 + 하위깊이
                
                logger.info(f"🔍 메뉴 복사 깊이 체크 - 부모깊이: {parent_depth}, 하위깊이: {max_child_depth}, 총깊이: {total_depth}")
                
                if total_depth > 10:
                    logger.warning(f"⚠️ 메뉴 복사 깊이 제한 초과: {total_depth}")
                    raise ValueError(f"메뉴 복사 깊이가 너무 깊습니다 (최대 10레벨, 예상: {total_depth}레벨)")
            
            # 재귀 호출 깊이 체크 (안전장치)
            logger.info(f"🔍 메뉴 복사 재귀 깊이 체크 - 현재 깊이: {_depth}, 원본 메뉴: {source_menu_id}")
            if _depth > 15:  # 재귀 호출 안전장치
                logger.warning(f"⚠️ 메뉴 복사 재귀 깊이 제한 초과: {_depth}")
                raise ValueError(f"메뉴 복사 재귀 깊이가 너무 깊습니다 (최대 15레벨, 현재: {_depth}레벨)")
            
            # 복사된 메뉴 추적 초기화
            if _copied_menus is None:
                _copied_menus = set()
            
            # 자기 자신을 복사하는 것 방지
            if source_menu_id == new_parent_id:
                logger.warning(f"⚠️ 자기 자신을 복사하려고 시도: {source_menu_id}")
                raise ValueError(f"자기 자신을 복사할 수 없습니다: {source_menu_id}")
            
            # 순환 참조 방지
            if source_menu_id in _copied_menus:
                logger.warning(f"⚠️ 순환 참조 감지: {source_menu_id}")
                raise ValueError(f"순환 참조가 감지되었습니다: {source_menu_id}")
            
            # 현재 메뉴를 복사된 목록에 추가
            _copied_menus.add(source_menu_id)
            # 원본 메뉴 조회
            source_menu = self.get_by_menu_id(db, source_menu_id)
            if not source_menu:
                raise ValueError(f"원본 메뉴를 찾을 수 없습니다: {source_menu_id}")
            
            # 새로운 메뉴 ID 중복 확인
            existing_menu = self.get_by_menu_id(db, new_menu_id)
            if existing_menu:
                raise ValueError(f"이미 존재하는 메뉴 ID입니다: {new_menu_id}")
            
            # 새로운 상위 메뉴 존재 확인
            if new_parent_id:
                parent_menu = self.get_by_menu_id(db, new_parent_id)
                if not parent_menu:
                    raise ValueError(f"상위 메뉴를 찾을 수 없습니다: {new_parent_id}")
            
            # 새로운 순서 계산
            max_order = db.query(MenuInfo.menu_ordr).filter(
                MenuInfo.upper_menu_no == new_parent_id
            ).order_by(desc(MenuInfo.menu_ordr)).first()
            new_order = (max_order[0] if max_order else 0) + 1
            
            # 메뉴 복사
            copied_menu = MenuInfo(
                menu_no=new_menu_id,
                menu_nm=new_menu_nm or source_menu.menu_nm,
                upper_menu_no=new_parent_id,
                menu_ordr=new_order,
                menu_dc=source_menu.menu_dc,
                progrm_file_nm=source_menu.progrm_file_nm,
                display_yn=source_menu.display_yn,
                use_tag_yn=source_menu.use_tag_yn,
                relate_image_path=source_menu.relate_image_path,
                relate_image_nm=source_menu.relate_image_nm,
                menu_tag=source_menu.menu_tag,
                frst_register_id=user_id,
                frst_regist_pnttm=datetime.now(),
                last_updusr_id=user_id,
                last_updt_pnttm=datetime.now()
            )
            
            db.add(copied_menu)
            db.flush()  # ID 생성을 위해 flush
            
            # 하위 메뉴 복사 (재귀적)
            if copy_children:
                children = db.query(MenuInfo).filter(
                    MenuInfo.upper_menu_no == source_menu_id
                ).all()
                
                for i, child in enumerate(children):
                    # 고유한 새 메뉴 ID 생성 (타임스탬프 포함)
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    child_new_id = f"{new_menu_id}_{i+1:03d}_{timestamp[-6:]}"
                    
                    # 재귀 호출 시 깊이와 추적 정보 전달
                    self.copy_menu(
                        db=db,
                        source_menu_id=child.menu_no,
                        new_menu_id=child_new_id,
                        new_menu_nm=child.menu_nm,
                        new_parent_id=new_menu_id,
                        copy_children=True,
                        user_id=user_id,
                        _depth=_depth + 1,
                        _copied_menus=_copied_menus.copy()  # 복사본 전달
                    )
            
            db.commit()
            
            logger.info(f"✅ 메뉴 복사 완료 - 원본: {source_menu_id}, 복사본: {new_menu_id}")
            return copied_menu
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 메뉴 복사 실패 - 원본: {source_menu_id}, 오류: {str(e)}")
            raise
    
    def soft_delete(self, db: Session, menu_id: str, user_id: str) -> Optional[MenuInfo]:
        """
        메뉴 논리적 삭제 (display_yn을 'N'으로 설정)
        
        Args:
            db: 데이터베이스 세션
            menu_id: 삭제할 메뉴 ID (menu_no)
            user_id: 삭제 수행자 ID
            
        Returns:
            삭제된 메뉴 정보 또는 None
        """
        try:
            menu = db.query(MenuInfo).filter(MenuInfo.menu_no == menu_id).first()
            if menu:
                menu.display_yn = 'N'
                if hasattr(menu, 'last_updusr_id'):
                    menu.last_updusr_id = user_id
                if hasattr(menu, 'last_updt_pnttm'):
                    menu.last_updt_pnttm = datetime.now()
                
                db.add(menu)
                db.commit()
                db.refresh(menu)
                
                logger.info(f"✅ 메뉴 논리적 삭제 완료 - menu_id: {menu_id}")
                return menu
            return None
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 메뉴 논리적 삭제 실패 - menu_id: {menu_id}, 오류: {str(e)}")
            raise
    
    def export_menu_data(self, db: Session, format: str = "json", include_inactive: bool = False) -> Dict[str, Any]:
        """메뉴 데이터 내보내기
        
        Args:
            db: 데이터베이스 세션
            format: 내보내기 형식
            include_inactive: 비활성 메뉴 포함 여부
            
        Returns:
            내보내기 데이터
        """
        try:
            query = db.query(MenuInfo)
            
            if not include_inactive:
                query = query.filter(MenuInfo.display_yn == 'Y')
            
            menus = query.all()
            
            # 임시 파일 생성 및 데이터 저장
            import uuid
            import json
            import os
            from datetime import timedelta
            
            export_id = str(uuid.uuid4())
            file_name = f"menu_export_{export_id[:8]}.json"
            file_path = os.path.join("uploads", file_name)
            
            export_data = {
                "format": format,
                "export_time": datetime.now().isoformat(),
                "total_count": len(menus),
                "data": []
            }
            
            for menu in menus:
                menu_dict = {
                    "menu_no": menu.menu_no,
                    "menu_nm": menu.menu_nm,
                    "upper_menu_no": menu.upper_menu_no,
                    "progrm_file_nm": menu.progrm_file_nm,
                    "menu_dc": menu.menu_dc,
                    "menu_ordr": str(menu.menu_ordr),
                    "display_yn": menu.display_yn,
                    "relate_image_path": menu.relate_image_path,
                    "relate_image_nm": menu.relate_image_nm
                }
                export_data["data"].append(menu_dict)
            
            # 파일 저장
            os.makedirs("uploads", exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(file_path)
            expires_at = datetime.now() + timedelta(hours=24)
            
            return {
                "export_id": export_id,
                "file_name": file_name,
                "file_size": file_size,
                "download_url": f"/api/v1/files/download/{file_name}",
                "expires_at": expires_at
            }
            
        except Exception as e:
            logger.error(f"❌ 메뉴 데이터 내보내기 실패: {str(e)}")
            raise
    
    def import_menu_data(self, db: Session, data: List[Dict], format: str = "json", overwrite: bool = False) -> Dict[str, Any]:
        """메뉴 데이터 가져오기
        
        Args:
            db: 데이터베이스 세션
            data: 가져올 데이터
            format: 데이터 형식
            overwrite: 덮어쓰기 여부
            
        Returns:
            가져오기 결과
        """
        try:
            result = {
                "success_count": 0,
                "error_count": 0,
                "errors": []
            }
            
            for menu_data in data:
                try:
                    existing_menu = self.get_by_menu_id(db, menu_data["menu_no"])
                    
                    if existing_menu and not overwrite:
                        result["error_count"] += 1
                        result["errors"].append(f"메뉴 번호가 이미 존재합니다: {menu_data['menu_no']}")
                        continue
                    
                    if existing_menu and overwrite:
                        # 기존 메뉴 업데이트
                        for key, value in menu_data.items():
                            if hasattr(existing_menu, key):
                                setattr(existing_menu, key, value)
                        existing_menu.last_updt_pnttm = datetime.now()
                        db.add(existing_menu)
                    else:
                        # 새 메뉴 생성
                        new_menu = MenuInfo(**menu_data)
                        new_menu.frst_regist_pnttm = datetime.now()
                        new_menu.last_updt_pnttm = datetime.now()
                        db.add(new_menu)
                    
                    result["success_count"] += 1
                    
                except Exception as e:
                    result["error_count"] += 1
                    result["errors"].append(f"메뉴 처리 실패 {menu_data.get('menu_no', 'Unknown')}: {str(e)}")
            
            db.commit()
            return result
            
        except Exception as e:
            db.rollback()
            logger.error(f"❌ 메뉴 데이터 가져오기 실패: {str(e)}")
            raise
    
    def validate_menu_data(self, db: Session, menu_data: MenuInfoCreate) -> dict:
        """
        메뉴 데이터를 검증합니다.
        
        Args:
            db: 데이터베이스 세션
            menu_data: 검증할 메뉴 데이터
            
        Returns:
            검증 결과
        """
        try:
            validation_results = []
            errors = []
            warnings = []
            suggestions = []
            
            # 1. 메뉴 번호 중복 검사
            existing_menu = self.get_by_menu_id(db, menu_data.menu_no)
            if existing_menu:
                errors.append(f"메뉴 번호가 이미 존재합니다: {menu_data.menu_no}")
            
            # 2. 상위 메뉴 존재 검사
            if menu_data.upper_menu_no:
                parent_menu = self.get_by_menu_id(db, menu_data.upper_menu_no)
                if not parent_menu:
                    errors.append(f"상위 메뉴가 존재하지 않습니다: {menu_data.upper_menu_no}")
            
            # 3. 메뉴명 검사
            if not menu_data.menu_nm or len(menu_data.menu_nm.strip()) == 0:
                errors.append("메뉴명은 필수입니다")
            elif len(menu_data.menu_nm) > 60:
                errors.append("메뉴명은 60자를 초과할 수 없습니다")
            
            # 4. 프로그램 파일명 검사
            if menu_data.progrm_file_nm and len(menu_data.progrm_file_nm) > 100:
                errors.append("프로그램 파일명은 100자를 초과할 수 없습니다")
            
            # 5. 메뉴 설명 검사
            if menu_data.menu_dc and len(menu_data.menu_dc) > 250:
                errors.append("메뉴 설명은 250자를 초과할 수 없습니다")
            
            # 검증 결과 생성
            is_valid = len(errors) == 0
            
            validation_result = {
                "is_valid": is_valid,
                "menu_id": menu_data.menu_no,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
            validation_results.append(validation_result)
            
            return {
                "is_valid": is_valid,
                "validation_results": validation_results,
                "summary": {
                    "total_checked": 1,
                    "valid_count": 1 if is_valid else 0,
                    "error_count": len(errors),
                    "warning_count": len(warnings)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ 메뉴 데이터 검증 실패: {str(e)}")
            raise
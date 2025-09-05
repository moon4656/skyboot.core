"""기본 CRUD 서비스 클래스

모든 서비스 클래스의 기본이 되는 CRUD 기능을 제공합니다.
"""

from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from datetime import datetime
import logging

# 타입 변수 정의
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """기본 CRUD 서비스 클래스
    
    모든 모델에 대한 기본적인 CRUD 작업을 제공합니다.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        서비스 초기화
        
        Args:
            model: SQLAlchemy 모델 클래스
        """
        self.model = model
    
    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        ID로 단일 레코드 조회
        
        Args:
            db: 데이터베이스 세션
            id: 조회할 레코드의 ID
            
        Returns:
            조회된 모델 인스턴스 또는 None
        """
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 조회 실패 - ID: {id}, 오류: {str(e)}")
            raise
    
    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """
        여러 레코드 조회 (페이지네이션 지원)
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 조회할 최대 레코드 수
            filters: 필터 조건 딕셔너리
            order_by: 정렬 기준 컬럼명
            order_desc: 내림차순 정렬 여부
            
        Returns:
            조회된 모델 인스턴스 리스트
        """
        try:
            query = db.query(self.model)
            
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            # LIKE 검색
                            query = query.filter(getattr(self.model, key).like(value))
                        else:
                            # 정확한 매치
                            query = query.filter(getattr(self.model, key) == value)
            
            # 정렬 적용
            if order_by and hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(asc(order_column))
            
            return query.offset(skip).limit(limit).all()
            
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 목록 조회 실패 - 오류: {str(e)}")
            raise
    
    def count(
        self, 
        db: Session, 
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        레코드 총 개수 조회
        
        Args:
            db: 데이터베이스 세션
            filters: 필터 조건 딕셔너리
            
        Returns:
            조건에 맞는 레코드 총 개수
        """
        try:
            query = db.query(self.model)
            
            # 필터 적용
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        if isinstance(value, str) and '%' in value:
                            query = query.filter(getattr(self.model, key).like(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)
            
            return query.count()
            
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 개수 조회 실패 - 오류: {str(e)}")
            raise
    
    def create(self, db: Session, obj_in: CreateSchemaType, **kwargs) -> ModelType:
        """
        새 레코드 생성
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 데이터 스키마
            **kwargs: 추가 필드 값
            
        Returns:
            생성된 모델 인스턴스
        """
        try:
            # Pydantic 모델을 딕셔너리로 변환
            obj_data = obj_in.dict() if hasattr(obj_in, 'dict') else obj_in
            
            # 추가 필드 병합
            obj_data.update(kwargs)
            
            # 공통 필드 설정
            current_time = datetime.now()
            if hasattr(self.model, 'frst_regist_pnttm'):
                obj_data['frst_regist_pnttm'] = current_time
            if hasattr(self.model, 'last_updt_pnttm'):
                obj_data['last_updt_pnttm'] = current_time
            
            # 모델에 존재하는 필드만 필터링
            model_columns = {column.name for column in self.model.__table__.columns}
            filtered_data = {key: value for key, value in obj_data.items() if key in model_columns}
            
            # 모델 인스턴스 생성
            db_obj = self.model(**filtered_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            # Primary key 필드 찾기
            pk_field = None
            for column in self.model.__table__.primary_key.columns:
                pk_field = column.name
                break
            pk_value = getattr(db_obj, pk_field, 'N/A') if pk_field else 'N/A'
            logger.info(f"✅ {self.model.__name__} 생성 완료 - {pk_field}: {pk_value}")
            return db_obj
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ {self.model.__name__} 생성 실패 - 오류: {str(e)}")
            raise
    
    def update(
        self, 
        db: Session, 
        db_obj: ModelType, 
        obj_in: UpdateSchemaType,
        **kwargs
    ) -> ModelType:
        """
        기존 레코드 수정
        
        Args:
            db: 데이터베이스 세션
            db_obj: 수정할 모델 인스턴스
            obj_in: 수정할 데이터 스키마
            **kwargs: 추가 필드 값
            
        Returns:
            수정된 모델 인스턴스
        """
        try:
            # Pydantic 모델을 딕셔너리로 변환 (None 값 제외)
            if hasattr(obj_in, 'dict'):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = {k: v for k, v in obj_in.items() if v is not None}
            
            # 추가 필드 병합
            obj_data.update(kwargs)
            
            # 공통 필드 설정
            if hasattr(self.model, 'last_updt_pnttm'):
                obj_data['last_updt_pnttm'] = datetime.now()
            
            # 필드 업데이트
            for field, value in obj_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            
            logger.info(f"✅ {self.model.__name__} 수정 완료 - ID: {getattr(db_obj, 'id', 'N/A')}")
            return db_obj
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ {self.model.__name__} 수정 실패 - 오류: {str(e)}")
            raise
    
    def delete(self, db: Session, id: Any) -> Optional[ModelType]:
        """
        레코드 삭제 (물리적 삭제)
        
        Args:
            db: 데이터베이스 세션
            id: 삭제할 레코드의 ID
            
        Returns:
            삭제된 모델 인스턴스 또는 None
        """
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj:
                db.delete(obj)
                db.commit()
                logger.info(f"✅ {self.model.__name__} 삭제 완료 - ID: {id}")
                return obj
            return None
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ {self.model.__name__} 삭제 실패 - ID: {id}, 오류: {str(e)}")
            raise
    
    def soft_delete(self, db: Session, id: Any, user_id: str) -> Optional[ModelType]:
        """
        레코드 논리적 삭제 (delete_at 플래그 사용)
        
        Args:
            db: 데이터베이스 세션
            id: 삭제할 레코드의 ID
            user_id: 삭제 수행자 ID
            
        Returns:
            삭제된 모델 인스턴스 또는 None
        """
        try:
            obj = db.query(self.model).filter(self.model.id == id).first()
            if obj and hasattr(obj, 'delete_at'):
                obj.delete_at = 'Y'
                if hasattr(obj, 'last_updusr_id'):
                    obj.last_updusr_id = user_id
                if hasattr(obj, 'last_updt_pnttm'):
                    obj.last_updt_pnttm = datetime.now()
                
                db.add(obj)
                db.commit()
                db.refresh(obj)
                
                logger.info(f"✅ {self.model.__name__} 논리적 삭제 완료 - ID: {id}")
                return obj
            return None
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"❌ {self.model.__name__} 논리적 삭제 실패 - ID: {id}, 오류: {str(e)}")
            raise
    
    def exists(self, db: Session, **filters) -> bool:
        """
        레코드 존재 여부 확인
        
        Args:
            db: 데이터베이스 세션
            **filters: 필터 조건
            
        Returns:
            레코드 존재 여부
        """
        try:
            query = db.query(self.model)
            
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            
            return query.first() is not None
            
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 존재 확인 실패 - 오류: {str(e)}")
            raise
    
    def get_active(self, db: Session, **filters) -> List[ModelType]:
        """
        활성 상태인 레코드만 조회 (use_at='Y', delete_at='N')
        
        Args:
            db: 데이터베이스 세션
            **filters: 추가 필터 조건
            
        Returns:
            활성 상태인 모델 인스턴스 리스트
        """
        try:
            query = db.query(self.model)
            
            # 기본 활성 조건
            if hasattr(self.model, 'use_at'):
                query = query.filter(self.model.use_at == 'Y')
            if hasattr(self.model, 'delete_at'):
                query = query.filter(self.model.delete_at == 'N')
            
            # 추가 필터 적용
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
            
            return query.all()
            
        except SQLAlchemyError as e:
            logger.error(f"❌ {self.model.__name__} 활성 레코드 조회 실패 - 오류: {str(e)}")
            raise
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터베이스 사용자 확인 스크립트

현재 데이터베이스에 등록된 사용자들을 확인합니다.
"""

import sys
import os
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user_models import UserInfo
from app.services.auth_service import AuthorInfoService
from passlib.context import CryptContext

# 비밀번호 해시 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def check_existing_users():
    """기존 사용자 확인"""
    db = SessionLocal()
    try:
        print("=" * 60)
        print("데이터베이스 사용자 확인")
        print("=" * 60)
        
        # 모든 사용자 조회
        users = db.query(UserInfo).all()
        
        if not users:
            print("❌ 데이터베이스에 사용자가 없습니다.")
            print("\n테스트용 사용자를 생성하시겠습니까? (y/n): ", end="")
            response = input().lower().strip()
            
            if response == 'y':
                create_test_user(db)
            return
        
        print(f"✅ 총 {len(users)}명의 사용자가 등록되어 있습니다.\n")
        
        for i, user in enumerate(users, 1):
            print(f"{i}. 사용자 ID: {user.user_id}")
            print(f"   사용자명: {user.user_nm}")
            print(f"   이메일: {user.email_adres or 'N/A'}")
            print(f"   상태: {'활성' if user.lock_at == 'N' else '잠금'}")
            print(f"   생성일: {user.frst_regist_pnttm}")
            print()
        
        # 테스트용 사용자 확인
        test_user = db.query(UserInfo).filter(UserInfo.user_id == "admin").first()
        if test_user:
            print("✅ 테스트용 'admin' 사용자가 존재합니다.")
            
            # 비밀번호 확인
            test_password = "admin123"
            if pwd_context.verify(test_password, test_user.password):
                print(f"✅ 비밀번호 '{test_password}'가 올바릅니다.")
            else:
                print(f"❌ 비밀번호 '{test_password}'가 올바르지 않습니다.")
                print("   실제 해시된 비밀번호:", test_user.password[:50] + "...")
        else:
            print("❌ 테스트용 'admin' 사용자가 없습니다.")
            print("\n테스트용 사용자를 생성하시겠습니까? (y/n): ", end="")
            response = input().lower().strip()
            
            if response == 'y':
                create_test_user(db)
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        db.close()

def create_test_user(db: Session):
    """테스트용 사용자 생성"""
    try:
        print("\n테스트용 사용자 생성 중...")
        
        # 테스트 사용자 데이터
        test_user_data = {
            "user_id": "admin",
            "user_nm": "관리자",
            "password": pwd_context.hash("admin123"),
            "email_adres": "admin@test.com",
            "emplyr_sttus_code": "P",
            "lock_at": "N",
            "lock_cnt": 0,
            "esntl_id": "admin-test-001"
        }
        
        # 사용자 생성
        test_user = UserInfo(**test_user_data)
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print("✅ 테스트용 사용자가 생성되었습니다.")
        print(f"   사용자 ID: {test_user.user_id}")
        print(f"   비밀번호: admin123")
        print(f"   사용자명: {test_user.user_nm}")
        
    except Exception as e:
        print(f"❌ 테스트 사용자 생성 실패: {str(e)}")
        db.rollback()

def test_authentication():
    """인증 테스트"""
    db = SessionLocal()
    try:
        print("\n=" * 60)
        print("인증 테스트")
        print("=" * 60)
        
        auth_service = AuthorInfoService()
        
        # admin 사용자로 인증 테스트
        user_info = auth_service.authenticate(db, "admin", "admin123")
        
        if user_info:
            print("✅ 인증 성공!")
            print(f"   사용자 ID: {user_info.user_id}")
            print(f"   사용자명: {user_info.user_nm}")
            print(f"   이메일: {user_info.email_adres}")
        else:
            print("❌ 인증 실패")
            
    except Exception as e:
        print(f"❌ 인증 테스트 오류: {str(e)}")
    finally:
        db.close()

def main():
    """메인 함수"""
    try:
        check_existing_users()
        test_authentication()
        
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
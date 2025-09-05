#!/usr/bin/env python3
"""
기본 관리자 사용자 생성 스크립트

이 스크립트는 시스템 초기 설정 시 기본 관리자 계정을 생성합니다.
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database.database import SessionLocal
from app.models.user_models import UserInfo

# 비밀번호 해시화 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """
    기본 관리자 사용자를 생성합니다.
    """
    db: Session = SessionLocal()
    
    try:
        # 기존 admin 사용자 확인
        existing_admin = db.query(UserInfo).filter(UserInfo.user_id == "admin").first()
        if existing_admin:
            print("✅ 관리자 사용자가 이미 존재합니다.")
            return
        
        # 비밀번호 해시화
        hashed_password = pwd_context.hash("admin123")
        
        # 관리자 사용자 생성
        admin_user = UserInfo(
            user_id="admin",
            esntl_id="admin",
            user_nm="관리자",
            password=hashed_password,
            email_adres="admin@example.com",
            orgnzt_id="ORG001",
            emplyr_sttus_code="1",
            empl_no="EMP001",
            group_id="ADMIN",
            sbscrb_de=datetime.now(),
            frst_regist_pnttm=datetime.now(),
            frst_register_id="system",
            lock_at="N",
            lock_cnt=Decimal(0)
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("🎉 관리자 사용자가 성공적으로 생성되었습니다!")
        print(f"   - 사용자 ID: {admin_user.user_id}")
        print(f"   - 사용자명: {admin_user.user_nm}")
        print(f"   - 이메일: {admin_user.email_adres}")
        print(f"   - 비밀번호: admin123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 관리자 사용자 생성 실패: {str(e)}")
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 기본 관리자 사용자 생성을 시작합니다...")
    create_admin_user()
    print("✅ 작업이 완료되었습니다.")
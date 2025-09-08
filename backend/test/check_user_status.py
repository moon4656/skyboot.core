#!/usr/bin/env python3
"""
사용자 상태 확인 및 수정 스크립트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_models import UserInfo
from app.services.auth_service import AuthorInfoService
import bcrypt

def check_and_fix_user_status():
    """
    사용자 상태를 확인하고 필요시 수정합니다.
    """
    db = next(get_db())
    
    try:
        # admin 사용자 조회
        user = db.query(UserInfo).filter(UserInfo.user_id == "admin").first()
        
        if user:
            print(f"📋 사용자 정보:")
            print(f"   - 사용자 ID: {user.user_id}")
            print(f"   - 사용자명: {user.user_nm}")
            print(f"   - 이메일: {user.email_adres}")
            print(f"   - 상태 코드: {user.emplyr_sttus_code}")
            print(f"   - 잠금 상태: {user.lock_at}")
            print(f"   - 잠금 횟수: {user.lock_cnt}")
            print(f"   - 사용 여부: {getattr(user, 'use_at', 'N/A')}")
            
            # 상태 코드가 '1'이 아니면 수정
            if user.emplyr_sttus_code != '1':
                print(f"\n🔧 상태 코드를 '1'로 변경합니다...")
                user.emplyr_sttus_code = '1'
                
            # 잠금 상태가 'Y'이면 해제
            if user.lock_at == 'Y':
                print(f"🔓 계정 잠금을 해제합니다...")
                user.lock_at = 'N'
                user.lock_cnt = 0
                
            # 사용 여부가 'N'이면 'Y'로 변경
            if hasattr(user, 'use_at') and user.use_at == 'N':
                print(f"✅ 사용 여부를 'Y'로 변경합니다...")
                user.use_at = 'Y'
                
            db.commit()
            print(f"\n✅ 사용자 상태 업데이트 완료")
            
            # 비밀번호 검증 테스트
            print(f"\n🔐 비밀번호 검증 테스트...")
            auth_service = AuthorInfoService()
            
            # 저장된 비밀번호 해시 확인
            print(f"저장된 비밀번호 해시: {user.password[:50]}...")
            
            # 비밀번호 검증
            is_valid = auth_service.verify_password("admin123", user.password)
            print(f"비밀번호 'admin123' 검증 결과: {is_valid}")
            
            if not is_valid:
                print(f"\n🔧 비밀번호를 다시 설정합니다...")
                new_hash = auth_service.hash_password("admin123")
                user.password = new_hash
                db.commit()
                print(f"✅ 비밀번호 재설정 완료")
                
                # 다시 검증
                is_valid = auth_service.verify_password("admin123", user.password)
                print(f"재설정 후 비밀번호 검증 결과: {is_valid}")
            
            # 최종 인증 테스트
            print(f"\n🧪 최종 인증 테스트...")
            authenticated_user = auth_service.authenticate(db, "admin", "admin123")
            
            if authenticated_user:
                print(f"✅ 인증 성공!")
                print(f"   - 인증된 사용자: {authenticated_user.user_id}")
                print(f"   - 상태 코드: {authenticated_user.emplyr_sttus_code}")
            else:
                print(f"❌ 인증 실패")
                
        else:
            print(f"❌ 'admin' 사용자를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_and_fix_user_status()
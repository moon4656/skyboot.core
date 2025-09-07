#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사용자 활성화 스크립트

테스트용 사용자를 활성화합니다.
"""

import sys
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.models.user_models import UserInfo
from datetime import datetime

def activate_user(user_id: str = "admin"):
    """사용자 활성화"""
    db = SessionLocal()
    try:
        print(f"사용자 '{user_id}' 활성화 중...")
        
        # 사용자 조회
        user = db.query(UserInfo).filter(UserInfo.user_id == user_id).first()
        
        if not user:
            print(f"❌ 사용자 '{user_id}'를 찾을 수 없습니다.")
            return False
        
        print(f"현재 상태:")
        print(f"  - 사용자 상태 코드: {user.emplyr_sttus_code}")
        print(f"  - 잠금 상태: {user.lock_at}")
        print(f"  - 잠금 횟수: {user.lock_cnt}")
        
        # 사용자 활성화
        user.emplyr_sttus_code = "P"  # P: 활성
        user.lock_at = "N"  # N: 잠금 해제
        user.lock_cnt = 0  # 잠금 횟수 초기화
        user.last_updt_pnttm = datetime.now()
        user.last_updusr_id = "SYSTEM"
        
        db.commit()
        db.refresh(user)
        
        print(f"✅ 사용자 '{user_id}'가 활성화되었습니다.")
        print(f"업데이트된 상태:")
        print(f"  - 사용자 상태 코드: {user.emplyr_sttus_code}")
        print(f"  - 잠금 상태: {user.lock_at}")
        print(f"  - 잠금 횟수: {user.lock_cnt}")
        
        return True
        
    except Exception as e:
        print(f"❌ 사용자 활성화 실패: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """메인 함수"""
    try:
        print("=" * 60)
        print("사용자 활성화")
        print("=" * 60)
        
        success = activate_user("admin")
        
        if success:
            print("\n이제 로그인 테스트를 다시 실행할 수 있습니다.")
        else:
            print("\n사용자 활성화에 실패했습니다.")
            
    except KeyboardInterrupt:
        print("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
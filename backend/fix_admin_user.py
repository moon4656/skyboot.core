#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
admin 사용자 상태 코드 수정 스크립트

admin 사용자의 emplyr_sttus_code를 '1'로 업데이트하여 로그인이 가능하도록 합니다.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def fix_admin_user():
    """
    admin 사용자의 상태 코드를 수정합니다.
    """
    try:
        # 데이터베이스 연결
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'skybootcore'),
            user=os.getenv('DB_USER', 'skybootcore'),
            password=os.getenv('DB_PASSWORD', 'skybootcore123!')
        )
        
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("🔍 admin 사용자 현재 상태 확인...")
        
        # 현재 admin 사용자 상태 확인
        cursor.execute("""
            SELECT user_id, user_nm, emplyr_sttus_code, lock_at
            FROM skybootcore.tb_userinfo 
            WHERE user_id = 'admin'
        """)
        
        user = cursor.fetchone()
        if user:
            print(f"현재 상태: user_id={user['user_id']}, emplyr_sttus_code={user['emplyr_sttus_code']}, lock_at={user['lock_at']}")
            
            # emplyr_sttus_code를 '1'로 업데이트
            print("\n📝 admin 사용자 상태 코드 업데이트 중...")
            cursor.execute("""
                UPDATE skybootcore.tb_userinfo 
                SET emplyr_sttus_code = '1',
                    lock_at = 'N',
                    lock_cnt = 0,
                    last_updt_pnttm = CURRENT_TIMESTAMP,
                    last_updusr_id = 'system'
                WHERE user_id = 'admin'
            """)
            
            # 변경사항 커밋
            conn.commit()
            
            # 업데이트 후 상태 확인
            cursor.execute("""
                SELECT user_id, user_nm, emplyr_sttus_code, lock_at, lock_cnt
                FROM skybootcore.tb_userinfo 
                WHERE user_id = 'admin'
            """)
            
            updated_user = cursor.fetchone()
            print(f"\n✅ 업데이트 완료!")
            print(f"업데이트 후 상태: user_id={updated_user['user_id']}, emplyr_sttus_code={updated_user['emplyr_sttus_code']}, lock_at={updated_user['lock_at']}, lock_cnt={updated_user['lock_cnt']}")
            
        else:
            print("❌ admin 사용자를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_admin_user()
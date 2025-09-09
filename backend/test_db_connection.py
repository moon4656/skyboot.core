#!/usr/bin/env python3
"""
데이터베이스 연결 테스트 스크립트
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_database_connection():
    """
    데이터베이스 연결을 테스트합니다.
    """
    try:
        # 환경 변수에서 데이터베이스 URL 가져오기
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL 환경 변수가 설정되지 않았습니다.")
            return False
        
        print(f"🔗 데이터베이스 연결 시도: {database_url.replace(os.getenv('DB_PASSWORD', ''), '***')}")
        
        # 데이터베이스 엔진 생성
        engine = create_engine(database_url)
        
        # 연결 테스트
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
            if test_value == 1:
                print("✅ 데이터베이스 연결 성공!")
                
                # 테이블 존재 확인 (public 스키마)
                public_tables_result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
                
                public_tables = [row[0] for row in public_tables_result.fetchall()]
                print(f"📋 public 스키마 테이블 ({len(public_tables)}개): {', '.join(public_tables)}")
                
                # skybootcore 스키마 테이블 확인
                skyboot_tables_result = connection.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'skybootcore'
                    ORDER BY table_name
                """))
                
                skyboot_tables = [row[0] for row in skyboot_tables_result.fetchall()]
                print(f"📋 skybootcore 스키마 테이블 ({len(skyboot_tables)}개): {', '.join(skyboot_tables)}")
                
                # 사용자 테이블 확인
                if 'tb_userinfo' in skyboot_tables:
                    print("✅ tb_userinfo 테이블이 skybootcore 스키마에 존재합니다.")
                    
                    # tb_userinfo 테이블에서 사용자 수 확인
                    user_count_query = text("SELECT COUNT(*) FROM skybootcore.tb_userinfo")
                    user_count = connection.execute(user_count_query).scalar()
                    print(f"📊 tb_userinfo 테이블 사용자 수: {user_count}")
                    
                    # admin 사용자 상세 정보 확인
                    admin_query = text("""
                        SELECT user_id, user_nm, emplyr_sttus_code, password, lock_at, lock_cnt 
                        FROM skybootcore.tb_userinfo 
                        WHERE user_id = 'admin'
                    """)
                    admin_result = connection.execute(admin_query).fetchone()
                    if admin_result:
                        print(f"👤 admin 사용자 상세 정보:")
                        print(f"   - user_id: {admin_result[0]}")
                        print(f"   - user_nm: {admin_result[1]}")
                        print(f"   - emplyr_sttus_code: {admin_result[2]}")
                        print(f"   - password (해시): {admin_result[3][:50]}...")
                        print(f"   - lock_at: {admin_result[4]}")
                        print(f"   - lock_cnt: {admin_result[5]}")
                    else:
                        print("❌ admin 사용자를 찾을 수 없습니다.")
                        
                    # 모든 사용자의 상태 코드 확인
                    all_users_query = text("""
                        SELECT user_id, user_nm, emplyr_sttus_code 
                        FROM skybootcore.tb_userinfo 
                        ORDER BY user_id
                    """)
                    all_users = connection.execute(all_users_query).fetchall()
                    print(f"\n📋 모든 사용자 상태:")
                    for user in all_users:
                        print(f"   - {user[0]} ({user[1]}): 상태코드 '{user[2]}'")
                else:
                    print("⚠️ tb_userinfo 테이블이 없습니다.")
                
                return True
            else:
                print("❌ 데이터베이스 연결 테스트 실패")
                return False
                
    except Exception as e:
        print(f"❌ 데이터베이스 연결 오류: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 데이터베이스 연결 테스트 시작...")
    success = test_database_connection()
    
    if success:
        print("\n✅ 모든 테스트 완료!")
        sys.exit(0)
    else:
        print("\n❌ 테스트 실패!")
        sys.exit(1)
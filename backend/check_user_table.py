import psycopg2
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

try:
    # 데이터베이스 연결
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'skyboot_core'),
        user=os.getenv('DB_USER', 'skyboot_user'),
        password=os.getenv('DB_PASSWORD', 'skyboot_password')
    )
    
    cur = conn.cursor()
    
    # 사용자 테이블 구조 확인
    print("=== tb_userinfo 테이블 구조 ===")
    cur.execute("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'tb_userinfo' AND table_schema = 'skybootcore'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    for col in columns:
        print(f"컬럼: {col[0]}, 타입: {col[1]}, NULL 허용: {col[2]}, 기본값: {col[3]}")
    
    # admin 사용자 확인
    print("\n=== admin 사용자 확인 ===")
    cur.execute("SELECT user_id, user_nm, password FROM skybootcore.tb_userinfo WHERE user_id = 'admin'")
    admin_user = cur.fetchone()
    
    if admin_user:
        print(f"사용자 ID: {admin_user[0]}")
        print(f"사용자명: {admin_user[1]}")
        print(f"비밀번호 해시: {admin_user[2][:20]}...")
    else:
        print("admin 사용자를 찾을 수 없습니다.")
    
    conn.close()
    print("\n✅ 테이블 구조 확인 완료")
    
except Exception as e:
    print(f"❌ 오류 발생: {e}")
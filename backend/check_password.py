from app.services.auth_service import AuthorInfoService
from app.database.database import get_db

def check_admin_password():
    db = next(get_db())
    try:
        auth = AuthorInfoService()
        user = auth.get_by_user_id(db, 'admin')
        
        if user:
            print(f"✅ 사용자 발견: {user.user_id}")
            print(f"📝 비밀번호 해시: {user.password[:50]}...")
            print(f"🔐 비밀번호 검증 (admin123): {auth.verify_password('admin123', user.password)}")
            print(f"🔐 비밀번호 검증 (admin): {auth.verify_password('admin', user.password)}")
            print(f"📊 계정 상태: {user.emplyr_sttus_code}")
            print(f"🔒 잠금 상태: {user.lock_at}")
        else:
            print("❌ admin 사용자를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_admin_password()
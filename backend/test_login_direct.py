from app.database.database import get_db
from app.services.auth_service import AuthorInfoService
from app.schemas.auth_schemas import UserLoginRequest

# 서비스 초기화
auth_service = AuthorInfoService()
db = next(get_db())

# 로그인 테스트
login_data = UserLoginRequest(user_id="admin", password="admin123")

print("🔐 로그인 테스트 시작...")
print(f"사용자 ID: {login_data.user_id}")
print(f"비밀번호: {login_data.password}")

# 인증 테스트
user = auth_service.authenticate(db, login_data.user_id, login_data.password)
if user:
    print(f"✅ 인증 성공: {user.user_id} ({user.user_nm})")
    
    # 토큰 생성 테스트
    tokens = auth_service.authenticate_and_create_tokens(db, login_data.user_id, login_data.password)
    if tokens:
        print(f"✅ 토큰 생성 성공")
        print(f"액세스 토큰: {tokens['access_token'][:50]}...")
        print(f"리프레시 토큰: {tokens['refresh_token'][:50]}...")
    else:
        print("❌ 토큰 생성 실패")
else:
    print("❌ 인증 실패")

db.close()
print("🏁 테스트 완료")
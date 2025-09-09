import bcrypt
from app.database.database import get_db
from app.models.user_models import UserInfo

# 데이터베이스 연결
db = next(get_db())

# admin 사용자 조회
user = db.query(UserInfo).filter(UserInfo.user_id == 'admin').first()

if user:
    print(f'사용자 ID: {user.user_id}')
    print(f'저장된 비밀번호 해시: {user.password[:50]}...')  # 처음 50자만 출력
    
    # 비밀번호 검증 테스트
    test_passwords = ['admin123', 'admin', 'password', '123456']
    
    for pwd in test_passwords:
        try:
            is_valid = bcrypt.checkpw(
                pwd.encode('utf-8'), 
                user.password.encode('utf-8')
            )
            print(f'비밀번호 "{pwd}": {"✅ 일치" if is_valid else "❌ 불일치"}')
        except Exception as e:
            print(f'비밀번호 "{pwd}": ❌ 오류 - {str(e)}')
else:
    print('❌ admin 사용자가 존재하지 않습니다')

db.close()
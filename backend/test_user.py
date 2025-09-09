from app.database.database import get_db
from app.models.user_models import UserInfo

# 데이터베이스 연결
db = next(get_db())

# admin 사용자 조회
user = db.query(UserInfo).filter(UserInfo.user_id == 'admin').first()

if user:
    print(f'✅ 사용자 존재: {user.user_id}')
    print(f'사용자명: {user.user_nm}')
    print(f'이메일: {user.email_adres}')
    print(f'사용자상태코드: {user.emplyr_sttus_code}')
    print(f'잠금여부: {user.lock_at}')
else:
    print('❌ admin 사용자가 존재하지 않습니다')

db.close()
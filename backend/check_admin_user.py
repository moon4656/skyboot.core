from app.database.database import get_db
from app.models.user_models import UserInfo

db = next(get_db())
user = db.query(UserInfo).filter(UserInfo.user_id == 'admin').first()

print('✅ admin 사용자 존재:', user is not None)
if user:
    print(f'사용자 정보: ID={user.user_id}, 이름={user.user_nm}, 상태={user.emplyr_sttus_code}, 잠금={user.lock_at}')
    print(f'비밀번호 해시: {user.password[:50]}...')
else:
    print('❌ admin 사용자가 존재하지 않습니다.')
    
db.close()
from sqlalchemy import inspect
from app.database.database import engine

inspector = inspect(engine)
tables = inspector.get_table_names(schema='skybootcore')

print(f'총 테이블 수: {len(tables)}')
print('\n현재 데이터베이스의 모든 테이블:')
for table in sorted(tables):
    print(f'  - {table}')

# database.sql에 정의된 테이블 목록
expected_tables = [
    'tb_authorinfo', 'tb_authormenu', 'tb_bbs', 'tb_bbsmaster',
    'tb_cmmn_code', 'tb_cmmn_grp_code', 'tb_comment', 'tb_file',
    'tb_filedetail', 'tb_loginlog', 'tb_menuinfo', 'tb_org',
    'tb_progrmlist', 'tb_syslog', 'tb_userinfo', 'tb_weblog', 'tb_zip'
]

print('\ndatabase.sql과 비교:')
missing_tables = []
for expected in expected_tables:
    if expected in tables:
        print(f'  ✓ {expected} - 존재함')
    else:
        print(f'  ✗ {expected} - 누락됨')
        missing_tables.append(expected)

if missing_tables:
    print(f'\n누락된 테이블: {missing_tables}')
else:
    print('\n모든 테이블이 성공적으로 생성되었습니다!')
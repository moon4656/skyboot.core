#!/usr/bin/env python3
"""WebLog 테이블에 누락된 컬럼들을 추가하는 스크립트"""

from app.database.database import engine
from sqlalchemy import text

def add_weblog_columns():
    """WebLog 테이블에 누락된 컬럼들을 추가합니다."""
    
    columns_to_add = [
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS rqester_nm VARCHAR(60);",
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS trget_menu_nm VARCHAR(60);",
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS process_se_code VARCHAR(20);",
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS process_cn VARCHAR(2000);",
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS process_time NUMERIC(10,3);",
        "ALTER TABLE skybootcore.tb_weblog ADD COLUMN IF NOT EXISTS rqest_de TIMESTAMP;"
    ]
    
    try:
        with engine.connect() as conn:
            for sql in columns_to_add:
                print(f"실행 중: {sql}")
                conn.execute(text(sql))
            conn.commit()
            print("✅ WebLog 테이블에 모든 컬럼 추가 완료")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        raise

if __name__ == "__main__":
    add_weblog_columns()
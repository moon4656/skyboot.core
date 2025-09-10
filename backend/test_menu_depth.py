#!/usr/bin/env python3

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.services.menu_service import MenuInfoService
    from app.database.database import get_db
    from app.models.menu_models import MenuInfo
    from sqlalchemy.orm import Session
    from datetime import datetime
    
    def create_test_menus():
        """테스트용 메뉴 생성"""
        db: Session = next(get_db())
        
        try:
            # 기존 테스트 메뉴 삭제
            db.query(MenuInfo).filter(MenuInfo.menu_no.like('TEST_%')).delete()
            db.commit()
            
            # 테스트 메뉴 생성
            test_menus = [
                # 레벨 1 (루트)
                MenuInfo(
                    menu_no='TEST_ROOT',
                    menu_nm='테스트 루트 메뉴',
                    progrm_file_nm='test_root.html',
                    upper_menu_no=None,
                    menu_ordr=1,
                    menu_dc='테스트용 루트 메뉴',
                    display_yn='Y',
                    frst_register_id='system',
                    frst_regist_pnttm=datetime.now(),
                    last_updusr_id='system',
                    last_updt_pnttm=datetime.now()
                ),
                # 레벨 2
                MenuInfo(
                    menu_no='TEST_L2_1',
                    menu_nm='레벨2 메뉴1',
                    progrm_file_nm='test_l2_1.html',
                    upper_menu_no='TEST_ROOT',
                    menu_ordr=1,
                    menu_dc='레벨2 테스트 메뉴',
                    display_yn='Y',
                    frst_register_id='system',
                    frst_regist_pnttm=datetime.now(),
                    last_updusr_id='system',
                    last_updt_pnttm=datetime.now()
                ),
                # 레벨 3
                MenuInfo(
                    menu_no='TEST_L3_1',
                    menu_nm='레벨3 메뉴1',
                    progrm_file_nm='test_l3_1.html',
                    upper_menu_no='TEST_L2_1',
                    menu_ordr=1,
                    menu_dc='레벨3 테스트 메뉴',
                    display_yn='Y',
                    frst_register_id='system',
                    frst_regist_pnttm=datetime.now(),
                    last_updusr_id='system',
                    last_updt_pnttm=datetime.now()
                ),
                # 레벨 4
                MenuInfo(
                    menu_no='TEST_L4_1',
                    menu_nm='레벨4 메뉴1',
                    progrm_file_nm='test_l4_1.html',
                    upper_menu_no='TEST_L3_1',
                    menu_ordr=1,
                    menu_dc='레벨4 테스트 메뉴',
                    display_yn='Y',
                    frst_register_id='system',
                    frst_regist_pnttm=datetime.now(),
                    last_updusr_id='system',
                    last_updt_pnttm=datetime.now()
                ),
                # 레벨 5
                MenuInfo(
                    menu_no='TEST_L5_1',
                    menu_nm='레벨5 메뉴1',
                    progrm_file_nm='test_l5_1.html',
                    upper_menu_no='TEST_L4_1',
                    menu_ordr=1,
                    menu_dc='레벨5 테스트 메뉴',
                    display_yn='Y',
                    frst_register_id='system',
                    frst_regist_pnttm=datetime.now(),
                    last_updusr_id='system',
                    last_updt_pnttm=datetime.now()
                )
            ]
            
            for menu in test_menus:
                db.add(menu)
            
            db.commit()
            print("✅ 테스트 메뉴 생성 완료")
            
            # 메뉴 구조 출력
            print("\n=== 생성된 테스트 메뉴 구조 ===")
            print("TEST_ROOT (레벨 1)")
            print("  └─ TEST_L2_1 (레벨 2)")
            print("      └─ TEST_L3_1 (레벨 3)")
            print("          └─ TEST_L4_1 (레벨 4)")
            print("              └─ TEST_L5_1 (레벨 5)")
            
        except Exception as e:
            db.rollback()
            print(f"❌ 테스트 메뉴 생성 실패: {e}")
        finally:
            db.close()
    
    def test_menu_copy():
        """메뉴 복사 테스트"""
        db: Session = next(get_db())
        menu_service = MenuInfoService()
        
        try:
            print("\n=== 메뉴 복사 테스트 시작 ===")
            
            # TEST_L2_1을 TEST_ROOT 하위에 복사 (하위 메뉴 포함)
            # 이 경우 깊이는: TEST_ROOT(1) -> 복사된메뉴(2) -> TEST_L3_1(3) -> TEST_L4_1(4) = 4레벨
            result = menu_service.copy_menu(
                db=db,
                source_menu_id='TEST_L2_1',
                new_menu_id='TEST_COPY_L2',
                new_menu_nm='복사된 레벨2 메뉴',
                new_parent_id='TEST_ROOT',
                copy_children=True,
                user_id='test_user'
            )
            
            print(f"✅ 메뉴 복사 성공: {result.menu_no}")
            
        except Exception as e:
            print(f"❌ 메뉴 복사 실패: {e}")
        finally:
            db.close()
    
    if __name__ == "__main__":
        create_test_menus()
        test_menu_copy()
        
except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    print("현재 작업 디렉토리:", os.getcwd())
    print("Python 경로:", sys.path[:3])
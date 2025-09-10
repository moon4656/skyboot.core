from app.database.database import get_db
from app.services.menu_service import MenuInfoService
from app.models.menu_models import MenuInfo
from datetime import datetime

def clean_test_menus():
    """테스트로 생성된 메뉴들 정리"""
    db = next(get_db())
    service = MenuInfoService()
    
    try:
        print("=== 테스트 메뉴 정리 시작 ===")
        
        # 복사 테스트 관련 메뉴들 찾기
        test_menus = db.query(MenuInfo).filter(
            MenuInfo.menu_nm.like('%복사 테스트%')
        ).all()
        
        print(f"발견된 테스트 메뉴 개수: {len(test_menus)}")
        
        for menu in test_menus:
            print(f"  - {menu.menu_nm} ({menu.menu_no})")
        
        # 하위 메뉴부터 삭제 (깊이 순으로)
        def get_menu_depth(menu_no):
            depth = 0
            current = menu_no
            while current:
                menu = db.query(MenuInfo).filter(MenuInfo.menu_no == current).first()
                if menu and menu.upper_menu_no:
                    depth += 1
                    current = menu.upper_menu_no
                else:
                    break
            return depth
        
        # 깊이 순으로 정렬 (깊은 것부터)
        test_menus.sort(key=lambda x: get_menu_depth(x.menu_no), reverse=True)
        
        print("\n=== 메뉴 삭제 시작 ===")
        for menu in test_menus:
            try:
                print(f"삭제 중: {menu.menu_nm} ({menu.menu_no})")
                db.delete(menu)
                db.commit()
                print(f"✅ 삭제 완료: {menu.menu_nm}")
            except Exception as e:
                print(f"❌ 삭제 실패: {menu.menu_nm} - {str(e)}")
                db.rollback()
        
        print("\n=== 정리 완료 ===")
        
        # 남은 하위 메뉴 확인
        remaining_children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900004').all()
        print(f"10900004의 남은 하위 메뉴 개수: {len(remaining_children)}")
        for child in remaining_children:
            print(f"  - {child.menu_nm} ({child.menu_no})")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_test_menus()
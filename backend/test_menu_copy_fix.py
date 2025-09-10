from app.database.database import get_db
from app.services.menu_service import MenuInfoService
from app.models.menu_models import MenuInfo
from datetime import datetime

def test_menu_copy():
    """메뉴 복사 테스트"""
    db = next(get_db())
    service = MenuInfoService()
    
    try:
        print("=== 메뉴 복사 테스트 시작 ===")
        
        # 원본 메뉴 확인
        source_menu = service.get_by_menu_id(db, '10900004')
        if not source_menu:
            print("원본 메뉴를 찾을 수 없습니다.")
            return
        
        print(f"원본 메뉴: {source_menu.menu_nm} ({source_menu.menu_no})")
        print(f"상위 메뉴: {source_menu.upper_menu_no}")
        
        # 하위 메뉴 확인
        children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900004').all()
        print(f"하위 메뉴 개수: {len(children)}")
        for child in children:
            print(f"  - {child.menu_nm} ({child.menu_no})")
        
        # 메뉴 복사 실행
        print("\n메뉴 복사 실행...")
        copied_menu = service.copy_menu(
            db=db,
            source_menu_id='10900004',
            new_menu_id='10900018',
            new_menu_nm='복사 테스트 수정됨',
            new_parent_id='10900000',
            copy_children=True,
            user_id='admin'
        )
        
        print(f"✅ 메뉴 복사 성공: {copied_menu.menu_nm} ({copied_menu.menu_no})")
        
        # 복사된 하위 메뉴 확인
        copied_children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900018').all()
        print(f"복사된 하위 메뉴 개수: {len(copied_children)}")
        for child in copied_children:
            print(f"  - {child.menu_nm} ({child.menu_no})")
        
    except Exception as e:
        print(f"❌ 메뉴 복사 실패: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_menu_copy()
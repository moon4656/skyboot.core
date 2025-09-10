from app.database.database import get_db
from app.services.menu_service import MenuInfoService
from app.models.menu_models import MenuInfo
from datetime import datetime

def debug_menu_depth():
    """메뉴 깊이 계산 디버깅"""
    db = next(get_db())
    service = MenuInfoService()
    
    try:
        print("=== 메뉴 깊이 계산 디버깅 ===")
        
        # 원본 메뉴 확인
        source_menu = service.get_by_menu_id(db, '10900004')
        if not source_menu:
            print("원본 메뉴를 찾을 수 없습니다.")
            return
        
        print(f"원본 메뉴: {source_menu.menu_nm} ({source_menu.menu_no})")
        print(f"상위 메뉴: {source_menu.upper_menu_no}")
        
        # 현재 메뉴의 깊이 계산
        current_depth = 0
        current_menu_no = source_menu.upper_menu_no
        print(f"\n=== 현재 메뉴 깊이 계산 ===")
        print(f"시작: {source_menu.menu_no}")
        
        while current_menu_no:
            current_depth += 1
            parent_menu = service.get_by_menu_id(db, current_menu_no)
            if parent_menu:
                print(f"레벨 {current_depth}: {parent_menu.menu_nm} ({parent_menu.menu_no})")
                current_menu_no = parent_menu.upper_menu_no
            else:
                break
        
        print(f"현재 메뉴 깊이: {current_depth}")
        
        # 하위 메뉴들의 최대 깊이 계산
        print(f"\n=== 하위 메뉴 최대 깊이 계산 ===")
        max_child_depth = service._get_max_child_depth(db, '10900004')
        print(f"하위 메뉴 최대 깊이: {max_child_depth}")
        
        # 전체 깊이 계산
        total_depth = current_depth + 1 + max_child_depth
        print(f"\n=== 전체 깊이 계산 ===")
        print(f"현재 메뉴 깊이: {current_depth}")
        print(f"복사될 메뉴 자체: +1")
        print(f"하위 메뉴 최대 깊이: {max_child_depth}")
        print(f"전체 예상 깊이: {total_depth}")
        
        # 하위 메뉴들 상세 확인
        print(f"\n=== 하위 메뉴 상세 확인 ===")
        children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900004').all()
        for child in children:
            child_depth = service._get_max_child_depth(db, child.menu_no)
            print(f"  - {child.menu_nm} ({child.menu_no}): 하위 깊이 {child_depth}")
            
            # 각 하위 메뉴의 하위 메뉴들도 확인
            grandchildren = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == child.menu_no).all()
            for grandchild in grandchildren:
                grandchild_depth = service._get_max_child_depth(db, grandchild.menu_no)
                print(f"    - {grandchild.menu_nm} ({grandchild.menu_no}): 하위 깊이 {grandchild_depth}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_menu_depth()
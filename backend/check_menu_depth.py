from app.database.database import get_db
from app.services.menu_service import MenuInfoService

def check_menu_depth(menu_id):
    db = next(get_db())
    service = MenuInfoService()
    
    menu = service.get_by_menu_id(db, menu_id)
    if not menu:
        print(f"메뉴를 찾을 수 없습니다: {menu_id}")
        return
    
    print(f"시작 메뉴: {menu.menu_nm} ({menu.menu_no})")
    print(f"상위 메뉴: {menu.upper_menu_no}")
    
    # 상위로 올라가면서 깊이 계산
    parent = menu.upper_menu_no
    depth = 0
    path = []
    
    current_menu = menu
    while current_menu:
        path.insert(0, f"레벨 {depth}: {current_menu.menu_nm} ({current_menu.menu_no})")
        if current_menu.upper_menu_no:
            parent_menu = service.get_by_menu_id(db, current_menu.upper_menu_no)
            current_menu = parent_menu
            depth += 1
        else:
            break
    
    print("\n메뉴 계층 구조:")
    for level in path:
        print(level)
    
    print(f"\n현재 메뉴의 깊이: {depth}")
    return depth

if __name__ == "__main__":
    depth = check_menu_depth('10900004')
    print(f"\n메뉴 10900004의 현재 깊이: {depth}")
    print(f"복사 시 하위 메뉴가 추가되면 깊이: {depth + 1}")
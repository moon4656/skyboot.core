from app.database.database import get_db
from app.services.menu_service import MenuInfoService

def check_copied_menu_structure():
    db = next(get_db())
    service = MenuInfoService()
    
    # 복사된 메뉴 확인
    copied_menu = service.get_by_menu_id(db, 'TEST_COPY_L5')
    if copied_menu:
        print(f"복사된 메뉴: {copied_menu.menu_nm}")
        
        # 하위 메뉴들 확인
        children = service.get_child_menus(db, 'TEST_COPY_L5')
        print(f"하위 메뉴 개수: {len(children)}")
        
        for child in children:
            print(f"  - {child.menu_no}: {child.menu_nm}")
            
            # 2레벨 하위 메뉴 확인
            grandchildren = service.get_child_menus(db, child.menu_no)
            for grandchild in grandchildren:
                print(f"    - {grandchild.menu_no}: {grandchild.menu_nm}")
                
                # 3레벨 하위 메뉴 확인
                great_grandchildren = service.get_child_menus(db, grandchild.menu_no)
                for ggchild in great_grandchildren:
                    print(f"      - {ggchild.menu_no}: {ggchild.menu_nm}")
                    
                    # 4레벨 하위 메뉴 확인 (max_depth=3이므로 없어야 함)
                    fourth_level = service.get_child_menus(db, ggchild.menu_no)
                    if fourth_level:
                        print(f"        ❌ 4레벨 메뉴가 존재함: {len(fourth_level)}개")
                        for fl in fourth_level:
                            print(f"          - {fl.menu_no}: {fl.menu_nm}")
                    else:
                        print(f"        ✅ 4레벨 메뉴 없음 (깊이 제한 적용됨)")
    else:
        print("복사된 메뉴를 찾을 수 없습니다.")

if __name__ == "__main__":
    check_copied_menu_structure()
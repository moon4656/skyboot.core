from app.database.database import get_db
from app.services.menu_service import MenuInfoService
from app.models.menu_models import MenuInfo
from datetime import datetime

def clean_all_test_menus():
    """모든 테스트 메뉴들 완전 정리"""
    db = next(get_db())
    
    try:
        print("=== 모든 테스트 메뉴 완전 정리 시작 ===")
        
        # 10900004의 모든 하위 메뉴 확인
        all_children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900004').all()
        print(f"10900004의 현재 하위 메뉴들:")
        for child in all_children:
            print(f"  - {child.menu_nm} ({child.menu_no})")
        
        # 원본 메뉴들만 남기고 모든 복사본 삭제
        original_menus = ['10900005', '10900006']  # 권한관리, 사용자권한
        
        menus_to_delete = []
        for child in all_children:
            if child.menu_no not in original_menus:
                menus_to_delete.append(child)
        
        print(f"\n삭제할 메뉴 개수: {len(menus_to_delete)}")
        
        # 재귀적으로 모든 하위 메뉴 찾기
        def find_all_descendants(menu_no, visited=None):
            if visited is None:
                visited = set()
            
            if menu_no in visited:
                return []
            
            visited.add(menu_no)
            descendants = []
            
            children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == menu_no).all()
            for child in children:
                descendants.append(child)
                descendants.extend(find_all_descendants(child.menu_no, visited))
            
            return descendants
        
        all_descendants = []
        for menu in menus_to_delete:
            descendants = find_all_descendants(menu.menu_no)
            all_descendants.extend(descendants)
            all_descendants.append(menu)
        
        # 중복 제거
        unique_menus = {}
        for menu in all_descendants:
            unique_menus[menu.menu_no] = menu
        
        print(f"삭제할 전체 메뉴 개수 (하위 포함): {len(unique_menus)}")
        
        # 깊이 순으로 정렬하여 삭제 (깊은 것부터)
        def get_menu_depth(menu_no):
            depth = 0
            current = menu_no
            visited = set()
            
            while current and current not in visited:
                visited.add(current)
                menu = db.query(MenuInfo).filter(MenuInfo.menu_no == current).first()
                if menu and menu.upper_menu_no:
                    depth += 1
                    current = menu.upper_menu_no
                else:
                    break
            return depth
        
        sorted_menus = sorted(unique_menus.values(), key=lambda x: get_menu_depth(x.menu_no), reverse=True)
        
        print("\n=== 메뉴 삭제 시작 ===")
        deleted_count = 0
        for menu in sorted_menus:
            try:
                print(f"삭제 중: {menu.menu_nm} ({menu.menu_no})")
                db.delete(menu)
                db.commit()
                deleted_count += 1
                print(f"✅ 삭제 완료: {menu.menu_nm}")
            except Exception as e:
                print(f"❌ 삭제 실패: {menu.menu_nm} - {str(e)}")
                db.rollback()
        
        print(f"\n=== 정리 완료 - 총 {deleted_count}개 메뉴 삭제 ===")
        
        # 최종 확인
        final_children = db.query(MenuInfo).filter(MenuInfo.upper_menu_no == '10900004').all()
        print(f"10900004의 최종 하위 메뉴 개수: {len(final_children)}")
        for child in final_children:
            print(f"  - {child.menu_nm} ({child.menu_no})")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clean_all_test_menus()
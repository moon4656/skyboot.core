import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { menuAPI } from '../api/client';

// 메뉴 아이템 타입 정의
export interface MenuItem {
  id: number;
  name: string;
  path?: string;
  icon?: string;
  parent_id?: number;
  order_num: number;
  is_active: boolean;
  children?: MenuItem[];
  component?: string;
  meta?: {
    requiresAuth?: boolean;
    roles?: string[];
    title?: string;
  };
}

export const useMenuStore = defineStore('menu', () => {
  // State
  const menuTree = ref<MenuItem[]>([]);
  const flatMenus = ref<MenuItem[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeMenus = computed(() => {
    // 최상위 루트 메뉴만 표시하도록 parent_id가 없거나 0/빈 값인 항목만 필터링합니다.
    return menuTree.value.filter(
      (menu) => menu.is_active && (menu.parent_id === undefined || menu.parent_id === null || menu.parent_id === 0)
    );
  });

  const getMenuById = computed(() => {
    return (id: number): MenuItem | undefined => {
      return flatMenus.value.find(menu => menu.id === id);
    };
  });

  const getMenuByPath = computed(() => {
    return (path: string): MenuItem | undefined => {
      return flatMenus.value.find(menu => menu.path === path);
    };
  });

  // 백엔드 응답을 프론트엔드 인터페이스로 변환하는 함수
  // parentId 매개변수를 추가하여 재귀적으로 변환 시 상위 메뉴 ID를 전달합니다.
  const transformMenuData = (backendMenu: any, parentId?: number): MenuItem => {
    // 백엔드에서 내려오는 필드가 상황에 따라 다를 수 있으므로 최대한 유연하게 매핑합니다.
    // 1) id / menu_id / menu_no 순으로 확인하여 숫자형 ID를 생성합니다.
    const rawId = backendMenu.id ?? backendMenu.menu_id ?? backendMenu.menu_no;
    const numericId = typeof rawId === 'number' ? rawId : parseInt(rawId || '0');

    // 2) path는 path / progrm_file_nm 순으로 확인합니다.
    const resolvedPath: string = backendMenu.path || backendMenu.progrm_file_nm || '';

    // 3) icon은 icon / relate_image_nm 순으로 확인합니다.
    const resolvedIcon: string = backendMenu.icon || backendMenu.relate_image_nm || '';

    const menuItem: MenuItem = {
      id: numericId,
      name: backendMenu.menu_nm || backendMenu.name || '',
      path: resolvedPath,
      icon: resolvedIcon,
      // 상위 메뉴 ID가 명시적으로 존재하면 해당 값을 사용하고, 그렇지 않은 경우 재귀 호출 시 전달된 parentId를 사용합니다.
      parent_id: backendMenu.upper_menu_no
        ? parseInt(backendMenu.upper_menu_no)
        : parentId,
      order_num: parseInt(backendMenu.menu_ordr || backendMenu.order_num || '0'),
      // "is_active"는 메뉴의 표시 여부(display_yn)만으로 판단합니다. 루트 메뉴(leaf_at = 'N')도 표시되어야 하므로 leaf_at 값은 고려하지 않습니다.
      is_active: backendMenu.display_yn !== 'N' && backendMenu.is_active !== false,
      // 위에서 정의한 transformMenuData는 parentId를 인수로 받으므로 명시적으로 전달합니다.
      children: Array.isArray(backendMenu.children)
        ? backendMenu.children.map((child: any) => transformMenuData(child, numericId))
        : [],
      component: resolvedPath,
      meta: {
        requiresAuth: true,
        title: backendMenu.menu_nm || backendMenu.name || ''
      }
    };
    return menuItem;
  };

  // Actions
  const fetchMenuTree = async (): Promise<void> => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await menuAPI.getMenuTree();
      console.log('Raw menu response:', response);
      
      // 백엔드 응답을 프론트엔드 형식으로 변환
      const transformedMenus = Array.isArray(response) 
        ? response.map(transformMenuData)
        : response.data 
          ? (Array.isArray(response.data) ? response.data.map(transformMenuData) : [transformMenuData(response.data)])
          : [transformMenuData(response)];
      
      menuTree.value = transformedMenus;
      console.log('Transformed menu tree:', menuTree.value);
      
      // 플랫 메뉴 리스트 생성 (검색 및 권한 체크용)
      flatMenus.value = flattenMenuTree(menuTree.value);
    } catch (err: any) {
      error.value = err.response?.data?.detail || '메뉴를 불러올 수 없습니다.';
      console.error('메뉴 트리 조회 실패:', err);
    } finally {
      isLoading.value = false;
    }
  };

  const fetchMenus = async (): Promise<void> => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await menuAPI.getMenus();
      flatMenus.value = response.data || [];
    } catch (err: any) {
      error.value = err.response?.data?.detail || '메뉴를 불러올 수 없습니다.';
      console.error('메뉴 목록 조회 실패:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // 메뉴 트리를 플랫 리스트로 변환하는 헬퍼 함수
  const flattenMenuTree = (menus: MenuItem[]): MenuItem[] => {
    const result: MenuItem[] = [];
    
    const flatten = (items: MenuItem[]) => {
      items.forEach(item => {
        result.push(item);
        if (item.children && item.children.length > 0) {
          flatten(item.children);
        }
      });
    };
    
    flatten(menus);
    return result;
  };

  // 사용자 권한에 따른 메뉴 필터링
  const filterMenusByPermission = (menus: MenuItem[], userRoles: string[] = []): MenuItem[] => {
    return menus.filter(menu => {
      // 메뉴가 비활성화된 경우 제외
      if (!menu.is_active) {
        return false;
      }

      // 권한이 필요한 메뉴인 경우 사용자 권한 체크
      if (menu.meta?.roles && menu.meta.roles.length > 0) {
        return menu.meta.roles.some(role => userRoles.includes(role));
      }

      // 권한 설정이 없는 메뉴는 모든 사용자에게 표시
      return true;
    }).map(menu => ({
      ...menu,
      children: menu.children ? filterMenusByPermission(menu.children, userRoles) : []
    }));
  };

  const clearError = (): void => {
    error.value = null;
  };

  const resetMenus = (): void => {
    menuTree.value = [];
    flatMenus.value = [];
    error.value = null;
  };

  return {
    // State
    menuTree,
    flatMenus,
    isLoading,
    error,
    
    // Getters
    activeMenus,
    getMenuById,
    getMenuByPath,
    
    // Actions
    fetchMenuTree,
    fetchMenus,
    filterMenusByPermission,
    clearError,
    resetMenus,
  };
});
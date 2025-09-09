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
    return menuTree.value.filter(menu => menu.is_active);
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

  // Actions
  const fetchMenuTree = async (): Promise<void> => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await menuAPI.getMenuTree();
      menuTree.value = response.data || [];
      
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
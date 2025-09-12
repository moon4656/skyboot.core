import { computed, onMounted } from 'vue'
import { useMenuStore } from '@/stores/menu'
import type { MenuTreeNode } from '@/services/api'

/**
 * 메뉴 관련 컴포저블
 * 메뉴 데이터 로딩, 검색, 네비게이션 등의 기능을 제공합니다.
 */
export function useMenu() {
  const menuStore = useMenuStore()
  
  // 메뉴 데이터 자동 로딩
  onMounted(async () => {
    if (!menuStore.hasMenuItems) {
      await menuStore.initializeMenu()
    }
  })
  
  // 메뉴 새로고침
  const refreshMenu = async () => {
    return await menuStore.fetchMenuTree('Y', true)
  }
  
  // 메뉴 트리를 플랫 리스트로 변환
  const flattenMenuTree = (items: MenuTreeNode[]): MenuTreeNode[] => {
    const result: MenuTreeNode[] = []
    
    const flatten = (nodes: MenuTreeNode[]) => {
      for (const node of nodes) {
        result.push(node)
        if (node.children && node.children.length > 0) {
          flatten(node.children)
        }
      }
    }
    
    flatten(items)
    return result
  }
  
  // 메뉴 검색
  const searchMenus = (keyword: string): MenuTreeNode[] => {
    if (!keyword.trim()) return []
    
    const flatMenus = flattenMenuTree(menuStore.menuItems)
    const lowerKeyword = keyword.toLowerCase()
    
    return flatMenus.filter(menu => 
      menu.name.toLowerCase().includes(lowerKeyword) ||
      (menu.description && menu.description.toLowerCase().includes(lowerKeyword))
    )
  }
  
  // 메뉴 필터링 (권한 기반)
  const filterMenusByPermission = (items: MenuTreeNode[], userPermissions: string[] = []): MenuTreeNode[] => {
    return items.filter(item => {
      // 권한이 필요하지 않은 메뉴는 항상 표시
      if (!item.permission_code) {
        return true
      }
      
      // 사용자가 해당 권한을 가지고 있는지 확인
      const hasPermission = userPermissions.includes(item.permission_code)
      
      // 자식 메뉴도 재귀적으로 필터링
      if (item.children && item.children.length > 0) {
        item.children = filterMenusByPermission(item.children, userPermissions)
        // 자식 메뉴가 있으면 부모 메뉴도 표시
        return hasPermission || item.children.length > 0
      }
      
      return hasPermission
    })
  }
  
  // 메뉴 트리에서 특정 레벨의 메뉴만 가져오기
  const getMenusByLevel = (level: number): MenuTreeNode[] => {
    if (level === 1) {
      return menuStore.menuItems
    }
    
    const getChildrenAtLevel = (items: MenuTreeNode[], currentLevel: number): MenuTreeNode[] => {
      if (currentLevel === level) {
        return items
      }
      
      const children: MenuTreeNode[] = []
      for (const item of items) {
        if (item.children && item.children.length > 0) {
          children.push(...getChildrenAtLevel(item.children, currentLevel + 1))
        }
      }
      return children
    }
    
    return getChildrenAtLevel(menuStore.menuItems, 1)
  }
  
  // 메뉴 통계 정보
  const menuStats = computed(() => {
    const flatMenus = flattenMenuTree(menuStore.menuItems)
    const totalMenus = flatMenus.length
    const activeMenus = flatMenus.filter(menu => menu.use_at === 'Y').length
    const menusByLevel = {
      level1: menuStore.menuItems.length,
      level2: getMenusByLevel(2).length,
      level3: getMenusByLevel(3).length
    }
    
    return {
      total: totalMenus,
      active: activeMenus,
      inactive: totalMenus - activeMenus,
      byLevel: menusByLevel
    }
  })
  
  return {
    // 스토어 상태
    menuItems: computed(() => menuStore.menuItems),
    isLoading: computed(() => menuStore.isLoading),
    error: computed(() => menuStore.error),
    hasMenuItems: computed(() => menuStore.hasMenuItems),
    
    // 액션
    refreshMenu,
    findMenuById: menuStore.findMenuById,
    getMenuPath: menuStore.getMenuPath,
    findActiveMenu: menuStore.findActiveMenu,
    
    // 유틸리티
    flattenMenuTree,
    searchMenus,
    filterMenusByPermission,
    getMenusByLevel,
    
    // 통계
    menuStats
  }
}

/**
 * 메뉴 네비게이션 컴포저블
 * 현재 활성 메뉴, breadcrumb 등의 네비게이션 관련 기능을 제공합니다.
 */
export function useMenuNavigation() {
  const menuStore = useMenuStore()
  
  // 현재 경로에 해당하는 활성 메뉴 찾기
  const getCurrentMenu = (currentPath: string): MenuTreeNode | null => {
    return menuStore.findActiveMenu(currentPath)
  }
  
  // Breadcrumb 생성
  const getBreadcrumb = (currentPath: string): MenuTreeNode[] => {
    const activeMenu = getCurrentMenu(currentPath)
    if (!activeMenu) return []
    
    return menuStore.getMenuPath(activeMenu.id) || []
  }
  
  // 사이드바 메뉴 생성 (현재 메뉴의 형제/자식 메뉴)
  const getSidebarMenus = (currentPath: string): MenuTreeNode[] => {
    const activeMenu = getCurrentMenu(currentPath)
    if (!activeMenu) return menuStore.menuItems
    
    const menuPath = menuStore.getMenuPath(activeMenu.id)
    if (!menuPath || menuPath.length === 0) return menuStore.menuItems
    
    // 현재 메뉴가 최상위 메뉴인 경우
    if (menuPath.length === 1) {
      return activeMenu.children || []
    }
    
    // 부모 메뉴의 자식 메뉴들 반환
    const parentMenu = menuPath[menuPath.length - 2]
    return parentMenu.children || []
  }
  
  return {
    getCurrentMenu,
    getBreadcrumb,
    getSidebarMenus
  }
}
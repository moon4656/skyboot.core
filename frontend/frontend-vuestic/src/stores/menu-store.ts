import { defineStore } from 'pinia'
import { MenuApiService } from '../services/menu-api'
import { useAuthStore } from './auth-store'

// 메뉴 아이템 인터페이스
export interface MenuItem {
  id: number
  name: string
  displayName: string
  path?: string
  icon?: string
  parentId?: number | null
  order: number
  isActive: boolean
  requiredRole?: string
  children?: MenuItem[]
  meta?: {
    icon?: string
    badge?: string | number
    external?: boolean
    target?: string
  }
}

// API 응답 메뉴 아이템 인터페이스
export interface ApiMenuItem {
  id: number
  name: string
  display_name: string
  path?: string
  icon?: string
  parent_id?: number | null
  order: number
  is_active: boolean
  required_role?: string
  children?: ApiMenuItem[]
}

// 메뉴 스토어 상태 인터페이스
interface MenuState {
  menuItems: MenuItem[]
  flatMenuItems: MenuItem[]
  isLoading: boolean
  error: string | null
  lastFetchTime: number | null
}

export const useMenuStore = defineStore('menu', {
  state: (): MenuState => ({
    menuItems: [],
    flatMenuItems: [],
    isLoading: false,
    error: null,
    lastFetchTime: null,
  }),

  getters: {
    /**
     * 권한에 따라 필터링된 메뉴 아이템 반환
     */
    filteredMenuItems: (state): MenuItem[] => {
      const authStore = useAuthStore()
      return state.menuItems.filter(item => 
        hasPermissionForMenuItem(item, authStore.userRole)
      )
    },

    /**
     * 플랫 구조의 메뉴 아이템 반환 (검색 등에 사용)
     */
    allMenuItems: (state): MenuItem[] => state.flatMenuItems,

    /**
     * 특정 경로에 해당하는 메뉴 아이템 찾기
     */
    getMenuItemByPath: (state) => (path: string): MenuItem | undefined => {
      return state.flatMenuItems.find(item => item.path === path)
    },

    /**
     * 특정 ID의 메뉴 아이템 찾기
     */
    getMenuItemById: (state) => (id: number): MenuItem | undefined => {
      return state.flatMenuItems.find(item => item.id === id)
    },

    /**
     * 로딩 상태 확인
     */
    loading: (state): boolean => state.isLoading,

    /**
     * 에러 상태 확인
     */
    hasError: (state): boolean => !!state.error,
  },

  actions: {
    /**
     * 메뉴 데이터 조회
     */
    async fetchMenuItems(force = false): Promise<void> {
      // 캐시된 데이터가 있고 강제 새로고침이 아닌 경우 스킵
      const cacheTimeout = 5 * 60 * 1000 // 5분
      if (!force && this.lastFetchTime && 
          Date.now() - this.lastFetchTime < cacheTimeout) {
        return
      }

      this.isLoading = true
      this.error = null

      try {
        // MenuApiService를 사용하여 메뉴 데이터 가져오기
        const response: ApiMenuItem[] = await MenuApiService.getMenuItems()

        // API 응답을 내부 형식으로 변환
        const convertedMenuItems = response.map(item => 
          convertApiMenuItemToMenuItem(item)
        )

        // 메뉴 아이템 정렬 및 트리 구조 생성
        this.menuItems = buildMenuTree(convertedMenuItems)
        this.flatMenuItems = flattenMenuItems(this.menuItems)
        this.lastFetchTime = Date.now()
      } catch (error: any) {
        console.error('메뉴 데이터 조회 실패:', error)
        this.error = error.message || '메뉴 데이터를 불러오는데 실패했습니다.'
        
        // 에러 발생 시 기본 메뉴 사용
        this.menuItems = getDefaultMenuItems()
        this.flatMenuItems = flattenMenuItems(this.menuItems)
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 권한별 메뉴 데이터 조회
     */
    async fetchMenuItemsByRole(roleId?: number): Promise<void> {
      this.isLoading = true
      this.error = null
      
      try {
        // MenuApiService를 사용하여 권한별 메뉴 데이터 가져오기
        const response: ApiMenuItem[] = await MenuApiService.getMenuItemsByRole(roleId)
        
        // API 응답을 내부 형식으로 변환
        const convertedMenuItems = response.map(item => 
          convertApiMenuItemToMenuItem(item)
        )
        
        // 메뉴 아이템 정렬 및 트리 구조 생성
        this.menuItems = buildMenuTree(convertedMenuItems)
        this.flatMenuItems = flattenMenuItems(this.menuItems)
      } catch (error: any) {
        console.error('권한별 메뉴 데이터 로드 실패:', error)
        this.error = error.message || '권한별 메뉴 데이터를 가져오는데 실패했습니다.'
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 메뉴 트리 조회
     */
    async fetchMenuTree(): Promise<void> {
      this.isLoading = true
      this.error = null
      
      try {
        // MenuApiService를 사용하여 메뉴 트리 가져오기
        const response: ApiMenuItem[] = await MenuApiService.getMenuTree()
        
        // API 응답을 내부 형식으로 변환
        const convertedMenuItems = response.map(item => 
          convertApiMenuItemToMenuItem(item)
        )
        
        this.menuItems = convertedMenuItems
        this.flatMenuItems = flattenMenuItems(this.menuItems)
      } catch (error: any) {
        console.error('메뉴 트리 로드 실패:', error)
        this.error = error.message || '메뉴 트리를 가져오는데 실패했습니다.'
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 메뉴 접근 권한 확인
     */
    async checkMenuAccess(menuId: number): Promise<boolean> {
      try {
        return await MenuApiService.checkMenuAccess(menuId)
      } catch (error: any) {
        console.error('메뉴 접근 권한 확인 실패:', error)
        return false
      }
    },

    /**
     * 메뉴 캐시 초기화
     */
    clearCache(): void {
      this.lastFetchTime = null
    },

    /**
     * 메뉴 데이터 새로고침
     */
    async refreshMenuItems(): Promise<void> {
      await this.fetchMenuItems(true)
    },

    /**
     * 특정 메뉴 아이템 활성화/비활성화
     */
    toggleMenuItem(id: number): void {
      const item = this.getMenuItemById(id)
      if (item) {
        item.isActive = !item.isActive
      }
    },

    /**
     * 메뉴 아이템 업데이트
     */
    updateMenuItem(id: number, updates: Partial<MenuItem>): void {
      const item = this.getMenuItemById(id)
      if (item) {
        Object.assign(item, updates)
      }
    },
  },
})

/**
 * API 메뉴 아이템을 내부 형식으로 변환
 */
function convertApiMenuItemToMenuItem(apiItem: ApiMenuItem): MenuItem {
  return {
    id: apiItem.id,
    name: apiItem.name,
    displayName: apiItem.display_name,
    path: apiItem.path,
    icon: apiItem.icon,
    parentId: apiItem.parent_id,
    order: apiItem.order,
    isActive: apiItem.is_active,
    requiredRole: apiItem.required_role,
    children: apiItem.children?.map(child => 
      convertApiMenuItemToMenuItem(child)
    ),
    meta: {
      icon: apiItem.icon,
    },
  }
}

/**
 * 플랫 메뉴 아이템 배열을 트리 구조로 변환
 */
function buildMenuTree(items: MenuItem[]): MenuItem[] {
  const itemMap = new Map<number, MenuItem>()
  const rootItems: MenuItem[] = []

  // 모든 아이템을 맵에 저장
  items.forEach(item => {
    itemMap.set(item.id, { ...item, children: [] })
  })

  // 트리 구조 생성
  items.forEach(item => {
    const menuItem = itemMap.get(item.id)!
    
    if (item.parentId === null || item.parentId === undefined) {
      rootItems.push(menuItem)
    } else {
      const parent = itemMap.get(item.parentId)
      if (parent) {
        parent.children = parent.children || []
        parent.children.push(menuItem)
      }
    }
  })

  // 정렬
  const sortItems = (items: MenuItem[]): MenuItem[] => {
    return items
      .sort((a, b) => a.order - b.order)
      .map(item => ({
        ...item,
        children: item.children ? sortItems(item.children) : undefined,
      }))
  }

  return sortItems(rootItems)
}

/**
 * 트리 구조의 메뉴를 플랫 배열로 변환
 */
function flattenMenuItems(items: MenuItem[]): MenuItem[] {
  const result: MenuItem[] = []
  
  const flatten = (items: MenuItem[]) => {
    items.forEach(item => {
      result.push(item)
      if (item.children && item.children.length > 0) {
        flatten(item.children)
      }
    })
  }
  
  flatten(items)
  return result
}

/**
 * 메뉴 아이템에 대한 권한 확인
 */
function hasPermissionForMenuItem(item: MenuItem, userRole: string | null): boolean {
  // 활성화되지 않은 메뉴는 표시하지 않음
  if (!item.isActive) {
    return false
  }

  // 권한이 필요하지 않은 메뉴는 모두 표시
  if (!item.requiredRole) {
    return true
  }

  // 사용자 역할이 없으면 표시하지 않음
  if (!userRole) {
    return false
  }

  // 관리자는 모든 메뉴 접근 가능
  if (userRole === 'admin') {
    return true
  }

  // 필요한 역할과 사용자 역할이 일치하는지 확인
  return userRole === item.requiredRole
}

/**
 * 기본 메뉴 아이템 (API 실패 시 사용)
 */
function getDefaultMenuItems(): MenuItem[] {
  return [
    {
      id: 1,
      name: 'dashboard',
      displayName: '대시보드',
      path: '/dashboard',
      icon: 'dashboard',
      parentId: null,
      order: 1,
      isActive: true,
      meta: { icon: 'dashboard' },
    },
    {
      id: 2,
      name: 'users',
      displayName: '사용자 관리',
      path: '/users',
      icon: 'group',
      parentId: null,
      order: 2,
      isActive: true,
      requiredRole: 'admin',
      meta: { icon: 'group' },
    },
    {
      id: 3,
      name: 'projects',
      displayName: '프로젝트',
      path: '/projects',
      icon: 'folder_shared',
      parentId: null,
      order: 3,
      isActive: true,
      meta: { icon: 'folder_shared' },
    },
    {
      id: 4,
      name: 'payments',
      displayName: '결제 관리',
      path: '/payments',
      icon: 'payment',
      parentId: null,
      order: 4,
      isActive: true,
      children: [
        {
          id: 41,
          name: 'payment-methods',
          displayName: '결제 수단',
          path: '/payments/payment-methods',
          icon: 'credit_card',
          parentId: 4,
          order: 1,
          isActive: true,
          meta: { icon: 'credit_card' },
        },
        {
          id: 42,
          name: 'billing',
          displayName: '청구서',
          path: '/payments/billing',
          icon: 'receipt',
          parentId: 4,
          order: 2,
          isActive: true,
          meta: { icon: 'receipt' },
        },
        {
          id: 43,
          name: 'pricing-plans',
          displayName: '요금제',
          path: '/payments/pricing-plans',
          icon: 'price_check',
          parentId: 4,
          order: 3,
          isActive: true,
          meta: { icon: 'price_check' },
        },
      ],
      meta: { icon: 'payment' },
    },
    {
      id: 5,
      name: 'faq',
      displayName: 'FAQ',
      path: '/faq',
      icon: 'help',
      parentId: null,
      order: 5,
      isActive: true,
      meta: { icon: 'help' },
    },
    {
      id: 6,
      name: 'settings',
      displayName: '설정',
      path: '/settings',
      icon: 'settings',
      parentId: null,
      order: 6,
      isActive: true,
      meta: { icon: 'settings' },
    },
    {
      id: 7,
      name: 'preferences',
      displayName: '환경설정',
      path: '/preferences',
      icon: 'tune',
      parentId: null,
      order: 7,
      isActive: true,
      meta: { icon: 'tune' },
    },
  ]
}
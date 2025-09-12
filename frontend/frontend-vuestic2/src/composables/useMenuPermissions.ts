import { computed, ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { menuApi, type MenuTreeNode } from '@/services/api'

/**
 * 메뉴 권한 관리를 위한 컴포저블
 * 사용자의 권한에 따라 메뉴 표시 여부를 제어합니다.
 */

// 메뉴 아이템 인터페이스
export interface MenuItem {
  id: string
  name: string
  path: string
  icon?: string
  children?: MenuItem[]
  permissions?: string[] // 필요한 권한 목록
  roles?: string[] // 필요한 역할 목록
  isVisible?: boolean
  isActive?: boolean
  order?: number
}

// 권한 타입 정의
export interface Permission {
  id: string
  name: string
  code: string
  description?: string
}

// 역할 타입 정의
export interface Role {
  id: string
  name: string
  code: string
  permissions: Permission[]
}

export function useMenuPermissions() {
  const authStore = useAuthStore()
  
  // 동적 메뉴 상태
  const dynamicMenuItems = ref<MenuItem[]>([])
  const isLoadingMenus = ref(false)
  const menuLoadError = ref<string | null>(null)
  
  // 기본 메뉴 구조 정의
  const defaultMenuItems = ref<MenuItem[]>([
    {
      id: 'dashboard',
      name: '대시보드',
      path: '/admin/dashboard',
      icon: 'dashboard',
      permissions: ['dashboard.view'],
      order: 1
    },
    {
      id: 'user-management',
      name: '사용자 관리',
      path: '/admin/users',
      icon: 'people',
      permissions: ['user.view', 'user.manage'],
      roles: ['admin', 'user_manager'],
      order: 2
    },
    {
      id: 'menu-management',
      name: '메뉴 관리',
      path: '/admin/menus',
      icon: 'menu',
      permissions: ['menu.view', 'menu.manage'],
      roles: ['admin', 'system_manager'],
      order: 3
    },
    {
      id: 'program-management',
      name: '프로그램 관리',
      path: '/admin/programs',
      icon: 'apps',
      permissions: ['program.view', 'program.manage'],
      roles: ['admin', 'system_manager'],
      order: 4
    },
    {
      id: 'menu-permissions',
      name: '메뉴 권한',
      path: '/admin/menu-permissions',
      icon: 'security',
      permissions: ['menu_permission.view', 'menu_permission.manage'],
      roles: ['admin'],
      order: 5
    },
    {
      id: 'user-permissions',
      name: '사용자 권한',
      path: '/admin/user-permissions',
      icon: 'admin_panel_settings',
      permissions: ['user_permission.view', 'user_permission.manage'],
      roles: ['admin'],
      order: 6
    },
    {
      id: 'common-codes',
      name: '공통코드',
      path: '/admin/common-codes',
      icon: 'code',
      permissions: ['common_code.view', 'common_code.manage'],
      roles: ['admin', 'system_manager'],
      order: 7
    },
    {
      id: 'board-management',
      name: '게시판 관리',
      path: '/admin/boards',
      icon: 'forum',
      permissions: ['board.view', 'board.manage'],
      roles: ['admin', 'content_manager'],
      order: 8
    }
  ])
  
  // URL을 /admin 하위 경로로 정규화
  const normalizeAdminPath = (url?: string, id?: number): string => {
    if (!url || url.trim() === '') return `/admin/menu/${id ?? ''}`
    // 앞의 슬래시 제거하여 정규화 준비
    const cleaned = url.replace(/^\/+/, '')
    // 이미 /admin 또는 admin/ 로 시작하는 경우, 중복 접두어 방지
    if (cleaned === 'admin') return '/admin'
    if (cleaned.startsWith('admin/')) return `/${cleaned}` // ex) 'admin/unauthorized' -> '/admin/unauthorized'
    if (url.startsWith('/admin')) return url // ex) '/admin/unauthorized' 유지
    // 절대경로(다른 루트)면 그대로 사용
    if (url.startsWith('/')) return url
    // 상대경로면 /admin 접두어 부여
    return `/admin/${cleaned}`
  }
  
  // API 메뉴를 내부 MenuItem 형식으로 변환 (MenuTreeNode 기준)
  const convertApiMenuToMenuItem = (apiMenu: MenuTreeNode): MenuItem => {
    return {
      id: `menu_${apiMenu.id}`,
      name: apiMenu.name,
      path: normalizeAdminPath(apiMenu.url, apiMenu.id),
      icon: apiMenu.icon || 'folder',
      order: apiMenu.sort_order,
      children: apiMenu.children?.map(convertApiMenuToMenuItem),
      permissions: apiMenu.permission_code ? [apiMenu.permission_code] : [],
      roles: [],
      isVisible: apiMenu.use_at === 'Y'
    }
  }
  
  // 동적 메뉴 로드
  const loadDynamicMenus = async () => {
    isLoadingMenus.value = true
    menuLoadError.value = null
    
    try {
      console.log('🔄 동적 메뉴 로딩 시작...')
      const apiMenus = await menuApi.getMenuTree('Y')
      
      // API 메뉴를 내부 형식으로 변환
      dynamicMenuItems.value = apiMenus.map(convertApiMenuToMenuItem)
      
      console.log('✅ 동적 메뉴 로딩 완료:', dynamicMenuItems.value.length, '개 메뉴')
    } catch (error) {
      console.error('❌ 동적 메뉴 로딩 실패:', error)
      menuLoadError.value = '메뉴를 불러오는데 실패했습니다.'
      // 실패 시 기본 메뉴 사용
      dynamicMenuItems.value = []
    } finally {
      isLoadingMenus.value = false
    }
  }

  /**
   * 사용자가 특정 권한을 가지고 있는지 확인
   */
  const hasPermission = (permission: string): boolean => {
    const user = authStore.user
    if (!user || !user.permissions) return false
    
    return user.permissions.some(p => p.code === permission)
  }

  /**
   * 사용자가 특정 역할을 가지고 있는지 확인
   */
  const hasRole = (role: string): boolean => {
    const user = authStore.user
    if (!user || !user.roles) return false
    
    return user.roles.some(r => r.code === role)
  }

  /**
   * 사용자가 여러 권한 중 하나라도 가지고 있는지 확인
   */
  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }

  /**
   * 사용자가 여러 역할 중 하나라도 가지고 있는지 확인
   */
  const hasAnyRole = (roles: string[]): boolean => {
    return roles.some(role => hasRole(role))
  }

  /**
   * 메뉴 아이템이 표시 가능한지 확인
   */
  const canShowMenuItem = (menuItem: MenuItem): boolean => {
    // 슈퍼 관리자는 모든 메뉴 접근 가능
    if (hasRole('super_admin')) return true
    
    // 권한 체크
    if (menuItem.permissions && menuItem.permissions.length > 0) {
      if (!hasAnyPermission(menuItem.permissions)) return false
    }
    
    // 역할 체크
    if (menuItem.roles && menuItem.roles.length > 0) {
      if (!hasAnyRole(menuItem.roles)) return false
    }
    
    return true
  }

  /**
   * 권한에 따라 필터링된 메뉴 목록 반환 (동적 메뉴 + 기본 메뉴)
   */
  const filteredMenuItems = computed<MenuItem[]>(() => {
    // 동적 메뉴와 기본 메뉴 병합
    const allMenuItems = [...dynamicMenuItems.value, ...defaultMenuItems.value]
    
    return allMenuItems
      .filter(menuItem => canShowMenuItem(menuItem) && menuItem.isVisible !== false)
      .map(menuItem => ({
        ...menuItem,
        isVisible: true,
        children: menuItem.children?.filter(child => canShowMenuItem(child))
      }))
      .sort((a, b) => (a.order || 0) - (b.order || 0))
  })

  /**
   * 특정 경로에 대한 접근 권한 확인
   */
  const canAccessPath = (path: string): boolean => {
    const menuItem = [...dynamicMenuItems.value, ...defaultMenuItems.value].find(item => 
      item.path === path || 
      item.children?.some(child => child.path === path)
    )
    
    if (!menuItem) return false
    
    return canShowMenuItem(menuItem)
  }

  /**
   * 현재 활성 메뉴 아이템 설정
   */
  const setActiveMenuItem = (path: string) => {
    defaultMenuItems.value.forEach(item => {
      item.isActive = item.path === path
      if (item.children) {
        item.children.forEach(child => {
          child.isActive = child.path === path
        })
      }
    })
  }

  /**
   * 메뉴 아이템 동적 추가
   */
  const addMenuItem = (menuItem: MenuItem) => {
    defaultMenuItems.value.push(menuItem)
    // 순서에 따라 정렬
    defaultMenuItems.value.sort((a, b) => (a.order || 0) - (b.order || 0))
  }

  /**
   * 메뉴 아이템 제거
   */
  const removeMenuItem = (menuId: string) => {
    const index = defaultMenuItems.value.findIndex(item => item.id === menuId)
    if (index > -1) {
      defaultMenuItems.value.splice(index, 1)
    }
  }

  /**
   * 메뉴 아이템 업데이트
   */
  const updateMenuItem = (menuId: string, updates: Partial<MenuItem>) => {
    const menuItem = defaultMenuItems.value.find(item => item.id === menuId)
    if (menuItem) {
      Object.assign(menuItem, updates)
    }
  }

  /**
   * 사용자 권한 정보 반환
   */
  const userPermissions = computed(() => {
    const user = authStore.user
    return {
      permissions: user?.permissions || [],
      roles: user?.roles || [],
      isAdmin: hasRole('admin') || hasRole('super_admin'),
      isSuperAdmin: hasRole('super_admin')
    }
  })

  // 컴포넌트 마운트 시 동적 메뉴 로드
  onMounted(() => {
    loadDynamicMenus()
  })

  return {
    // 상태
    defaultMenuItems,
    dynamicMenuItems,
    filteredMenuItems,
    userPermissions,
    isLoadingMenus,
    menuLoadError,
    
    // 메서드
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAnyRole,
    canShowMenuItem,
    canAccessPath,
    setActiveMenuItem,
    addMenuItem,
    removeMenuItem,
    updateMenuItem,
    loadDynamicMenus,
    convertApiMenuToMenuItem
  }
}

/**
 * 라우터 가드에서 사용할 권한 체크 함수
 */
export function createPermissionGuard() {
  const { canAccessPath } = useMenuPermissions()
  
  return (to: any, from: any, next: any) => {
    if (canAccessPath(to.path)) {
      next()
    } else {
      // 권한이 없는 경우 대시보드로 리다이렉트
      next('/admin/dashboard')
    }
  }
}
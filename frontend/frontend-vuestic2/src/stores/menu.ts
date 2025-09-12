import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { menuApi, type MenuTreeNode } from '@/services/api'

export const useMenuStore = defineStore('menu', () => {
  // 상태 관리
  const menuItems = ref<MenuTreeNode[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const lastFetchTime = ref<number | null>(null)
  
  // 캐시 유효 시간 (5분)
  const CACHE_DURATION = 5 * 60 * 1000
  
  // 계산된 속성
  const hasMenuItems = computed(() => menuItems.value.length > 0)
  const isCacheValid = computed(() => {
    if (!lastFetchTime.value) return false
    return Date.now() - lastFetchTime.value < CACHE_DURATION
  })
  
  // 메뉴 트리 가져오기
  const fetchMenuTree = async (useAt: string = 'Y', forceRefresh: boolean = false) => {
    // 캐시가 유효하고 강제 새로고침이 아닌 경우 기존 데이터 반환
    if (!forceRefresh && hasMenuItems.value && isCacheValid.value) {
      return menuItems.value
    }
    
    isLoading.value = true
    error.value = null
    
    try {
      console.log('🔄 메뉴 트리 로딩 시작...')
      const response = await menuApi.getMenuTree(useAt)
      
      if (response && Array.isArray(response)) {
        menuItems.value = response
        lastFetchTime.value = Date.now()
        console.log('✅ 메뉴 트리 로딩 완료:', response.length, '개 메뉴')
      } else {
        console.warn('⚠️ 메뉴 응답이 배열이 아닙니다:', response)
        menuItems.value = []
      }
      
      return menuItems.value
    } catch (err: any) {
      console.error('❌ 메뉴 트리 로딩 실패:', err)
      error.value = err.message || '메뉴를 불러오는데 실패했습니다.'
      menuItems.value = []
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  // 메뉴 초기화
  const initializeMenu = async () => {
    try {
      await fetchMenuTree()
    } catch (err) {
      console.error('메뉴 초기화 실패:', err)
    }
  }
  
  // 메뉴 캐시 클리어
  const clearCache = () => {
    menuItems.value = []
    lastFetchTime.value = null
    error.value = null
  }
  
  // 특정 메뉴 찾기 (재귀적으로 검색)
  const findMenuById = (id: number, items: MenuTreeNode[] = menuItems.value): MenuTreeNode | null => {
    for (const item of items) {
      if (item.id === id) {
        return item
      }
      if (item.children && item.children.length > 0) {
        const found = findMenuById(id, item.children)
        if (found) return found
      }
    }
    return null
  }
  
  // 메뉴 경로 찾기 (breadcrumb용)
  const getMenuPath = (id: number, items: MenuTreeNode[] = menuItems.value, path: MenuTreeNode[] = []): MenuTreeNode[] | null => {
    for (const item of items) {
      const currentPath = [...path, item]
      
      if (item.id === id) {
        return currentPath
      }
      
      if (item.children && item.children.length > 0) {
        const found = getMenuPath(id, item.children, currentPath)
        if (found) return found
      }
    }
    return null
  }
  
  // 활성 메뉴 찾기 (URL 기반)
  const findActiveMenu = (url: string, items: MenuTreeNode[] = menuItems.value): MenuTreeNode | null => {
    for (const item of items) {
      if (item.url === url) {
        return item
      }
      if (item.children && item.children.length > 0) {
        const found = findActiveMenu(url, item.children)
        if (found) return found
      }
    }
    return null
  }
  
  return {
    // 상태
    menuItems,
    isLoading,
    error,
    lastFetchTime,
    
    // 계산된 속성
    hasMenuItems,
    isCacheValid,
    
    // 액션
    fetchMenuTree,
    initializeMenu,
    clearCache,
    findMenuById,
    getMenuPath,
    findActiveMenu
  }
})
<template>
  <div class="admin-layout">
    <!-- 사이드바 -->
    <va-sidebar
      v-model="sidebarVisible"
      :width="sidebarWidth"
      color="primary"
      class="admin-sidebar"
    >
      <div class="sidebar-header">
        <h2 class="text-white font-bold text-xl p-4">
          <va-icon name="admin_panel_settings" class="mr-2" />
          SkyBoot Admin
        </h2>
      </div>
      
      <va-sidebar-item-content>
        <va-list class="sidebar-menu">
          <!-- 대시보드 -->
          <va-list-item
            :to="{ name: 'Dashboard' }"
            class="menu-item"
          >
            <va-list-item-section avatar>
              <va-icon name="dashboard" />
            </va-list-item-section>
            <va-list-item-section>
              <va-list-item-label>대시보드</va-list-item-label>
            </va-list-item-section>
          </va-list-item>

          <!-- 관리자 메뉴 -->
          <va-list-item
            class="menu-group-header"
            disabled
          >
            <va-list-item-section>
              <va-list-item-label class="text-gray-400 text-sm font-semibold">
                관리자 메뉴
              </va-list-item-label>
            </va-list-item-section>
          </va-list-item>

          <va-list-item
            v-for="menuItem in adminMenuItems"
            :key="menuItem.name"
            :to="menuItem.to"
            class="menu-item"
            @click="handleMenuClick(menuItem)"
          >
            <va-list-item-section avatar>
              <va-icon :name="menuItem.icon" />
            </va-list-item-section>
            <va-list-item-section>
              <va-list-item-label>{{ menuItem.label }}</va-list-item-label>
            </va-list-item-section>
          </va-list-item>

          <va-list-item
            :to="{ name: 'Menus' }"
            class="menu-item"
          >
            <va-list-item-section avatar>
              <va-icon name="menu" />
            </va-list-item-section>
            <va-list-item-section>
              <va-list-item-label>메뉴 관리</va-list-item-label>
            </va-list-item-section>
          </va-list-item>
        </va-list>
      </va-sidebar-item-content>
    </va-sidebar>

    <!-- 메인 컨텐츠 영역 -->
    <div class="main-content" :class="{ 'sidebar-open': sidebarVisible }">
      <!-- 상단 네비게이션 -->
      <va-navbar class="top-navbar">
        <template #left>
          <va-button
            preset="plain"
            icon="menu"
            @click="toggleSidebar"
            class="sidebar-toggle"
          />
        </template>
        
        <template #center>
          <div class="breadcrumb">
            <va-breadcrumbs
              :items="breadcrumbItems"
              color="primary"
            />
          </div>
        </template>

        <template #right>
          <div class="user-menu">
            <va-dropdown>
              <template #anchor>
                <va-button preset="plain" class="user-button">
                  <va-avatar
                    size="small"
                    :src="userAvatar"
                    :fallback-text="userInitials"
                    class="mr-2"
                  />
                  <span class="user-name">{{ authStore.user?.username }}</span>
                  <va-icon name="expand_more" class="ml-1" />
                </va-button>
              </template>
              
              <va-dropdown-content>
                <va-list>
                  <va-list-item @click="handleProfile">
                    <va-list-item-section avatar>
                      <va-icon name="person" />
                    </va-list-item-section>
                    <va-list-item-section>
                      <va-list-item-label>프로필</va-list-item-label>
                    </va-list-item-section>
                  </va-list-item>
                  
                  <va-list-item @click="handleSettings">
                    <va-list-item-section avatar>
                      <va-icon name="settings" />
                    </va-list-item-section>
                    <va-list-item-section>
                      <va-list-item-label>설정</va-list-item-label>
                    </va-list-item-section>
                  </va-list-item>
                  
                  <va-divider />
                  
                  <va-list-item @click="handleLogout">
                    <va-list-item-section avatar>
                      <va-icon name="logout" />
                    </va-list-item-section>
                    <va-list-item-section>
                      <va-list-item-label>로그아웃</va-list-item-label>
                    </va-list-item-section>
                  </va-list-item>
                </va-list>
              </va-dropdown-content>
            </va-dropdown>
          </div>
        </template>
      </va-navbar>

      <!-- 페이지 컨텐츠 -->
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMenuPermissions } from '@/composables/useMenuPermissions'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { filteredMenuItems, setActiveMenuItem } = useMenuPermissions()

// 사이드바 상태
const sidebarVisible = ref(true)
const sidebarWidth = '280px'

// 관리자 메뉴 아이템 (권한에 따라 필터링됨)
const adminMenuItems = computed(() => {
  return filteredMenuItems.value.filter(item => 
    item.path.startsWith('/admin') && item.path !== '/admin'
  ).map(item => ({
    name: item.path.split('/').pop(),
    label: item.name,
    icon: item.icon || 'folder',
    to: { path: item.path }
  }))
})

// 브레드크럼 아이템
const breadcrumbItems = computed(() => {
  const items = [{ label: '홈', to: '/admin' }]
  
  if (route.name === 'Dashboard') {
    items.push({ label: '대시보드' })
  } else if (route.path.startsWith('/admin')) {
    items.push({ label: '관리자' })
    
    const currentMenuItem = filteredMenuItems.value.find(item => item.path === route.path)
    if (currentMenuItem) {
      items.push({ label: currentMenuItem.name })
    }
  }
  
  return items
})

// 현재 페이지 제목 계산
const currentPageTitle = computed(() => {
  const currentMenuItem = filteredMenuItems.value.find(item => 
    item.path === route.path || 
    item.children?.some(child => child.path === route.path)
  )
  return currentMenuItem?.name || '관리자 페이지'
})

// 사용자 정보
const userAvatar = computed(() => {
  // 기본 아바타 이미지 또는 사용자 프로필 이미지
  return null
})

const userInitials = computed(() => {
  const username = authStore.user?.username || 'U'
  return username.charAt(0).toUpperCase()
})

// 메서드
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const handleProfile = () => {
  // 프로필 페이지로 이동 (미구현)
  router.push({ name: 'ComingSoon' })
}

const handleSettings = () => {
  // 설정 페이지로 이동 (미구현)
  router.push({ name: 'ComingSoon' })
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/auth/login')
  } catch (error) {
    console.error('로그아웃 실패:', error)
  }
}

// 메뉴 클릭 핸들러
const handleMenuClick = (menuItem: any) => {
  setActiveMenuItem(menuItem.to.path)
  router.push(menuItem.to)
  
  // 모바일에서는 메뉴 클릭 시 사이드바 닫기
  if (window.innerWidth <= 768) {
    sidebarVisible.value = false
  }
}

// 토큰 유효성 검사 및 로그인 페이지 리다이렉트 함수
const checkAuthenticationStatus = async () => {
  // 1. Access Token 존재 여부 확인
  if (!authStore.accessToken) {
    console.warn('⚠️ Access Token이 없습니다. 로그인 페이지로 이동합니다.')
    await router.push('/auth/login')
    return false
  }

  // 2. 토큰 유효성 검사
  if (!authStore.isAuthenticated) {
    console.warn('⚠️ Access Token이 만료되었습니다. 토큰 갱신을 시도합니다.')
    
    // 3. 토큰 갱신 시도
    const refreshed = await authStore.refreshAccessToken()
    if (!refreshed) {
      console.warn('⚠️ 토큰 갱신에 실패했습니다. 로그인 페이지로 이동합니다.')
      await router.push('/auth/login')
      return false
    }
  }

  // 4. 사용자 정보 로드
  if (!authStore.user) {
    await authStore.refreshUserInfo()
  }

  return true
}

// Storage 이벤트 리스너 (다른 탭에서 로그아웃 감지)
const handleStorageChange = (event: StorageEvent) => {
  if (event.key === 'skyboot_access_token' && !event.newValue) {
    console.warn('⚠️ 다른 탭에서 로그아웃이 감지되었습니다.')
    router.push('/auth/login')
  }
}

// 주기적 토큰 검증 (5분마다)
let tokenCheckInterval: NodeJS.Timeout | null = null

const startTokenValidation = () => {
  tokenCheckInterval = setInterval(async () => {
    if (!authStore.isAuthenticated) {
      console.warn('⚠️ 주기적 검증에서 토큰 만료가 감지되었습니다.')
      clearInterval(tokenCheckInterval!)
      await router.push('/auth/login')
    }
  }, 5 * 60 * 1000) // 5분마다 검증
}

const stopTokenValidation = () => {
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval)
    tokenCheckInterval = null
  }
}

// 라이프사이클
onMounted(async () => {
  // 인증 상태 확인 및 토큰 검증
  const isAuthenticated = await checkAuthenticationStatus()
  
  if (isAuthenticated) {
    // 현재 경로에 따라 활성 메뉴 설정
    setActiveMenuItem(route.path)
    
    // 화면 크기에 따라 사이드바 초기 상태 설정
    if (window.innerWidth < 768) {
      sidebarVisible.value = false
    }
    
    // Storage 이벤트 리스너 등록 (다른 탭에서 로그아웃 감지)
    window.addEventListener('storage', handleStorageChange)
    
    // 주기적 토큰 검증 시작
    startTokenValidation()
  }
})

// 컴포넌트 언마운트 시 정리
onUnmounted(() => {
  // Storage 이벤트 리스너 제거
  window.removeEventListener('storage', handleStorageChange)
  
  // 토큰 검증 인터벌 정리
  stopTokenValidation()
})
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: var(--skyboot-bg-primary);
}

.admin-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  z-index: 1000;
  background: linear-gradient(135deg, var(--skyboot-primary) 0%, var(--skyboot-secondary) 100%);
  box-shadow: var(--skyboot-shadow-lg);
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  padding: 1rem 0;
}

.menu-item {
  margin: 0.25rem 1rem;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transition: left 0.5s ease;
}

.menu-item:hover::before {
  left: 100%;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
  box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.1);
}

.menu-item.router-link-active {
  background-color: rgba(245, 245, 220, 0.2);
  border-left: 4px solid var(--skyboot-beige-200);
  box-shadow: inset 0 0 30px rgba(255, 255, 255, 0.1);
}

.menu-item.router-link-active::after {
  content: '';
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 60%;
  background: var(--skyboot-beige-200);
  border-radius: 2px 0 0 2px;
  box-shadow: 0 0 10px var(--skyboot-beige-200);
}

.menu-group-header {
  margin: 1.5rem 1rem 0.5rem;
  padding: 0.5rem 0;
}

.main-content {
  flex: 1;
  margin-left: 0;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
}

.main-content.sidebar-open {
  margin-left: 280px;
}

.top-navbar {
  background: var(--skyboot-bg-element);
  border-bottom: 1px solid var(--skyboot-bg-border);
  box-shadow: var(--skyboot-shadow-sm);
  z-index: 999;
  backdrop-filter: blur(10px);
}

.sidebar-toggle {
  color: var(--skyboot-text-primary);
}

.breadcrumb {
  flex: 1;
  display: flex;
  justify-content: center;
}

.user-menu {
  display: flex;
  align-items: center;
}

.user-button {
  display: flex;
  align-items: center;
  color: var(--skyboot-text-primary);
  font-weight: 500;
  transition: all 0.2s ease;
  border-radius: 0.5rem;
  padding: 0.5rem;
  border: 1px solid transparent;
}

.user-button:hover {
  background: var(--skyboot-bg-secondary);
  border-color: var(--skyboot-bg-border);
  transform: translateY(-1px);
  box-shadow: var(--skyboot-shadow-sm);
}

.user-name {
  font-size: 0.9rem;
}

.page-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background-color: var(--skyboot-bg-primary);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .main-content.sidebar-open {
    margin-left: 0;
  }
  
  .admin-sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .admin-sidebar.va-sidebar--visible {
    transform: translateX(0);
  }
  
  .page-content {
    padding: 1rem;
  }
}

/* 부드러운 애니메이션 */
.menu-item,
.user-button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.menu-item:hover {
  box-shadow: var(--skyboot-shadow-md);
}

/* 사이드바 그라데이션 오버레이 */
.admin-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, 
    rgba(255, 255, 255, 0.05) 0%, 
    transparent 50%, 
    rgba(255, 255, 255, 0.02) 100%);
  pointer-events: none;
}

/* 네비게이션 바 글래스 효과 */
.top-navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(232, 230, 224, 0.8);
}

/* 호버 시 아이콘 애니메이션 */
.menu-item:hover .va-icon {
  animation: iconPulse 0.6s ease-in-out;
}

@keyframes iconPulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}
</style>
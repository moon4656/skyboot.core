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
        <div class="flex items-center justify-between p-4">
          <h2 class="font-bold text-xl" style="color: #ffffff;">
            <va-icon name="admin_panel_settings" class="mr-2" />
            SkyBoot Admin
          </h2>
          <va-button
            preset="plain"
            icon="refresh"
            size="small"
            color="#ffffff"
            :loading="isLoadingMenus"
            @click="loadDynamicMenus"
            title="메뉴 새로고침"
          />
        </div>
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

          <!-- 메뉴 상태 및 목록 -->
          <template v-if="isLoadingMenus">
            <va-list-item class="menu-item" disabled>
              <va-list-item-section avatar>
                <va-progress-circle indeterminate size="small" />
              </va-list-item-section>
              <va-list-item-section>
                <va-list-item-label>메뉴 로딩 중...</va-list-item-label>
              </va-list-item-section>
            </va-list-item>
          </template>

          <template v-else-if="menuLoadError">
            <va-list-item class="menu-item" disabled>
              <va-list-item-section avatar>
                <va-icon name="error" color="danger" />
              </va-list-item-section>
              <va-list-item-section>
                <va-list-item-label class="text-danger">{{ menuLoadError }}</va-list-item-label>
              </va-list-item-section>
            </va-list-item>
          </template>

          <template v-else>
            <!-- 빈 상태 -->
            <va-list-item v-if="adminMenuItems.length === 0" class="menu-item" disabled>
              <va-list-item-section avatar>
                <va-icon name="info" />
              </va-list-item-section>
              <va-list-item-section>
                <va-list-item-label>표시할 메뉴가 없습니다</va-list-item-label>
              </va-list-item-section>
            </va-list-item>

            <!-- 동적 메뉴 아이템들 -->
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
          </template>

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
const { 
  filteredMenuItems, 
  setActiveMenuItem, 
  isLoadingMenus, 
  menuLoadError, 
  loadDynamicMenus 
} = useMenuPermissions()

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

// 사이드바 토글 함수 (템플릿에서 사용)
const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

// 메뉴 클릭 핸들러: 활성 메뉴 설정 및 모바일에서 사이드바 닫기
const handleMenuClick = (menuItem: any) => {
  const targetPath = menuItem?.to?.path || menuItem?.path
  if (targetPath) {
    setActiveMenuItem(targetPath)
  }
  // 작은 화면에서는 자동으로 사이드바를 닫아 UX 개선
  if (window.innerWidth < 1024) {
    sidebarVisible.value = false
  }
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.admin-sidebar {
  flex-shrink: 0;
  z-index: 1000;
}

.sidebar-header {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-menu {
  padding: 1rem 0;
}

.menu-item {
  margin: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-item.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
  font-weight: 600;
}

.menu-group-header {
  margin: 1rem 0.5rem 0.5rem;
  padding: 0.5rem 1rem;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-open {
  margin-left: 0;
}

.top-navbar {
  flex-shrink: 0;
  background: #ffffff;
  border-bottom: 1px solid #e9ecef;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 999;
}

.sidebar-toggle {
  color: #495057;
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
  color: #495057;
  font-weight: 500;
}

.user-name {
  margin: 0 0.5rem;
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 0;
  background: #f8f9fa;
}

/* 반응형 디자인 */
@media (max-width: 1023px) {
  .main-content {
    margin-left: 0;
  }
  
  .admin-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .admin-sidebar.va-sidebar--visible {
    transform: translateX(0);
  }
}

@media (max-width: 767px) {
  .breadcrumb {
    display: none;
  }
  
  .user-name {
    display: none;
  }
}
</style>
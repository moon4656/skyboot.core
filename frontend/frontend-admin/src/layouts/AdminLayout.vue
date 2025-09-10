<template>
  <div class="admin-layout">
    <VaLayout>
      <!-- 사이드바 -->
      <template #left>
        <VaSidebar
          v-model="sidebarVisible"
          :minimized="sidebarMinimized"
          :width="sidebarWidth"
          :minimized-width="sidebarMinimizedWidth"
          color="primary"
        >
          <!-- 사이드바 헤더 -->
          <div class="sidebar-header">
            <div class="logo-container">
              <VaIcon name="admin_panel_settings" size="2rem" color="#ffffff" />
              <span v-if="!sidebarMinimized" class="logo-text">Admin Panel</span>
            </div>
          </div>

          <!-- 메뉴 네비게이션 -->
          <VaSidebarItem
            v-for="item in menuItems"
            :key="item.id"
            :to="item.path"
            :active="isMenuActive(item.path)"
          >
            <VaSidebarItemContent>
              <VaIcon :name="item.icon" />
              <VaSidebarItemTitle>{{ item.name }}</VaSidebarItemTitle>
            </VaSidebarItemContent>
          </VaSidebarItem>
        </VaSidebar>
      </template>

      <!-- 메인 콘텐츠 -->
      <template #content>
        <div class="main-content">
          <!-- 상단 네비게이션 바 -->
          <VaNavbar class="navbar">
            <template #left>
              <VaButton
                preset="secondary"
                icon="menu"
                @click="toggleSidebar"
              />
              
              <!-- 브레드크럼 -->
              <VaBreadcrumbs class="ml-4">
                <VaBreadcrumbsItem
                  v-for="(crumb, index) in breadcrumbs"
                  :key="index"
                  :to="crumb.to"
                  :disabled="index === breadcrumbs.length - 1"
                >
                  {{ crumb.label }}
                </VaBreadcrumbsItem>
              </VaBreadcrumbs>
            </template>

            <template #right>
              <!-- 테마 토글 -->
              <VaButton
                preset="secondary"
                :icon="themeStore.isDark ? 'light_mode' : 'dark_mode'"
                @click="themeStore.toggleTheme"
              />

              <!-- 사용자 메뉴 -->
              <VaDropdown>
                <template #anchor>
                  <VaButton preset="secondary">
                    <VaAvatar size="small" color="primary">
                      {{ authStore.user?.username?.charAt(0).toUpperCase() }}
                    </VaAvatar>
                    <span class="ml-2">{{ authStore.user?.username }}</span>
                    <VaIcon name="expand_more" class="ml-1" />
                  </VaButton>
                </template>

                <VaDropdownContent>
                  <VaList>
                    <VaListItem @click="goToProfile">
                      <VaListItemSection avatar>
                        <VaIcon name="person" />
                      </VaListItemSection>
                      <VaListItemSection>
                        <VaListItemLabel>프로필</VaListItemLabel>
                      </VaListItemSection>
                    </VaListItem>

                    <VaListItem @click="goToSettings">
                      <VaListItemSection avatar>
                        <VaIcon name="settings" />
                      </VaListItemSection>
                      <VaListItemSection>
                        <VaListItemLabel>설정</VaListItemLabel>
                      </VaListItemSection>
                    </VaListItem>

                    <VaDivider />

                    <VaListItem @click="logout">
                      <VaListItemSection avatar>
                        <VaIcon name="logout" />
                      </VaListItemSection>
                      <VaListItemSection>
                        <VaListItemLabel>로그아웃</VaListItemLabel>
                      </VaListItemSection>
                    </VaListItem>
                  </VaList>
                </VaDropdownContent>
              </VaDropdown>
            </template>
          </VaNavbar>

          <!-- 페이지 콘텐츠 -->
          <div class="page-content">
            <router-view />
          </div>
        </div>
      </template>
    </VaLayout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useMenuStore } from '../stores/menu'
import { useThemeStore } from '../stores/theme'
import { useToast } from 'vuestic-ui'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const menuStore = useMenuStore()
const themeStore = useThemeStore()
const { init: notify } = useToast()

// 사이드바 상태
const sidebarVisible = ref(true)
const sidebarMinimized = ref(false)
const sidebarWidth = '280px'
const sidebarMinimizedWidth = '64px'

// 메뉴 아이템
const menuItems = computed(() => menuStore.activeMenus)

// 브레드크럼
const breadcrumbs = computed(() => {
  const pathSegments = route.path.split('/').filter(Boolean)
  const crumbs = [{ label: '홈', to: '/dashboard' }]
  
  let currentPath = ''
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`
    const menuItem = findMenuByPath(currentPath)
    if (menuItem) {
      crumbs.push({
        label: menuItem.name,
        to: currentPath
      })
    }
  })
  
  return crumbs
})

// 메뉴 활성 상태 확인
const isMenuActive = (path: string) => {
  return route.path.startsWith(path)
}

// 경로로 메뉴 찾기
const findMenuByPath = (path: string) => {
  return menuItems.value.find(item => item.path === path)
}

// 사이드바 토글
const toggleSidebar = () => {
  sidebarMinimized.value = !sidebarMinimized.value
}

// 프로필 페이지로 이동
const goToProfile = () => {
  router.push('/profile')
}

// 설정 페이지로 이동
const goToSettings = () => {
  router.push('/settings')
}

// 로그아웃
const logout = async () => {
  try {
    await authStore.logout()
    notify({
      message: '로그아웃되었습니다.',
      color: 'success',
      duration: 3000,
    })
    router.push('/login')
  } catch (error) {
    notify({
      message: '로그아웃 중 오류가 발생했습니다.',
      color: 'danger',
      duration: 3000,
    })
  }
}

// 컴포넌트 마운트 시 메뉴 로드
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await menuStore.fetchMenuTree()
  }
})
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  overflow: hidden;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.main-content {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  border-bottom: 1px solid var(--va-background-border);
  padding: 0 1.5rem;
  height: 64px;
  flex-shrink: 0;
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: 1.5rem;
  background-color: var(--va-background-secondary);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
  
  .navbar {
    padding: 0 1rem;
  }
}

/* 다크 모드 지원 */
.va-dark {
  .navbar {
    background-color: var(--va-background-primary);
    border-bottom-color: var(--va-background-border);
  }
  
  .page-content {
    background-color: var(--va-background-primary);
  }
}
</style>
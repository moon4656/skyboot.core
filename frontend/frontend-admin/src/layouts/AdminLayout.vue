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
          <template v-for="item in menuItems" :key="item.id">
            <VaSidebarItem
              v-if="hasChildren(item)"
              :active="isDescendantActive(item) || isMenuActive(item.path)"
              class="has-children"
            >
              <VaSidebarItemContent class="menu-parent" @click="toggleExpand(item.id)">
                <VaIcon :name="item.icon" />
                <VaSidebarItemTitle>{{ item.name }}</VaSidebarItemTitle>
                <span class="spacer"></span>
                <VaIcon :name="expanded[item.id] ? 'expand_less' : 'expand_more'" />
              </VaSidebarItemContent>

              <VaCollapse v-model="expanded[item.id]">
                <div class="children">
                  <template v-for="child in item.children" :key="child.id">
                    <VaSidebarItem
                      v-if="hasChildren(child)"
                      :active="isDescendantActive(child) || isMenuActive(child.path)"
                      class="child-parent"
                    >
                      <VaSidebarItemContent class="menu-child-parent" @click.stop="toggleExpand(child.id)">
                        <VaIcon :name="child.icon || 'chevron_right'" size="small" />
                        <VaSidebarItemTitle>{{ child.name }}</VaSidebarItemTitle>
                        <span class="spacer"></span>
                        <VaIcon :name="expanded[child.id] ? 'expand_less' : 'expand_more'" />
                      </VaSidebarItemContent>

                      <VaCollapse v-model="expanded[child.id]">
                        <div class="grandchildren">
                          <VaSidebarItem
                            v-for="grand in child.children"
                            :key="grand.id"
                            :to="grand.path"
                            :active="isMenuActive(grand.path)"
                            class="grandchild-item"
                          >
                            <VaSidebarItemContent>
                              <VaIcon :name="grand.icon || 'chevron_right'" size="small" />
                              <VaSidebarItemTitle>{{ grand.name }}</VaSidebarItemTitle>
                            </VaSidebarItemContent>
                          </VaSidebarItem>
                        </div>
                      </VaCollapse>
                    </VaSidebarItem>

                    <VaSidebarItem
                      v-else
                      :to="child.path"
                      :active="isMenuActive(child.path)"
                      class="child-item"
                    >
                      <VaSidebarItemContent>
                        <VaIcon :name="child.icon || 'chevron_right'" size="small" />
                        <VaSidebarItemTitle>{{ child.name }}</VaSidebarItemTitle>
                      </VaSidebarItemContent>
                    </VaSidebarItem>
                  </template>
                </div>
              </VaCollapse>
            </VaSidebarItem>

            <VaSidebarItem
              v-else
              :to="item.path"
              :active="isMenuActive(item.path)"
            >
              <VaSidebarItemContent>
                <VaIcon :name="item.icon" />
                <VaSidebarItemTitle>{{ item.name }}</VaSidebarItemTitle>
              </VaSidebarItemContent>
            </VaSidebarItem>
          </template>
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
import { ref, computed, onMounted, watch } from 'vue'
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

// 확장 상태 관리 및 유틸
const expanded = ref<Record<number, boolean>>({})
const hasChildren = (item: any) => Array.isArray(item.children) && item.children.length > 0
const isMenuActive = (path: string | undefined) => path ? route.path.startsWith(path) : false

// 하위(손자 포함) 어느 항목이라도 현재 경로와 일치하면 true
const isDescendantActive = (item: any): boolean => {
  if (!hasChildren(item)) return false
  return item.children.some((c: any) => isMenuActive(c.path) || isDescendantActive(c))
}

// 현재 경로 변경 시 부모/중간 메뉴들을 자동으로 펼침 상태로 동기화
const updateExpandedByRoute = () => {
  const traverse = (nodes: any[]) => {
    nodes.forEach((n: any) => {
      if (hasChildren(n)) {
        expanded.value[n.id] = isDescendantActive(n)
        traverse(n.children)
      }
    })
  }
  traverse(menuItems.value)
}

watch(
  () => route.path,
  () => {
    updateExpandedByRoute()
  },
  { immediate: true }
)

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

// 경로로 메뉴 찾기
const findMenuByPath = (path: string) => {
  return menuItems.value.find((item: any) => item.path === path)
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
    // 최초 진입 시 현재 경로 기준으로 펼침 동기화
    updateExpandedByRoute()
  }
})
</script>

<style scoped>
/* 기본 레이아웃 */
.admin-layout {
  height: 100vh;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

/* 사이드바 헤더 개선 */
.sidebar-header {
  padding: 1.75rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  backdrop-filter: blur(10px);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-text {
  font-size: 1.375rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.025em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 메인 콘텐츠 */
.main-content {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--va-background-secondary);
}

/* 네비게이션 바 개선 */
.navbar {
  border-bottom: 1px solid var(--va-background-border);
  padding: 0 1.75rem;
  height: 68px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.page-content {
  flex: 1;
  overflow: auto;
  padding: 2rem;
  background-color: var(--va-background-secondary);
}

/* 메뉴 아이템 레이아웃 개선 */
.menu-parent {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin: 0.25rem 0.5rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.menu-parent:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(4px);
}

.menu-child-parent {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0.625rem 1rem;
  border-radius: 6px;
  margin: 0.125rem 0.75rem;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  font-size: 0.925rem;
}

.menu-child-parent:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(2px);
}

.spacer {
  flex: 1;
}

/* 중첩 메뉴 간격 체계화 */
.children {
  padding-left: 0.75rem;
  margin-top: 0.25rem;
  border-left: 2px solid rgba(255, 255, 255, 0.1);
  margin-left: 1.5rem;
}

.grandchildren {
  padding-left: 1rem;
  margin-top: 0.25rem;
  border-left: 2px solid rgba(255, 255, 255, 0.08);
  margin-left: 1.25rem;
}

/* 타이포그래피 개선 */
.child-item .va-sidebar-item__title {
  font-size: 0.875rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.4;
}

.child-parent .va-sidebar-item__title {
  font-size: 0.925rem;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.95);
  line-height: 1.4;
}

.grandchild-item .va-sidebar-item__title {
  font-size: 0.825rem;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.4;
}

/* 활성 상태 스타일 */
.va-sidebar-item--active .menu-parent,
.va-sidebar-item--active .menu-child-parent {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  border-left: 3px solid rgba(255, 255, 255, 0.8);
}

.va-sidebar-item--active .va-sidebar-item__title {
  color: white;
  font-weight: 700;
}

/* 반응형 디자인 개선 */
@media (max-width: 1024px) {
  .page-content {
    padding: 1.5rem;
  }
  
  .navbar {
    padding: 0 1.5rem;
    height: 64px;
  }
  
  .sidebar-header {
    padding: 1.5rem 1rem;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
  
  .navbar {
    padding: 0 1rem;
    height: 60px;
  }
  
  .sidebar-header {
    padding: 1.25rem 0.875rem;
  }
  
  .logo-text {
    font-size: 1.25rem;
  }
  
  .menu-parent {
    padding: 0.625rem 0.875rem;
    margin: 0.125rem 0.375rem;
  }
  
  .menu-child-parent {
    padding: 0.5rem 0.875rem;
    margin: 0.125rem 0.5rem;
  }
}

@media (max-width: 480px) {
  .page-content {
    padding: 0.75rem;
  }
  
  .navbar {
    padding: 0 0.75rem;
  }
  
  .children {
    padding-left: 0.5rem;
    margin-left: 1rem;
  }
  
  .grandchildren {
    padding-left: 0.75rem;
    margin-left: 0.875rem;
  }
}

/* 다크 모드 지원 개선 */
.va-dark {
  .navbar {
    background: rgba(26, 32, 44, 0.95);
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }
  
  .page-content {
    background-color: var(--va-background-primary);
  }
  
  .sidebar-header {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
    border-bottom-color: rgba(255, 255, 255, 0.08);
  }
  
  .menu-parent:hover {
    background: rgba(255, 255, 255, 0.08);
  }
  
  .menu-child-parent:hover {
    background: rgba(255, 255, 255, 0.06);
  }
}

/* 애니메이션 효과 */
@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.va-sidebar-item {
  animation: slideIn 0.3s ease-out;
}

/* 포커스 상태 개선 */
.menu-parent:focus,
.menu-child-parent:focus {
  outline: 2px solid rgba(255, 255, 255, 0.5);
  outline-offset: 2px;
}

/* 스크롤바 스타일링 */
.va-sidebar::-webkit-scrollbar {
  width: 6px;
}

.va-sidebar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.va-sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

.va-sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}
</style>
<template>
  <VaLayout class="main-layout">
    <!-- 사이드바 -->
    <template #left>
      <VaSidebar
        v-model="isSidebarVisible"
        :width="sidebarWidth"
        :minimized="isSidebarMinimized"
        :minimized-width="minimizedSidebarWidth"
        color="primary"
        gradient
      >
        <!-- 로고 영역 -->
        <div class="sidebar-header">
          <div class="logo-container">
            <VaIcon
              name="admin_panel_settings"
              size="2rem"
              color="#ffffff"
            />
            <Transition name="fade">
              <span
                v-if="!isSidebarMinimized"
                class="logo-text"
              >
                SkyBoot Admin
              </span>
            </Transition>
          </div>
        </div>

        <!-- 네비게이션 메뉴 -->
        <VaSidebarItem
          v-for="menuItem in visibleMenus"
          :key="menuItem.id"
          :to="menuItem.path"
          :active="isMenuActive(menuItem)"
        >
          <VaSidebarItemContent>
            <VaIcon
              :name="menuItem.icon || 'folder'"
              slot="left"
            />
            <VaSidebarItemTitle>
              {{ menuItem.name }}
            </VaSidebarItemTitle>
          </VaSidebarItemContent>
          
          <!-- 하위 메뉴 -->
          <template v-if="menuItem.children && menuItem.children.length > 0">
            <VaSidebarItem
              v-for="child in menuItem.children"
              :key="child.id"
              :to="child.path"
              :active="isMenuActive(child)"
            >
              <VaSidebarItemContent>
                <VaIcon
                  :name="child.icon || 'circle'"
                  slot="left"
                  size="small"
                />
                <VaSidebarItemTitle>
                  {{ child.name }}
                </VaSidebarItemTitle>
              </VaSidebarItemContent>
            </VaSidebarItem>
          </template>
        </VaSidebarItem>

        <!-- 사이드바 하단 -->
        <template #bottom>
          <div class="sidebar-footer">
            <VaButton
              preset="secondary"
              color="secondary"
              size="small"
              class="toggle-btn"
              @click="toggleSidebar"
            >
              <VaIcon
                :name="isSidebarMinimized ? 'chevron_right' : 'chevron_left'"
              />
            </VaButton>
          </div>
        </template>
      </VaSidebar>
    </template>

    <!-- 메인 콘텐츠 -->
    <template #top>
      <!-- 상단 네비게이션 바 -->
      <VaNavbar class="main-navbar" color="background-primary">
        <template #left>
          <!-- 모바일 메뉴 토글 -->
          <VaButton
            preset="secondary"
            color="secondary"
            icon="menu"
            class="mobile-menu-btn"
            @click="toggleMobileSidebar"
          />
          
          <!-- 브레드크럼 -->
          <VaBreadcrumbs
            class="breadcrumbs"
            :items="breadcrumbItems"
            color="primary"
          />
        </template>

        <template #right>
          <!-- 테마 토글 -->
          <VaButton
            preset="secondary"
            color="secondary"
            :icon="themeStore.isDark ? 'light_mode' : 'dark_mode'"
            class="theme-toggle"
            @click="themeStore.toggleTheme"
          />

          <!-- 알림 -->
          <VaDropdown
            class="notification-dropdown"
            placement="bottom-end"
          >
            <template #anchor>
              <VaButton
                preset="secondary"
                color="secondary"
                icon="notifications"
              >
                <VaBadge
                  v-if="unreadNotifications > 0"
                  :text="unreadNotifications.toString()"
                  color="danger"
                  class="notification-badge"
                />
              </VaButton>
            </template>

            <VaDropdownContent class="notification-content">
              <div class="notification-header">
                <h4>알림</h4>
                <VaButton
                  preset="secondary"
                  size="small"
                  @click="markAllAsRead"
                >
                  모두 읽음
                </VaButton>
              </div>
              
              <div class="notification-list">
                <div
                  v-for="notification in notifications"
                  :key="notification.id"
                  class="notification-item"
                  :class="{ unread: !notification.read }"
                >
                  <VaIcon
                    :name="notification.icon"
                    :color="notification.color"
                    size="small"
                  />
                  <div class="notification-content">
                    <div class="notification-title">{{ notification.title }}</div>
                    <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
                  </div>
                </div>
              </div>
              
              <div class="notification-footer">
                <VaButton
                  preset="secondary"
                  size="small"
                  class="w-full"
                >
                  모든 알림 보기
                </VaButton>
              </div>
            </VaDropdownContent>
          </VaDropdown>

          <!-- 사용자 메뉴 -->
          <VaDropdown
            class="user-dropdown"
            placement="bottom-end"
          >
            <template #anchor>
              <div class="user-info">
                <VaAvatar
                  :src="currentUser?.avatar"
                  :fallback-text="currentUser?.username?.charAt(0).toUpperCase()"
                  size="small"
                  color="primary"
                />
                <span v-if="!isMobile" class="username">
                  {{ currentUser?.username }}
                </span>
                <VaIcon name="expand_more" size="small" />
              </div>
            </template>

            <VaDropdownContent class="user-menu">
              <VaList>
                <VaListItem
                  clickable
                  @click="goToProfile"
                >
                  <VaListItemSection avatar>
                    <VaIcon name="person" />
                  </VaListItemSection>
                  <VaListItemSection>
                    <VaListItemLabel>프로필</VaListItemLabel>
                  </VaListItemSection>
                </VaListItem>
                
                <VaListItem
                  clickable
                  @click="goToSettings"
                >
                  <VaListItemSection avatar>
                    <VaIcon name="settings" />
                  </VaListItemSection>
                  <VaListItemSection>
                    <VaListItemLabel>설정</VaListItemLabel>
                  </VaListItemSection>
                </VaListItem>
                
                <VaSeparator />
                
                <VaListItem
                  clickable
                  @click="handleLogout"
                >
                  <VaListItemSection avatar>
                    <VaIcon name="logout" color="danger" />
                  </VaListItemSection>
                  <VaListItemSection>
                    <VaListItemLabel class="text-danger">
                      로그아웃
                    </VaListItemLabel>
                  </VaListItemSection>
                </VaListItem>
              </VaList>
            </VaDropdownContent>
          </VaDropdown>
        </template>
      </VaNavbar>
    </template>

    <!-- 메인 콘텐츠 영역 -->
    <template #content>
      <main class="main-content">
        <RouterView />
      </main>
    </template>
  </VaLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useMenuStore } from '../../stores/menu';
import { useThemeStore } from '../../stores/theme';
import { useToast } from 'vuestic-ui';
import type { MenuItem } from '../../stores/menu';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const menuStore = useMenuStore();
const themeStore = useThemeStore();
const { init: notify } = useToast();

// 사이드바 상태
const isSidebarVisible = ref(true);
const isSidebarMinimized = ref(false);
const sidebarWidth = '280px';
const minimizedSidebarWidth = '64px';

// 모바일 감지
const isMobile = ref(false);

// 알림 데이터
const notifications = ref([
  {
    id: 1,
    title: '새로운 사용자가 등록되었습니다',
    icon: 'person_add',
    color: 'success',
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
    read: false,
  },
  {
    id: 2,
    title: '시스템 업데이트가 완료되었습니다',
    icon: 'system_update',
    color: 'info',
    timestamp: new Date(Date.now() - 1000 * 60 * 30),
    read: false,
  },
  {
    id: 3,
    title: '백업이 성공적으로 완료되었습니다',
    icon: 'backup',
    color: 'success',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2),
    read: true,
  },
]);

// 계산된 속성
const currentUser = computed(() => authStore.user);
const visibleMenus = computed(() => menuStore.activeMenus);
const unreadNotifications = computed(() => 
  notifications.value.filter(n => !n.read).length
);

// 브레드크럼 아이템
const breadcrumbItems = computed(() => {
  const items = [];
  const pathSegments = route.path.split('/').filter(Boolean);
  
  items.push({ label: '홈', to: '/dashboard' });
  
  let currentPath = '';
  pathSegments.forEach((segment, index) => {
    currentPath += `/${segment}`;
    
    // 메뉴에서 해당 경로의 이름 찾기
    const menuItem = findMenuByPath(currentPath);
    const label = menuItem?.name || segment.charAt(0).toUpperCase() + segment.slice(1);
    
    items.push({
      label,
      to: index === pathSegments.length - 1 ? undefined : currentPath,
    });
  });
  
  return items;
});

// 메뉴 관련 함수
const findMenuByPath = (path: string): MenuItem | null => {
  const findInMenus = (menus: MenuItem[]): MenuItem | null => {
    for (const menu of menus) {
      if (menu.path === path) {
        return menu;
      }
      if (menu.children) {
        const found = findInMenus(menu.children);
        if (found) return found;
      }
    }
    return null;
  };
  
  return findInMenus(menuStore.menuTree);
};

const isMenuActive = (menuItem: MenuItem): boolean => {
  return route.path === menuItem.path || route.path.startsWith(menuItem.path + '/');
};

// 사이드바 토글
const toggleSidebar = () => {
  isSidebarMinimized.value = !isSidebarMinimized.value;
};

const toggleMobileSidebar = () => {
  isSidebarVisible.value = !isSidebarVisible.value;
};

// 알림 관련 함수
const markAllAsRead = () => {
  notifications.value.forEach(notification => {
    notification.read = true;
  });
};

const formatTime = (timestamp: Date): string => {
  const now = new Date();
  const diff = now.getTime() - timestamp.getTime();
  const minutes = Math.floor(diff / (1000 * 60));
  const hours = Math.floor(diff / (1000 * 60 * 60));
  
  if (minutes < 1) {
    return '방금 전';
  } else if (minutes < 60) {
    return `${minutes}분 전`;
  } else {
    return `${hours}시간 전`;
  }
};

// 네비게이션 함수
const goToProfile = () => {
  router.push('/profile');
};

const goToSettings = () => {
  router.push('/settings');
};

const handleLogout = async () => {
  try {
    await authStore.logout();
    
    notify({
      message: '로그아웃되었습니다.',
      color: 'success',
      duration: 3000,
    });
    
    router.push('/login');
  } catch (error: any) {
    console.error('로그아웃 실패:', error);
    
    notify({
      message: error.message || '로그아웃 중 오류가 발생했습니다.',
      color: 'danger',
      duration: 5000,
    });
  }
};

// 반응형 처리
const handleResize = () => {
  isMobile.value = window.innerWidth < 768;
  
  if (isMobile.value) {
    isSidebarVisible.value = false;
    isSidebarMinimized.value = false;
  } else {
    isSidebarVisible.value = true;
  }
};

// 라이프사이클
onMounted(() => {
  handleResize();
  window.addEventListener('resize', handleResize);
  
  // 메뉴 로드
  menuStore.fetchMenuTree();
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
});
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.sidebar-header {
  padding: 1.5rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: white;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 600;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.toggle-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.main-navbar {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e0e0e0;
}

.mobile-menu-btn {
  display: none;
}

.breadcrumbs {
  margin-left: 1rem;
}

.theme-toggle {
  margin-right: 0.5rem;
}

.notification-dropdown,
.user-dropdown {
  margin-left: 0.5rem;
}

.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
}

.notification-content {
  width: 320px;
  max-height: 400px;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.notification-header h4 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.notification-list {
  max-height: 240px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: #f8f9fa;
}

.notification-item.unread {
  background-color: #f0f8ff;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.75rem;
  color: #666;
}

.notification-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #e0e0e0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f8f9fa;
}

.username {
  font-weight: 500;
  color: #333;
}

.user-menu {
  min-width: 200px;
}

.main-content {
  padding: 1.5rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 64px);
}

.w-full {
  width: 100%;
}

.text-danger {
  color: #f44336;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .mobile-menu-btn {
    display: inline-flex;
    margin-right: 0.5rem;
  }
  
  .breadcrumbs {
    display: none;
  }
  
  .username {
    display: none;
  }
  
  .main-content {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0.75rem;
  }
  
  .notification-content {
    width: 280px;
  }
}
</style>
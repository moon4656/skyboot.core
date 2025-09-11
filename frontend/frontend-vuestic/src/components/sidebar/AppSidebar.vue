<template>
  <VaSidebar
    v-model="isSidebarMinimized"
    :width="sidebarWidth"
    :minimized-width="sidebarMinimizedWidth"
    minimized
    hover-opacity
  >
    <!-- 로딩 상태 -->
    <div v-if="menuStore.isLoading" class="p-4">
      <VaSkeleton height="40px" class="mb-2" />
      <VaSkeleton height="40px" class="mb-2" />
      <VaSkeleton height="40px" class="mb-2" />
    </div>
    
    <!-- 에러 상태 -->
    <div v-else-if="menuStore.error" class="p-4">
      <VaAlert color="danger" class="mb-4">
        메뉴를 불러오는데 실패했습니다.
      </VaAlert>
      <VaButton size="small" @click="menuStore.fetchMenuItems()">
        다시 시도
      </VaButton>
    </div>
    
    <!-- 동적 메뉴 렌더링 -->
    <template v-else>
      <template v-for="menuItem in menuStore.menuItems" :key="menuItem.id">
        <DynamicMenuItem 
          :menu-item="menuItem"
          :current-route="currentRoute"
          :depth="0"
          @navigate="handleNavigation"
        />
      </template>
    </template>
    
    <!-- 메뉴가 없는 경우 -->
    <div v-if="!menuStore.isLoading && !menuStore.error && menuStore.menuItems.length === 0" class="p-4">
      <VaAlert color="info">
        사용 가능한 메뉴가 없습니다.
      </VaAlert>
    </div>
  </VaSidebar>
</template>
<script lang="ts" setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMenuStore } from '../../stores/menu-store'
import { useAuthStore } from '../../stores/auth-store'
import DynamicMenuItem from './DynamicMenuItem.vue'

const route = useRoute()
const router = useRouter()
const menuStore = useMenuStore()
const authStore = useAuthStore()

const isSidebarMinimized = ref(false)
const sidebarWidth = '240px'
const sidebarMinimizedWidth = '64px'

// 현재 라우트 정보
const currentRoute = computed(() => route.path)

// 네비게이션 처리
const handleNavigation = async (menuItem: any) => {
  if (menuItem.path) {
    try {
      await router.push(menuItem.path)
    } catch (error) {
      console.error('네비게이션 오류:', error)
    }
  }
}

// 컴포넌트 마운트 시 메뉴 데이터 로드
onMounted(async () => {
  if (authStore.isLoggedIn && menuStore.menuItems.length === 0) {
    await menuStore.fetchMenuItems()
  }
})
</script>

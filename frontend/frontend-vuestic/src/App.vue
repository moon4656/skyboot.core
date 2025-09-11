<template>
  <RouterView />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth-store'
import { useMenuStore } from './stores/menu-store'

const authStore = useAuthStore()
const menuStore = useMenuStore()

// 애플리케이션 초기화
onMounted(async () => {
  // 인증 상태 초기화
  await authStore.initializeAuth()
  
  // 로그인된 사용자의 경우 메뉴 데이터 로드
  if (authStore.isLoggedIn) {
    await menuStore.fetchMenuItems()
  }
})
</script>

<style lang="scss">
#app {
  font-family: 'Inter', Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  min-width: 20rem;
}
</style>

import { createPinia } from 'pinia'

// 스토어들을 내보내기
export { useUserStore } from './user-store'
export { useAuthStore } from './auth-store'
export { useMenuStore } from './menu-store'

export default createPinia()

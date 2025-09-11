import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useMenuPermissions } from '@/composables/useMenuPermissions'

// 레이아웃 컴포넌트
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const AuthLayout = () => import('@/layouts/AuthLayout.vue')

// 페이지 컴포넌트
const Dashboard = () => import('@/views/Dashboard.vue')
const Login = () => import('@/views/auth/Login.vue')
const Users = () => import('@/views/admin/Users.vue')
const Menus = () => import('@/views/admin/Menus.vue')
const Unauthorized = () => import('@/views/admin/Unauthorized.vue')
const Programs = () => import('@/views/admin/Programs.vue')
const MenuPermissions = () => import('@/views/admin/MenuPermissions.vue')
const UserPermissions = () => import('@/views/admin/UserPermissions.vue')
const CommonCodes = () => import('@/views/admin/CommonCodes.vue')
const BoardManagement = () => import('@/views/admin/BoardManagement.vue')
const ComingSoon = () => import('@/views/ComingSoon.vue')

const routes: Array<RouteRecordRaw> = [
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        path: 'login',
        name: 'Login',
        component: Login,
        meta: { requiresAuth: false }
      }
    ]
  },
  {
    path: '/',
    redirect: (to) => {
      const authStore = useAuthStore()
      return authStore.isAuthenticated ? '/admin' : '/auth/login'
    }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: Dashboard
      },
      {
        path: 'admin',
        children: [
          {
            path: 'users',
            name: 'Users',
            component: Users,
            meta: { requiresAuth: true }
          },
          {
            path: 'menus',
            name: 'Menus',
            component: Menus,
            meta: { requiresAuth: true }
          },
          {
            path: 'unauthorized',
            name: 'Unauthorized',
            component: Unauthorized,
            meta: { requiresAuth: true }
          },
          {
            path: 'programs',
            name: 'Programs',
            component: Programs,
            meta: { requiresAuth: true }
          },
          {
            path: 'menu-permissions',
            name: 'MenuPermissions',
            component: MenuPermissions,
            meta: { requiresAuth: true }
          },
          {
            path: 'user-permissions',
            name: 'UserPermissions',
            component: UserPermissions,
            meta: { requiresAuth: true }
          },
          {
            path: 'common-codes',
            name: 'CommonCodes',
            component: CommonCodes,
            meta: { requiresAuth: true }
          },
          {
            path: 'board-management',
            name: 'BoardManagement',
            component: BoardManagement,
            meta: { requiresAuth: true }
          }
        ]
      },
      {
        path: 'coming-soon',
        name: 'ComingSoon',
        component: ComingSoon
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/auth/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 라우터 가드
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const { canAccessPath } = useMenuPermissions()
  
  // 로그인 페이지 접근 시 이미 로그인된 사용자는 대시보드로 리다이렉트
  if (to.path === '/auth/login') {
    if (authStore.isAuthenticated) {
      next('/admin')
      return
    }
    next()
    return
  }
  
  // 인증이 필요한 페이지인지 확인
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true)
  
  if (requiresAuth) {
    // 1. Access Token 존재 여부 확인
    if (!authStore.accessToken) {
      console.warn('⚠️ [Router Guard] Access Token이 없습니다.')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 2. 토큰 유효성 검사
    if (!authStore.isAuthenticated) {
      console.warn('⚠️ [Router Guard] Access Token이 만료되었습니다. 토큰 갱신을 시도합니다.')
      
      // 3. 토큰 갱신 시도
      const refreshed = await authStore.refreshAccessToken()
      if (!refreshed) {
        console.warn('⚠️ [Router Guard] 토큰 갱신에 실패했습니다.')
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // 4. 사용자 정보 로드
    if (!authStore.user) {
      try {
        await authStore.refreshUserInfo()
      } catch (error) {
        console.error('❌ [Router Guard] 사용자 정보 로드 실패:', error)
        authStore.clearTokens()
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
    }
    
    // 5. 권한 체크 (관리자 페이지의 경우)
    if (to.path.startsWith('/admin') && 
        to.path !== '/admin' && 
        to.name !== 'Dashboard' && 
        to.name !== 'Unauthorized') {
      if (!canAccessPath(to.path)) {
        console.warn(`⚠️ [Router Guard] 권한 없음: ${to.path}`)
        next({ name: 'Unauthorized' })
        return
      }
    }
  }
  
  next()
})

export default router
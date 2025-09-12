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
const MenuTest = () => import('@/components/MenuTest.vue')

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
        path: 'dashboard',
        redirect: '/admin'
      },
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
        path: 'menu-test',
        name: 'MenuTest',
        component: MenuTest,
        meta: { requiresAuth: true }
      },
      {
        path: 'board-management',
        name: 'BoardManagement',
        component: BoardManagement,
        meta: { requiresAuth: true }
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
  
  console.log(`🔍 [Router Guard] 라우팅: ${from.path} → ${to.path}`)
  
  // 로그인 페이지 접근 시 이미 로그인된 사용자는 메인화면으로 리다이렉트
  if (to.path === '/auth/login') {
    if (authStore.isAuthenticated) {
      console.log('✅ [Router Guard] 이미 인증된 사용자 - 메인화면으로 리다이렉트')
      next('/admin')
      return
    }
    console.log('🔓 [Router Guard] 로그인 페이지 접근 허용')
    next()
    return
  }
  
  // 인증이 필요한 페이지인지 확인
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth === true)
  
  if (requiresAuth) {
    console.log('🔒 [Router Guard] 인증이 필요한 페이지 접근 시도')
    
    // 1. Access Token 존재 여부 확인
    if (!authStore.accessToken) {
      console.warn('⚠️ [Router Guard] Access Token이 없습니다 - 로그인 페이지로 이동')
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }
    
    // 2. 토큰 유효성 검사
    if (!authStore.isAuthenticated) {
      console.warn('⚠️ [Router Guard] Access Token이 만료되었습니다 - 토큰 갱신 시도')
      
      // 3. 토큰 갱신 시도
      const refreshed = await authStore.refreshAccessToken()
      if (!refreshed) {
        console.warn('⚠️ [Router Guard] 토큰 갱신에 실패했습니다 - 로그인 페이지로 이동')
        next({ name: 'Login', query: { redirect: to.fullPath } })
        return
      }
      console.log('✅ [Router Guard] 토큰 갱신 성공')
    }
    
    // 4. 사용자 정보 로드
    if (!authStore.user) {
      try {
        console.log('📡 [Router Guard] 사용자 정보 로드 중...')
        await authStore.refreshUserInfo()
        console.log('✅ [Router Guard] 사용자 정보 로드 완료')
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
      console.log(`🔐 [Router Guard] 권한 체크: ${to.path}`)
      if (!canAccessPath(to.path)) {
        console.warn(`⚠️ [Router Guard] 권한 없음: ${to.path} - Unauthorized 페이지로 이동`)
        next({ name: 'Unauthorized' })
        return
      }
      console.log('✅ [Router Guard] 권한 확인 완료')
    }
  }
  
  // 6. 모든 검증 통과 - 페이지 접근 허용
  console.log(`✅ [Router Guard] 페이지 접근 허용: ${to.path}`)
  next()
})

export default router
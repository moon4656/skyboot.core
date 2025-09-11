import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import AuthLayout from '../layouts/AuthLayout.vue'
import AppLayout from '../layouts/AppLayout.vue'
import { useAuthStore } from '../stores/auth-store'
import { useMenuStore } from '../stores/menu-store'

import RouteViewComponent from '../layouts/RouterBypass.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'login' },
  },
  {
    name: 'admin',
    path: '/',
    component: AppLayout,
    redirect: { name: 'login' },
    children: [
      {
        name: 'dashboard',
        path: 'dashboard',
        component: () => import('../pages/admin/dashboard/Dashboard.vue'),
      },
      {
        name: 'settings',
        path: 'settings',
        component: () => import('../pages/settings/Settings.vue'),
      },
      {
        name: 'preferences',
        path: 'preferences',
        component: () => import('../pages/preferences/Preferences.vue'),
      },
      {
        name: 'users',
        path: 'users',
        component: () => import('../pages/users/UsersPage.vue'),
      },
      {
        name: 'projects',
        path: 'projects',
        component: () => import('../pages/projects/ProjectsPage.vue'),
      },
      {
        name: 'payments',
        path: '/payments',
        component: RouteViewComponent,
        children: [
          {
            name: 'payment-methods',
            path: 'payment-methods',
            component: () => import('../pages/payments/PaymentsPage.vue'),
          },
          {
            name: 'billing',
            path: 'billing',
            component: () => import('../pages/billing/BillingPage.vue'),
          },
          {
            name: 'pricing-plans',
            path: 'pricing-plans',
            component: () => import('../pages/pricing-plans/PricingPlans.vue'),
          },
        ],
      },
      {
        name: 'faq',
        path: '/faq',
        component: () => import('../pages/faq/FaqPage.vue'),
      },
    ],
  },
  {
    path: '/auth',
    component: AuthLayout,
    children: [
      {
        name: 'login',
        path: 'login',
        component: () => import('../pages/auth/Login.vue'),
      },
      {
        name: 'signup',
        path: 'signup',
        component: () => import('../pages/auth/Signup.vue'),
      },
      {
        name: 'recover-password',
        path: 'recover-password',
        component: () => import('../pages/auth/RecoverPassword.vue'),
      },
      {
        name: 'recover-password-email',
        path: 'recover-password-email',
        component: () => import('../pages/auth/CheckTheEmail.vue'),
      },
      {
        path: '',
        redirect: { name: 'login' },
      },
    ],
  },
  {
    name: '404',
    path: '/404',
    component: () => import('../pages/404.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // scrollBehavior 임시 비활성화
  // scrollBehavior(to, from, savedPosition) {
  //   if (savedPosition) {
  //     return savedPosition
  //   }
  //   return { top: 0 }
  // },
  routes,
})

// 라우터 가드 설정
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const menuStore = useMenuStore()
  
  // 인증이 필요하지 않은 페이지 목록
  const publicPages = ['/auth/login', '/auth/signup', '/auth/recover-password', '/auth/recover-password-email', '/404']
  const authRequired = !publicPages.some(page => to.path.startsWith(page))
  
  // 로그인 상태 확인
  if (authRequired && !authStore.isLoggedIn) {
    // 인증이 필요하지만 로그인하지 않은 경우
    console.log('인증이 필요합니다. 로그인 페이지로 이동합니다.')
    return next('/auth/login')
  }
  
  // 로그인된 사용자가 인증 페이지에 접근하는 경우 대시보드로 리다이렉트
  if (!authRequired && authStore.isLoggedIn && to.path.startsWith('/auth')) {
    return next('/dashboard')
  }
  
  // 로그인된 사용자의 경우 메뉴 데이터가 없으면 로드
  if (authStore.isLoggedIn && menuStore.menuItems.length === 0) {
    await menuStore.fetchMenuItems()
  }
  
  next()
})

// 라우터 에러 핸들링
router.onError((error) => {
  console.error('라우터 에러:', error)
})

export default router

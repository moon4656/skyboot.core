import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useMenuStore } from '../stores/menu';

import AdminLayout from '../layouts/AdminLayout.vue';
import AuthLayout from '../layouts/AuthLayout.vue';
import LoginPage from '../pages/auth/LoginPage.vue';
import DashboardPage from '../pages/DashboardPage.vue';
import NotFoundPage from '../pages/error/NotFoundPage.vue';
import ForbiddenPage from '../pages/error/ForbiddenPage.vue';
import UserManagementPage from '../pages/admin/UserManagementPage.vue';
import MenuManagementPage from '../pages/admin/MenuManagementPage.vue';
import ProgramManagementPage from '../pages/admin/ProgramManagementPage.vue';
import OrgManagementPage from '../pages/admin/OrgManagementPage.vue';
import BoardManagementPage from '../pages/admin/BoardManagementPage.vue';

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginPage,
    meta: {
      layout: 'auth',
      requiresAuth: false,
      title: '로그인',
    },
  },
  {
    path: '/',
    component: AdminLayout,
    meta: {
      requiresAuth: true,
    },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: DashboardPage,
        meta: {
          title: '대시보드',
          icon: 'home',
        },
      },
      {
        path: '/admin',
        name: 'admin',
        meta: {
          title: '관리자',
          icon: 'settings',
        },
        children: [
          {
            path: 'users',
            name: 'admin-users',
            component: UserManagementPage,
            meta: {
              title: '사용자 관리',
              icon: 'users',
              requiresAuth: true,
            },
          },
          {
            path: 'menus',
            name: 'admin-menus',
            component: MenuManagementPage,
            meta: {
              title: '메뉴 관리',
              icon: 'menu',
              requiresAuth: true,
            },
          },
          {
            path: 'programs',
            name: 'admin-programs',
            component: ProgramManagementPage,
            meta: {
              title: '프로그램 관리',
              icon: 'code',
              requiresAuth: true,
            },
          },
          {
            path: 'organizations',
            name: 'admin-organizations',
            component: OrgManagementPage,
            meta: {
              title: '조직 관리',
              icon: 'building',
              requiresAuth: true,
            },
          },
          {
            path: 'boards',
            name: 'admin-boards',
            component: BoardManagementPage,
            meta: {
              title: '게시판 관리',
              icon: 'clipboard',
              requiresAuth: true,
            },
          },
        ],
      },
    ],
  },
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenPage,
    meta: {
      title: '접근 권한 없음',
      requiresAuth: false,
    },
  },
  {
    path: '/404',
    name: 'not-found',
    component: NotFoundPage,
    meta: {
      title: '페이지를 찾을 수 없음',
      requiresAuth: false,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 전역 네비게이션 가드
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  const menuStore = useMenuStore();
  
  // 페이지 타이틀 설정
  if (to.meta.title) {
    document.title = `${to.meta.title} - SkyBoot Admin 2`;
  } else {
    document.title = 'SkyBoot Admin 3';
  }

  // 인증이 필요한 페이지인지 확인
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth) {
    // 인증되지 않은 사용자는 로그인 페이지로 리다이렉트
    if (!authStore.isAuthenticated) {
      next({
        name: 'login',
        query: { redirect: to.fullPath },
      });
      return;
    }

    // 메뉴 정보가 없으면 로드
    if (menuStore.menuTree.length === 0) {
      try {
        await menuStore.fetchMenuTree();
      } catch (error) {
        console.error('메뉴 로드 실패:', error);
      }
    }

    // 권한 체크 (메뉴 기반)
    if (to.name !== 'dashboard') {
      const menu = menuStore.getMenuByPath(to.path);
      if (menu && menu.meta?.roles) {
        // 사용자 권한 체크 로직 (현재는 기본적으로 허용)
        // 실제 구현에서는 사용자의 역할을 확인해야 함
        const userRoles: string[] = []; // 사용자 역할 정보
        const hasPermission = menu.meta.roles.some(role => userRoles.includes(role));
        
        if (!hasPermission) {
          next({ name: 'forbidden' });
          return;
        }
      }
    }
  } else {
    // 인증이 필요하지 않은 페이지
    if (to.name === 'login' && authStore.isAuthenticated) {
      // 이미 로그인된 사용자가 로그인 페이지에 접근하면 대시보드로 리다이렉트
      next({ name: 'dashboard' });
      return;
    }
  }

  next();
});

// 라우터 에러 핸들링
router.onError((error) => {
  console.error('라우터 에러:', error);
});

export default router;

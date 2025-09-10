import { createApp } from 'vue';
import { createPinia } from 'pinia';
import './style.css';
import App from './App.vue';
import router from './router';
import { createVuestic } from 'vuestic-ui';
import 'vuestic-ui/css';
import { useAuthStore } from './stores/auth';
import { useThemeStore } from './stores/theme';

const app = createApp(App);
const pinia = createPinia();

// Pinia 설치
app.use(pinia);

// Vuestic UI 설정
app.use(createVuestic({
  config: {
    colors: {
      variables: {
        // 라이트 모드 색상
        primary: '#1976d2',
        secondary: '#424242',
        success: '#4caf50',
        info: '#2196f3',
        warning: '#ff9800',
        danger: '#f44336',
        // 배경 색상
        backgroundPrimary: '#ffffff',
        backgroundSecondary: '#f5f5f5',
        backgroundElement: '#ffffff',
        backgroundBorder: '#dee5ed',
        // 텍스트 색상
        textPrimary: '#262824',
        textInverted: '#ffffff',
      },
      // 다크 모드 색상 정의
      dark: {
        primary: '#4fc3f7',
        secondary: '#90a4ae',
        success: '#66bb6a',
        info: '#42a5f5',
        warning: '#ffb74d',
        danger: '#ef5350',
        // 다크 모드 배경 색상
        backgroundPrimary: '#1a1a1a',
        backgroundSecondary: '#2d2d2d',
        backgroundElement: '#262626',
        backgroundBorder: '#404040',
        // 다크 모드 텍스트 색상
        textPrimary: '#ffffff',
        textInverted: '#262824',
      },
    },
    components: {
      VaButton: {
        round: false,
      },
      VaCard: {
        square: false,
      },
    },
  },
}));

// 라우터 설치
app.use(router);

// 앱 초기화
const initializeApp = async () => {
  try {
    // 테마 초기화
    const themeStore = useThemeStore();
    themeStore.initializeTheme();

    // 인증 상태 초기화
    const authStore = useAuthStore();
    await authStore.initializeAuth();

    console.log('✅ 애플리케이션 초기화 완료');
  } catch (error) {
    console.error('❌ 애플리케이션 초기화 실패:', error);
  }
};

// 앱 마운트 및 초기화
app.mount('#app');
initializeApp();

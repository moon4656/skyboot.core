import { defineStore } from 'pinia';
import { ref, computed, watch } from 'vue';

export type ThemeMode = 'light' | 'dark' | 'auto';

export interface ThemeConfig {
  mode: ThemeMode;
  primaryColor: string;
  sidebarCollapsed: boolean;
  compactMode: boolean;
}

export const useThemeStore = defineStore('theme', () => {
  
  // State
  const mode = ref<ThemeMode>('light');
  const primaryColor = ref('#1976d2');
  const sidebarCollapsed = ref(false);
  const compactMode = ref(false);
  const isLoading = ref(false);

  // 로컬 스토리지 키
  const THEME_STORAGE_KEY = 'admin-theme-config';

  // Getters
  const isDark = computed(() => {
    if (mode.value === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return mode.value === 'dark';
  });

  const themeConfig = computed<ThemeConfig>(() => ({
    mode: mode.value,
    primaryColor: primaryColor.value,
    sidebarCollapsed: sidebarCollapsed.value,
    compactMode: compactMode.value,
  }));

  // Actions
  const setThemeMode = (newMode: ThemeMode): void => {
    mode.value = newMode;
    applyTheme();
    saveThemeConfig();
  };

  const setPrimaryColor = (color: string): void => {
    primaryColor.value = color;
    applyTheme();
    saveThemeConfig();
  };

  const toggleSidebar = (): void => {
    sidebarCollapsed.value = !sidebarCollapsed.value;
    saveThemeConfig();
  };

  const setSidebarCollapsed = (collapsed: boolean): void => {
    sidebarCollapsed.value = collapsed;
    saveThemeConfig();
  };

  const toggleCompactMode = (): void => {
    compactMode.value = !compactMode.value;
    saveThemeConfig();
  };

  const setCompactMode = (compact: boolean): void => {
    compactMode.value = compact;
    saveThemeConfig();
  };

  // 테마 적용
  const applyTheme = (): void => {
    const root = document.documentElement;
    
    // 다크 모드 클래스 토글
    if (isDark.value) {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    } else {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    }

    // CSS 커스텀 프로퍼티로 테마 설정
    root.style.setProperty('--va-primary', primaryColor.value);
    root.style.setProperty('--va-primary-darken', primaryColor.value);
    root.style.setProperty('--va-primary-lighten', primaryColor.value);

    // CSS 커스텀 프로퍼티 설정
    root.style.setProperty('--va-primary', primaryColor.value);
  };

  // 테마 설정 저장
  const saveThemeConfig = (): void => {
    try {
      const config = {
        mode: mode.value,
        primaryColor: primaryColor.value,
        sidebarCollapsed: sidebarCollapsed.value,
        compactMode: compactMode.value,
      };
      localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(config));
    } catch (error) {
      console.error('테마 설정 저장 실패:', error);
    }
  };

  // 테마 설정 로드
  const loadThemeConfig = (): void => {
    try {
      const savedConfig = localStorage.getItem(THEME_STORAGE_KEY);
      if (savedConfig) {
        const config: ThemeConfig = JSON.parse(savedConfig);
        mode.value = config.mode || 'light';
        primaryColor.value = config.primaryColor || '#1976d2';
        sidebarCollapsed.value = config.sidebarCollapsed || false;
        compactMode.value = config.compactMode || false;
      }
    } catch (error) {
      console.error('테마 설정 로드 실패:', error);
      // 기본값으로 초기화
      resetTheme();
    }
  };

  // 테마 초기화
  const initializeTheme = (): void => {
    isLoading.value = true;
    
    try {
      loadThemeConfig();
      applyTheme();
      
      // 시스템 테마 변경 감지 (auto 모드일 때)
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      mediaQuery.addEventListener('change', () => {
        if (mode.value === 'auto') {
          applyTheme();
        }
      });
    } finally {
      isLoading.value = false;
    }
  };

  // 테마 리셋
  const resetTheme = (): void => {
    mode.value = 'light';
    primaryColor.value = '#1976d2';
    sidebarCollapsed.value = false;
    compactMode.value = false;
    applyTheme();
    saveThemeConfig();
  };

  // 미리 정의된 테마 색상
  const presetColors = [
    '#1976d2', // Blue
    '#388e3c', // Green
    '#f57c00', // Orange
    '#7b1fa2', // Purple
    '#c62828', // Red
    '#00796b', // Teal
    '#5d4037', // Brown
    '#455a64', // Blue Grey
  ];

  const applyPresetTheme = (colorIndex: number): void => {
    if (colorIndex >= 0 && colorIndex < presetColors.length) {
      setPrimaryColor(presetColors[colorIndex]);
    }
  };

  const toggleTheme = (): void => {
    const newMode = mode.value === 'light' ? 'dark' : 'light';
    setThemeMode(newMode);
  };

  // 테마 모드 변경 감지
  watch(mode, () => {
    applyTheme();
  });

  return {
    // State
    mode,
    primaryColor,
    sidebarCollapsed,
    compactMode,
    isLoading,
    
    // Getters
    isDark,
    themeConfig,
    presetColors,
    
    // Actions
    setThemeMode,
    setPrimaryColor,
    toggleSidebar,
    setSidebarCollapsed,
    toggleCompactMode,
    setCompactMode,
    applyTheme,
    initializeTheme,
    resetTheme,
    applyPresetTheme,
    toggleTheme,
  };
});
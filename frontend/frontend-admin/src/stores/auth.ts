import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authAPI, TokenManager } from '../api/client';
import type { User, LoginRequest, AuthState } from '../types/auth';

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null);
  const accessToken = ref<string | null>(TokenManager.getAccessToken());
  const refreshToken = ref<string | null>(TokenManager.getRefreshToken());
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value;
  });

  const authState = computed<AuthState>(() => ({
    user: user.value,
    accessToken: accessToken.value,
    refreshToken: refreshToken.value,
    isAuthenticated: isAuthenticated.value,
    isLoading: isLoading.value,
  }));

  // Actions
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    try {
      isLoading.value = true;
      error.value = null;

      const response = await authAPI.login(credentials);
      
      // 토큰 저장
      accessToken.value = response.access_token;
      refreshToken.value = response.refresh_token;
      TokenManager.setTokens(response.access_token, response.refresh_token);

      // 사용자 정보 조회
      await fetchUserProfile();
      console.log('After fetchUserProfile - User:', user.value);
      console.log('After fetchUserProfile - isAuthenticated:', isAuthenticated.value);

      return true;
    } catch (err: any) {
      error.value = err.response?.data?.detail || '로그인에 실패했습니다.';
      return false;
    } finally {
      isLoading.value = false;
    }
  };

  const logout = async (): Promise<void> => {
    try {
      await authAPI.logout();
    } catch (err) {
      console.error('로그아웃 API 호출 실패:', err);
    } finally {
      // 로컬 상태 초기화
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;
      error.value = null;
      TokenManager.clearTokens();
    }
  };

  const fetchUserProfile = async (): Promise<void> => {
    try {
      const userData = await authAPI.getProfile();
      console.log('FetchUserProfile response:', userData);
      if (userData) {
        user.value = userData;
      }
    } catch (error) {
      if (error.response && error.response.status === 401) {
        try {
          await refreshTokens();
          const userData = await authAPI.getProfile();
          if (userData) {
            user.value = userData;
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          logout();
        }
      } else {
        console.error('Failed to fetch user profile:', error);
        logout();
      }
    }
  };

  const refreshTokens = async (): Promise<boolean> => {
    try {
      const currentRefreshToken = refreshToken.value;
      if (!currentRefreshToken) {
        throw new Error('리프레시 토큰이 없습니다.');
      }

      const response = await authAPI.refreshToken(currentRefreshToken);
      
      accessToken.value = response.access_token;
      refreshToken.value = response.refresh_token;
      TokenManager.setTokens(response.access_token, response.refresh_token);

      return true;
    } catch (err) {
      console.error('토큰 갱신 실패:', err);
      await logout();
      return false;
    }
  };

  const initializeAuth = async (): Promise<void> => {
    const token = TokenManager.getAccessToken();
    if (token) {
      accessToken.value = token;
      refreshToken.value = TokenManager.getRefreshToken();
      
      try {
        await fetchUserProfile();
      } catch (err) {
        console.error('인증 초기화 실패:', err);
        await logout();
      }
    }
  };

  const clearError = (): void => {
    error.value = null;
  };

  const oneClickLogin = async (): Promise<boolean> => {
    // 개발용 원클릭 로그인
    return await login({
      username: 'admin',
      password: 'admin123'
    });
  };

  return {
    // State
    user,
    accessToken,
    refreshToken,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    authState,
    
    // Actions
    login,
    logout,
    fetchUserProfile,
    refreshTokens,
    initializeAuth,
    clearError,
    oneClickLogin,
  };
});
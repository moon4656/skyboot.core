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
      const userProfile = await authAPI.getProfile();
      user.value = userProfile;
    } catch (err: any) {
      console.error('사용자 프로필 조회 실패:', err);
      error.value = '사용자 정보를 불러올 수 없습니다.';
      // 프로필 조회 실패 시 토큰만 정리하고 로그아웃 API 호출하지 않음
      user.value = null;
      accessToken.value = null;
      refreshToken.value = null;
      TokenManager.clearTokens();
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
        // 초기화 실패 시 토큰만 정리
        user.value = null;
        accessToken.value = null;
        refreshToken.value = null;
        TokenManager.clearTokens();
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
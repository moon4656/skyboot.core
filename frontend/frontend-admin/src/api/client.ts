import axios from 'axios';
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import type { LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse, User } from '../types/auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 토큰 관리 유틸리티
class TokenManager {
  private static readonly ACCESS_TOKEN_KEY = 'access_token';
  private static readonly REFRESH_TOKEN_KEY = 'refresh_token';

  static getAccessToken(): string | null {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  }

  static setAccessToken(token: string): void {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, token);
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  static setRefreshToken(token: string): void {
    localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
  }

  static clearTokens(): void {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  }

  static setTokens(accessToken: string, refreshToken: string): void {
    this.setAccessToken(accessToken);
    this.setRefreshToken(refreshToken);
  }
}

// 요청 인터셉터: 모든 요청에 Authorization 헤더 추가
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = TokenManager.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터: 401 에러 시 토큰 갱신 시도
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // 401 에러이고 재시도하지 않은 요청인 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = TokenManager.getRefreshToken();
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        // 토큰 갱신 요청
        const response = await axios.post<RefreshTokenResponse>(
          `${API_BASE_URL}/auth/refresh`,
          { refresh_token: refreshToken }
        );

        const { access_token, refresh_token } = response.data;
        TokenManager.setTokens(access_token, refresh_token);

        // 원래 요청 재시도
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // 토큰 갱신 실패 시 로그아웃 처리
        TokenManager.clearTokens();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// API 함수들
export const authAPI = {
  // 로그인
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', {
      user_id: credentials.username,
      password: credentials.password
    });
    return response.data;
  },

  // 토큰 갱신
  refreshToken: async (refreshToken: string): Promise<RefreshTokenResponse> => {
    const response = await apiClient.post<RefreshTokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },

  // 로그아웃
  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout');
    TokenManager.clearTokens();
  },

  // 사용자 프로필 조회
  getProfile: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/v1/users/profile');
    return response.data;
  },

  // HTTP 메서드 추가
  get: async (url: string, config?: any) => {
    const response = await apiClient.get(url, config);
    return response.data;
  },

  post: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.post(url, data, config);
    return response.data;
  },

  put: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.put(url, data, config);
    return response.data;
  },

  patch: async (url: string, data?: any, config?: any) => {
    const response = await apiClient.patch(url, data, config);
    return response.data;
  },

  delete: async (url: string, config?: any) => {
    const response = await apiClient.delete(url, config);
    return response.data;
  },
};

// 메뉴 API
export const menuAPI = {
  // 메뉴 트리 조회
  getMenuTree: async () => {
    const response = await apiClient.get('/api/v1/menus/tree');
    return response;
  },

  // 메뉴 목록 조회
  getMenus: async () => {
    const response = await apiClient.get('/api/v1/menus');
    return response;
  },
};

export { apiClient, TokenManager };
export default apiClient;
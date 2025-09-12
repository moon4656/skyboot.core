/**
 * API 서비스 모듈
 * FastAPI 백엔드와의 통신을 담당
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { useAuthStore } from '@/stores/auth'
import router from '@/router'

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const API_TIMEOUT = 30000

// 토큰 저장 키 (스토어와 일치시킴)
const ACCESS_TOKEN_KEY = import.meta.env.VITE_TOKEN_STORAGE_KEY || 'skyboot_access_token'
const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_STORAGE_KEY || 'skyboot_refresh_token'

// Axios 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 공개 엔드포인트 목록 (토큰이 필요하지 않은 엔드포인트)
const PUBLIC_ENDPOINTS = [
  '/auth/login',
  '/auth/refresh',
  '/menus/tree/public',
  '/health'
]

// 요청 인터셉터: JWT 토큰 자동 추가
apiClient.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    // 공개 엔드포인트인지 확인
    const isPublicEndpoint = PUBLIC_ENDPOINTS.some(endpoint => 
      config.url?.includes(endpoint)
    )
    
    // 공개 엔드포인트가 아닌 경우에만 토큰 추가
    if (!isPublicEndpoint) {
      // localStorage에서 직접 토큰 가져오기 (반응성 문제 방지)
      const token = localStorage.getItem(ACCESS_TOKEN_KEY)
      
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    
    // 요청 로깅
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url} ${isPublicEndpoint ? '(Public)' : '(Auth)'}`)
    
    return config
  },
  (error) => {
    console.error('❌ Request Error:', error)
    return Promise.reject(error)
  }
)

// 응답 인터셉터: 토큰 갱신 및 에러 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // 성공 응답 로깅
    console.log(`✅ API Response: ${response.status} ${response.config.url}`)
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 401 에러 (인증 실패) 처리
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // localStorage에서 리프레시 토큰 가져오기 (스토어 키와 동일하게)
        const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY)
        
        if (refreshToken) {
          // 리프레시 토큰으로 새 액세스 토큰 요청
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          })
          
          const newAccessToken = refreshResponse.data.access_token
          localStorage.setItem(ACCESS_TOKEN_KEY, newAccessToken)
          
          // 원래 요청에 새 토큰 추가하여 재시도
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          }
          
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        // 리프레시 실패 시 로그아웃 처리
        console.error('❌ Token refresh failed:', refreshError)
        localStorage.removeItem(ACCESS_TOKEN_KEY)
        localStorage.removeItem(REFRESH_TOKEN_KEY)
        // 사용자 정보 키가 다른 경우를 대비해 둘 다 정리
        localStorage.removeItem('skyboot_user_info')
        localStorage.removeItem('user')
        window.location.href = '/auth/login'
        return Promise.reject(refreshError)
      }
    }
    
    // 기타 에러 로깅
    console.error(`❌ API Error: ${error.response?.status} ${error.config?.url}`, error.response?.data)
    
    return Promise.reject(error)
  }
)

// API 응답 타입 정의
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  errors?: string[]
}

// 로그인 요청 타입
export interface LoginRequest {
  user_id: string
  password: string
}

// 로그인 응답 타입
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user_info: {
    user_id: string
    orgnzt_id?: string
    user_nm?: string
    email_adres?: string
    group_id?: string
    emplyr_sttus_code?: string
  }
}

// 사용자 정보 타입
export interface UserInfo {
  user_id: string
  orgnzt_id?: string
  user_nm?: string
  email_adres?: string
  group_id?: string
  emplyr_sttus_code?: string
}

// 메뉴 트리 노드 타입
export interface MenuTreeNode {
  id: number
  name: string
  url?: string
  icon?: string
  description?: string
  sort_order: number
  depth: number
  parent_id?: number
  use_at: string
  permission_code?: string
  created_at: string
  updated_at?: string
  children?: MenuTreeNode[]
}

// 메뉴 아이템 타입 (기존 호환성 유지)
export interface MenuItem {
  id: number
  name: string
  url?: string
  icon?: string
  children?: MenuItem[]
}

// 토큰 갱신 응답 타입
export interface RefreshTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// 인증 관련 API
export const authApi = {
  /**
   * 사용자 로그인
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await apiClient.post<LoginResponse>('/auth/login', credentials)
    return response.data
  },

  /**
   * 액세스 토큰 갱신
   */
  async refreshToken(refreshToken: string): Promise<RefreshTokenResponse> {
    const response = await apiClient.post<RefreshTokenResponse>('/auth/refresh', {
      refresh_token: refreshToken
    })
    return response.data
  },

  /**
   * 사용자 로그아웃
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout')
  },

  /**
   * 현재 사용자 정보 조회
   */
  async getCurrentUser(): Promise<UserInfo> {
    const response = await apiClient.get<UserInfo>('/auth/me')
    return response.data
  },

  /**
   * 비밀번호 변경
   */
  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await apiClient.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  }
}

// 사용자 관리 API
export const userApi = {
  /**
   * 사용자 목록 조회
   */
  async getUsers(page: number = 1, limit: number = 20): Promise<ApiResponse<UserInfo[]>> {
    const response = await apiClient.get<ApiResponse<UserInfo[]>>('/admin/users', {
      params: { page, limit }
    })
    return response.data
  },

  /**
   * 사용자 상세 조회
   */
  async getUser(userId: number): Promise<UserInfo> {
    const response = await apiClient.get<UserInfo>(`/admin/users/${userId}`)
    return response.data
  },

  /**
   * 사용자 생성
   */
  async createUser(userData: Partial<UserInfo>): Promise<UserInfo> {
    const response = await apiClient.post<UserInfo>('/admin/users', userData)
    return response.data
  },

  /**
   * 사용자 수정
   */
  async updateUser(userId: number, userData: Partial<UserInfo>): Promise<UserInfo> {
    const response = await apiClient.put<UserInfo>(`/admin/users/${userId}`, userData)
    return response.data
  },

  /**
   * 사용자 삭제
   */
  async deleteUser(userId: number): Promise<void> {
    await apiClient.delete(`/admin/users/${userId}`)
  }
}

// 메뉴 관련 타입 정의
export interface MenuItem {
  menu_no: number
  menu_nm: string
  progrm_file_nm?: string
  upper_menu_no?: number
  menu_level: number
  sort_ordr: number
  use_at: string
  menu_dc?: string
  relate_image_path?: string
  relate_image_nm?: string
  children?: MenuItem[]
}

// 메뉴 관리 API
export const menuApi = {
  /**
   * 메뉴 목록 조회
   */
  async getMenus(): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get<ApiResponse<any[]>>('/admin/menus')
    return response.data
  },

  /**
   * 메뉴 트리 조회 (동적 메뉴용)
   */
  async getMenuTree(useAt: string = 'Y'): Promise<MenuTreeNode[]> {
    try {
      console.log('🔄 메뉴 트리 API 호출:', `/menus/tree/public?use_at=${useAt}`)
      const response = await apiClient.get(`/menus/tree/public?use_at=${useAt}`)
      
      console.log('📡 메뉴 트리 응답:', response)
      
      // 응답 데이터 검증
      if (!response.data) {
        console.warn('⚠️ 응답 데이터가 없습니다')
        return []
      }
      
      // 백엔드에서 ApiResponse 형태로 반환하는 경우
      if (response.data.success !== undefined) {
        if (response.data.success && Array.isArray(response.data.data)) {
          console.log('✅ 메뉴 트리 로딩 성공:', response.data.data.length, '개 메뉴')
          return response.data.data
        } else {
          console.error('❌ API 응답 실패:', response.data.message)
          throw new Error(response.data.message || '메뉴 트리 조회에 실패했습니다')
        }
      }
      
      // 직접 배열로 반환하는 경우
      if (Array.isArray(response.data)) {
        console.log('✅ 메뉴 트리 로딩 성공:', response.data.length, '개 메뉴')
        return response.data
      }
      
      console.warn('⚠️ 예상하지 못한 응답 형태:', typeof response.data)
      return []
      
    } catch (error: any) {
      console.error('❌ 메뉴 트리 API 호출 실패:', error)
      
      // 네트워크 오류
      if (error.code === 'NETWORK_ERROR' || !error.response) {
        throw new Error('네트워크 연결을 확인해주세요')
      }
      
      // HTTP 오류
      if (error.response) {
        const status = error.response.status
        const message = error.response.data?.message || error.message
        
        switch (status) {
          case 401:
            throw new Error('인증이 필요합니다')
          case 403:
            throw new Error('메뉴 조회 권한이 없습니다')
          case 404:
            throw new Error('메뉴 API를 찾을 수 없습니다')
          case 500:
            throw new Error('서버 오류가 발생했습니다')
          default:
            throw new Error(message || `HTTP ${status} 오류가 발생했습니다`)
        }
      }
      
      throw error
    }
  },

  /**
   * 사용자별 메뉴 권한 조회
   */
  async getUserMenus(): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get<ApiResponse<any[]>>('/admin/menus/user')
    return response.data
  }
}

// 공통코드 API
export const codeApi = {
  /**
   * 공통코드 목록 조회
   */
  async getCodes(groupCode?: string): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get<ApiResponse<any[]>>('/admin/codes', {
      params: groupCode ? { group_code: groupCode } : {}
    })
    return response.data
  }
}

// 게시판 API
export const boardApi = {
  /**
   * 게시판 목록 조회
   */
  async getBoards(): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get<ApiResponse<any[]>>('/admin/boards')
    return response.data
  },

  /**
   * 게시글 목록 조회
   */
  async getPosts(boardId: number, page: number = 1, limit: number = 20): Promise<ApiResponse<any[]>> {
    const response = await apiClient.get<ApiResponse<any[]>>(`/admin/boards/${boardId}/posts`, {
      params: { page, limit }
    })
    return response.data
  }
}

// 파일 업로드 API
export const fileApi = {
  /**
   * 파일 업로드
   */
  async uploadFile(file: File, category: string = 'general'): Promise<ApiResponse<{ url: string; filename: string }>> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('category', category)
    
    const response = await apiClient.post<ApiResponse<{ url: string; filename: string }>>('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    return response.data
  }
}

// 대시보드 관련 타입 정의
export interface DashboardStats {
  total_users: number
  active_sessions: number
  today_visitors: number
  system_status: string
}

export interface DashboardActivity {
  id: number
  text: string
  time: string
  icon: string
  color: string
}

export interface DashboardSummary {
  stats: DashboardStats
  recent_activities: DashboardActivity[]
  system_health: {
    status: string
    uptime: string
    memory_usage: number
    cpu_usage: number
  }
}

// 대시보드 API
export const dashboardApi = {
  /**
   * 대시보드 요약 정보 조회
   */
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await apiClient.get<DashboardSummary>('/system/dashboard')
    return response.data
  },

  /**
   * 시스템 상태 확인
   */
  async getSystemHealth(): Promise<any> {
    const response = await apiClient.get('/system/health')
    return response.data
  }
}

// 기본 API 클라이언트 내보내기
export default apiClient

// 유틸리티 함수들
export const apiUtils = {
  /**
   * API 에러 메시지 추출
   */
  getErrorMessage(error: any): string {
    if (error.response?.data?.message) {
      return error.response.data.message
    }
    if (error.response?.data?.errors?.length > 0) {
      return error.response.data.errors[0]
    }
    if (error.message) {
      return error.message
    }
    return '알 수 없는 오류가 발생했습니다.'
  },

  /**
   * 성공 응답 여부 확인
   */
  isSuccessResponse(response: any): boolean {
    return response?.success === true || (response?.status >= 200 && response?.status < 300)
  },

  /**
   * 페이지네이션 정보 추출
   */
  getPaginationInfo(response: any) {
    return {
      currentPage: response?.current_page || 1,
      totalPages: response?.total_pages || 1,
      totalItems: response?.total_items || 0,
      itemsPerPage: response?.items_per_page || 20
    }
  }
}
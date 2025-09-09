import axios, { type AxiosResponse, type AxiosError } from 'axios'
import { useAuthStore } from '../stores/auth'
import router from '../router'

// API 기본 설정
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    const token = authStore.accessToken
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error: AxiosError) => {
    const authStore = useAuthStore()
    const originalRequest = error.config as any
    
    // 401 에러이고 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // 토큰 갱신 시도
        await authStore.refreshToken
        
        // 새로운 토큰으로 원래 요청 재시도
        const newToken = authStore.accessToken
        if (newToken && originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`
        }
        
        return api(originalRequest)
      } catch (refreshError) {
        // 토큰 갱신 실패 시 로그아웃
        authStore.logout()
        router.push('/login')
        return Promise.reject(refreshError)
      }
    }
    
    // 403 에러 시 권한 없음 페이지로 이동
    if (error.response?.status === 403) {
      router.push('/403')
    }
    
    return Promise.reject(error)
  }
)

export default api

// API 응답 타입
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  errors?: Record<string, string[]>
}

// 페이지네이션 응답 타입
export interface PaginatedResponse<T = any> {
  success: boolean
  data: {
    items: T[]
    total: number
    page: number
    size: number
    pages: number
  }
  message?: string
}

// API 에러 타입
export interface ApiError {
  message: string
  errors?: Record<string, string[]>
  status?: number
}

// 공통 API 함수들
export const apiUtils = {
  // GET 요청
  async get<T = any>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await api.get(url, { params })
    return response.data
  },
  
  // POST 요청
  async post<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await api.post(url, data)
    return response.data
  },
  
  // PUT 요청
  async put<T = any>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await api.put(url, data)
    return response.data
  },
  
  // DELETE 요청
  async delete<T = any>(url: string): Promise<ApiResponse<T>> {
    const response = await api.delete(url)
    return response.data
  },
  
  // 파일 업로드
  async upload<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
    
    return response.data
  },
  
  // 에러 처리 헬퍼
  handleError(error: any): ApiError {
    if (error.response?.data) {
      return {
        message: error.response.data.message || '서버 오류가 발생했습니다.',
        errors: error.response.data.errors,
        status: error.response.status,
      }
    }
    
    return {
      message: error.message || '네트워크 오류가 발생했습니다.',
    }
  },
}
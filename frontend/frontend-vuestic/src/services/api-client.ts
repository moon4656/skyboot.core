import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useToast } from 'vuestic-ui'

// API 클라이언트 인스턴스 생성
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터 - 토큰 자동 추가
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터 - 토큰 갱신 및 에러 처리
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const { init } = useToast()
    const originalRequest = error.config

    // 401 에러 처리 (토큰 만료)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token } = response.data
          localStorage.setItem('access_token', access_token)
          
          // 원래 요청 재시도
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return apiClient(originalRequest)
        } catch (refreshError) {
          // 리프레시 토큰도 만료된 경우 로그아웃
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          
          init({ message: '세션이 만료되었습니다. 다시 로그인해주세요.', color: 'danger' })
          window.location.href = '/auth/login'
          return Promise.reject(refreshError)
        }
      } else {
        // 리프레시 토큰이 없는 경우 로그인 페이지로 이동
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/auth/login'
      }
    }

    // 기타 에러 처리
    if (error.response?.status === 403) {
      init({ message: '접근 권한이 없습니다.', color: 'danger' })
    } else if (error.response?.status === 404) {
      init({ message: '요청한 리소스를 찾을 수 없습니다.', color: 'warning' })
    } else if (error.response?.status >= 500) {
      init({ message: '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', color: 'danger' })
    } else if (error.message === 'Network Error') {
      init({ message: '네트워크 연결을 확인해주세요.', color: 'danger' })
    }

    return Promise.reject(error)
  }
)

export default apiClient
export { apiClient }

// API 엔드포인트 정의
export const apiEndpoints = {
  // 인증 관련
  auth: {
    login: '/v1/auth/login',
    logout: '/v1/auth/logout',
    refresh: '/v1/auth/refresh',
    me: '/v1/auth/me',
  },
  // 메뉴 관련
  // 메뉴 관련 (v1)
   menu: {
     list: '/v1/menu',
     userMenu: '/v1/menu/user',
-  }
+  },
   // 사용자 관련
  users: {
    list: '/users',
    detail: (id: string) => `/users/${id}`,
    create: '/users',
    update: (id: string) => `/users/${id}`,
    delete: (id: string) => `/users/${id}`,
  },
  // 프로젝트 관련
  projects: {
    list: '/projects',
    detail: (id: string) => `/projects/${id}`,
    create: '/projects',
    update: (id: string) => `/projects/${id}`,
    delete: (id: string) => `/projects/${id}`,
  },
}

// 공통 API 요청 함수들
export const apiRequest = {
  get: <T = any>(url: string, config?: any): Promise<T> => 
    apiClient.get(url, config).then(response => response.data),
    
  post: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.post(url, data, config).then(response => response.data),
    
  put: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.put(url, data, config).then(response => response.data),
    
  patch: <T = any>(url: string, data?: any, config?: any): Promise<T> => 
    apiClient.patch(url, data, config).then(response => response.data),
    
  delete: <T = any>(url: string, config?: any): Promise<T> => 
    apiClient.delete(url, config).then(response => response.data),
}
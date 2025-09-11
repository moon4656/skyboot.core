import { defineStore } from 'pinia'
import { apiRequest, apiEndpoints } from '../services/api-client'
import { useToast } from 'vuestic-ui'

// 사용자 인터페이스
export interface User {
  id: number
  username: string
  email: string
  role: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// 로그인 요청 인터페이스
export interface LoginRequest {
  user_id: string
  password: string
}

// 로그인 응답 인터페이스
export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

// 인증 스토어 상태 인터페이스
interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    accessToken: localStorage.getItem('access_token'),
    refreshToken: localStorage.getItem('refresh_token'),
    isAuthenticated: false,
    isLoading: false,
  }),

  getters: {
    /**
     * 현재 사용자 정보 반환
     */
    currentUser: (state): User | null => state.user,

    /**
     * 인증 상태 확인
     */
    isLoggedIn: (state): boolean => state.isAuthenticated && !!state.accessToken,

    /**
     * 사용자 권한 확인
     */
    userRole: (state): string | null => state.user?.role || null,

    /**
     * 관리자 권한 확인
     */
    isAdmin: (state): boolean => state.user?.role === 'admin',

    /**
     * 로딩 상태 확인
     */
    loading: (state): boolean => state.isLoading,
  },

  actions: {
    /**
     * 로그인 처리
     */
    async login(credentials: LoginRequest): Promise<boolean> {
      const { init } = useToast()
      this.isLoading = true

      try {
        const response: LoginResponse = await apiRequest.post(
          apiEndpoints.auth.login,
          credentials
        )

        // 토큰 저장
        this.accessToken = response.access_token
        this.refreshToken = response.refresh_token
        this.user = response.user
        this.isAuthenticated = true

        // 로컬 스토리지에 저장
        localStorage.setItem('access_token', response.access_token)
        localStorage.setItem('refresh_token', response.refresh_token)
        localStorage.setItem('user', JSON.stringify(response.user))

        init({ message: '로그인에 성공했습니다.', color: 'success' })
        return true
      } catch (error: any) {
        console.error('로그인 실패:', error)
        
        let errorMessage = '로그인에 실패했습니다.'
        if (error.response?.status === 401) {
          errorMessage = '이메일 또는 비밀번호가 올바르지 않습니다.'
        } else if (error.response?.status === 422) {
          errorMessage = '입력 정보를 확인해주세요.'
        }
        
        init({ message: errorMessage, color: 'danger' })
        return false
      } finally {
        this.isLoading = false
      }
    },

    /**
     * 로그아웃 처리
     */
    async logout(): Promise<void> {
      const { init } = useToast()
      this.isLoading = true

      try {
        // 서버에 로그아웃 요청
        await apiRequest.post(apiEndpoints.auth.logout)
      } catch (error) {
        console.error('로그아웃 API 호출 실패:', error)
      } finally {
        // 로컬 상태 및 스토리지 정리
        this.clearAuthData()
        init({ message: '로그아웃되었습니다.', color: 'info' })
        this.isLoading = false
      }
    },

    /**
     * 토큰 갱신
     */
    async refreshAccessToken(): Promise<boolean> {
      if (!this.refreshToken) {
        return false
      }

      try {
        const response = await apiRequest.post(apiEndpoints.auth.refresh, {
          refresh_token: this.refreshToken,
        })

        this.accessToken = response.access_token
        localStorage.setItem('access_token', response.access_token)
        
        return true
      } catch (error) {
        console.error('토큰 갱신 실패:', error)
        this.clearAuthData()
        return false
      }
    },

    /**
     * 현재 사용자 정보 조회
     */
    async fetchCurrentUser(): Promise<void> {
      if (!this.accessToken) {
        return
      }

      try {
        const user: User = await apiRequest.get(apiEndpoints.auth.me)
        this.user = user
        this.isAuthenticated = true
        localStorage.setItem('user', JSON.stringify(user))
      } catch (error) {
        console.error('사용자 정보 조회 실패:', error)
        this.clearAuthData()
      }
    },

    /**
     * 인증 상태 초기화 (앱 시작 시 호출)
     */
    async initializeAuth(): Promise<void> {
      const storedUser = localStorage.getItem('user')
      const storedToken = localStorage.getItem('access_token')
      
      if (storedUser && storedToken) {
        try {
          this.user = JSON.parse(storedUser)
          this.accessToken = storedToken
          this.refreshToken = localStorage.getItem('refresh_token')
          
          // 토큰 유효성 확인을 위해 사용자 정보 재조회
          await this.fetchCurrentUser()
        } catch (error) {
          console.error('인증 초기화 실패:', error)
          this.clearAuthData()
        }
      }
    },

    /**
     * 인증 데이터 정리
     */
    clearAuthData(): void {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      this.isAuthenticated = false
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    },

    /**
     * 권한 확인
     */
    hasPermission(requiredRole: string): boolean {
      if (!this.user) {
        return false
      }
      
      // 관리자는 모든 권한 보유
      if (this.user.role === 'admin') {
        return true
      }
      
      return this.user.role === requiredRole
    },

    /**
     * 사용자 정보 업데이트
     */
    updateUser(userData: Partial<User>): void {
      if (this.user) {
        this.user = { ...this.user, ...userData }
        localStorage.setItem('user', JSON.stringify(this.user))
      }
    },
  },
})
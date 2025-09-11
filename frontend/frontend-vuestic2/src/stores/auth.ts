import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { jwtDecode } from 'jwt-decode'
import { authApi, type LoginRequest, type LoginResponse, type UserInfo } from '@/services/api'

// JWT 토큰 페이로드 타입 정의
interface JwtPayload {
  sub: string
  exp: number
  iat: number
  user_id: number
  email: string
  roles: string[]
  permissions?: string[] // 사용자 권한
}

// 권한 인터페이스
interface Permission {
  id: string
  name: string
  code: string
  description?: string
}

// 역할 인터페이스
interface Role {
  id: string
  name: string
  code: string
  permissions: Permission[]
  description?: string
}

// 로컬 스토리지 키 상수
const ACCESS_TOKEN_KEY = import.meta.env.VITE_TOKEN_STORAGE_KEY || 'skyboot_access_token'
const REFRESH_TOKEN_KEY = import.meta.env.VITE_REFRESH_TOKEN_STORAGE_KEY || 'skyboot_refresh_token'
const USER_INFO_KEY = 'skyboot_user_info'

export const useAuthStore = defineStore('auth', () => {
  // 상태 관리
  const accessToken = ref<string | null>(null)
  const refreshToken = ref<string | null>(null)
  const user = ref<UserInfo | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const userPermissions = ref<Permission[]>([])
  const userRoles = ref<Role[]>([])

  // 초기화 함수
  const initializeFromStorage = () => {
    accessToken.value = localStorage.getItem(ACCESS_TOKEN_KEY)
    refreshToken.value = localStorage.getItem(REFRESH_TOKEN_KEY)
    const storedUser = localStorage.getItem(USER_INFO_KEY)
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('Failed to parse stored user info:', e)
        localStorage.removeItem(USER_INFO_KEY)
      }
    }
  }

  // 스토어 초기화
  initializeFromStorage()

  // 계산된 속성
  const isAuthenticated = computed(() => {
    if (!accessToken.value) return false
    
    try {
      const decoded = jwtDecode<JwtPayload>(accessToken.value)
      return decoded.exp * 1000 > Date.now()
    } catch {
      return false
    }
  })

  const currentUser = computed(() => user.value)

  // 특정 권한 보유 여부 확인
  const hasPermission = (permissionCode: string): boolean => {
    return userPermissions.value.some(p => p.code === permissionCode)
  }

  // 특정 역할 보유 여부 확인
  const hasRole = (roleCode: string): boolean => {
    return userRoles.value.some(r => r.code === roleCode)
  }

  // 여러 권한 중 하나라도 보유 여부 확인
  const hasAnyPermission = (permissionCodes: string[]): boolean => {
    return permissionCodes.some(code => hasPermission(code))
  }

  // 여러 역할 중 하나라도 보유 여부 확인
  const hasAnyRole = (roleCodes: string[]): boolean => {
    return roleCodes.some(code => hasRole(code))
  }

  // 토큰 저장 함수
  const setTokens = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
  }

  // 토큰 제거 함수
  const clearTokens = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    userPermissions.value = []
    userRoles.value = []
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_INFO_KEY)
  }

  // 사용자 정보 설정
  const setUser = (userData: UserInfo) => {
    user.value = userData
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userData))
  }

  // 로그인 함수
  const login = async (credentials: LoginRequest): Promise<boolean> => {
    try {
      isLoading.value = true
      error.value = null

      console.log('🚀 로그인 시도:', credentials.user_id)
      
      const response = await authApi.login(credentials)
      const { access_token, refresh_token, user_info: userData } = response

      setTokens(access_token, refresh_token)
      setUser(userData)

      console.log('✅ 로그인 성공:', userData.user_id)
      return true
    } catch (err: any) {
      console.error('❌ 로그인 실패:', err)
      error.value = err.response?.data?.message || '로그인에 실패했습니다.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 로그아웃 함수
  const logout = async () => {
    try {
      console.log('🚀 로그아웃 시도')
      
      if (refreshToken.value) {
        await authApi.logout()
      }
      
      console.log('✅ 로그아웃 완료')
    } catch (err) {
      console.error('❌ 로그아웃 요청 실패:', err)
    } finally {
      clearTokens()
    }
  }

  // 토큰 갱신 함수
  const refreshAccessToken = async (): Promise<boolean> => {
    try {
      if (!refreshToken.value) {
        throw new Error('리프레시 토큰이 없습니다.')
      }

      console.log('🚀 토큰 갱신 시도')
      
      const response = await authApi.refreshToken(refreshToken.value)
      const { access_token } = response
      
      // 새로운 액세스 토큰만 업데이트 (리프레시 토큰은 유지)
      accessToken.value = access_token
      localStorage.setItem(ACCESS_TOKEN_KEY, access_token)

      console.log('✅ 토큰 갱신 성공')
      return true
    } catch (err) {
      console.error('❌ 토큰 갱신 실패:', err)
      clearTokens()
      return false
    }
  }

  // 현재 사용자 정보 새로고침
  const refreshUserInfo = async (): Promise<boolean> => {
    try {
      if (!isAuthenticated.value) {
        return false
      }

      console.log('🚀 사용자 정보 새로고침')
      
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      
      // 사용자 권한 및 역할 정보 로드
      await loadUserPermissions()
      
      console.log('✅ 사용자 정보 새로고침 완료')
      return true
    } catch (err) {
      console.error('❌ 사용자 정보 새로고침 실패:', err)
      return false
    }
  }

  // 사용자 권한 정보 로드
  const loadUserPermissions = async (): Promise<void> => {
    if (!user.value) return
    
    try {
      // TODO: 실제 API 연동 시 주석 해제
      // const permissionsResponse = await authApi.getUserPermissions(user.value.id)
      // const rolesResponse = await authApi.getUserRoles(user.value.id)
      // userPermissions.value = permissionsResponse.data
      // userRoles.value = rolesResponse.data
      
      // 임시 데모 데이터
      userPermissions.value = [
        { id: '1', name: '대시보드 조회', code: 'dashboard.view' },
        { id: '2', name: '사용자 조회', code: 'user.view' },
        { id: '3', name: '사용자 관리', code: 'user.manage' },
        { id: '4', name: '메뉴 조회', code: 'menu.view' },
        { id: '5', name: '메뉴 관리', code: 'menu.manage' }
      ]
      
      userRoles.value = [
        {
          id: '1',
          name: '관리자',
          code: 'admin',
          permissions: userPermissions.value,
          description: '시스템 관리자 권한'
        }
      ]
      
      console.log('✅ 사용자 권한 정보 로드 완료', { 
        permissionCount: userPermissions.value.length,
        roleCount: userRoles.value.length
      })
    } catch (err: any) {
      console.error('❌ 사용자 권한 정보 로드 실패:', err)
    }
  }

  // 비밀번호 변경
  const changePassword = async (oldPassword: string, newPassword: string): Promise<boolean> => {
    try {
      isLoading.value = true
      error.value = null

      console.log('🚀 비밀번호 변경 시도')
      
      await authApi.changePassword(oldPassword, newPassword)
      
      console.log('✅ 비밀번호 변경 완료')
      return true
    } catch (err: any) {
      console.error('❌ 비밀번호 변경 실패:', err)
      error.value = err.response?.data?.message || '비밀번호 변경에 실패했습니다.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  // 사용자 정보 로드
  const loadUserFromStorage = () => {
    const storedUser = localStorage.getItem(USER_INFO_KEY)
    if (storedUser) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (err) {
        console.error('❌ 사용자 정보 파싱 실패:', err)
        localStorage.removeItem(USER_INFO_KEY)
      }
    }
  }

  // 토큰 유효성 검사
  const validateToken = (): boolean => {
    if (!accessToken.value) return false
    
    try {
      const decoded = jwtDecode<JwtPayload>(accessToken.value)
      const isValid = decoded.exp * 1000 > Date.now()
      
      if (!isValid) {
        console.warn('⚠️ 토큰이 만료되었습니다.')
        clearTokens()
      }
      
      return isValid
    } catch (err) {
      console.error('❌ 토큰 검증 실패:', err)
      clearTokens()
      return false
    }
  }

  // 초기화 - 앱 시작 시 토큰 유효성 검사
  const initialize = async () => {
    loadUserFromStorage()
    
    if (accessToken.value) {
      if (isAuthenticated.value) {
        await refreshUserInfo()
      } else {
        // 액세스 토큰이 만료된 경우 리프레시 시도
        const refreshed = await refreshAccessToken()
        if (refreshed) {
          await refreshUserInfo()
        }
      }
    }
  }

  return {
    // 상태
    accessToken: readonly(accessToken),
    refreshToken: readonly(refreshToken),
    user: readonly(user),
    isLoading: readonly(isLoading),
    error: readonly(error),
    userPermissions: readonly(userPermissions),
    userRoles: readonly(userRoles),
    
    // 계산된 속성
    isAuthenticated,
    currentUser,
    
    // 메서드
    login,
    logout,
    refreshAccessToken,
    refreshUserInfo,
    loadUserPermissions,
    changePassword,
    setUser,
    clearTokens,
    validateToken,
    initialize,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAnyRole
  }
})
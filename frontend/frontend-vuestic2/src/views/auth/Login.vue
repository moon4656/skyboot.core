<template>
  <div class="login-form">
    <!-- 로그인 헤더 -->
    <div class="login-header">
      <h2 class="login-title">로그인</h2>
      <p class="login-subtitle">계정에 로그인하여 관리자 시스템을 이용하세요</p>
    </div>

    <!-- 로그인 폼 -->
    <va-form ref="loginForm" @submit.prevent="handleLogin">
      <div class="form-group">
        <va-input
          v-model="credentials.user_id"
          label="사용자명"
          placeholder="사용자명을 입력하세요"
          :rules="usernameRules"
          :loading="authStore.loading"
          class="login-input"
        >
          <template #prependInner>
            <va-icon name="person" color="primary" />
          </template>
        </va-input>
      </div>

      <div class="form-group">
        <va-input
          v-model="credentials.password"
          type="password"
          label="비밀번호"
          placeholder="비밀번호를 입력하세요"
          :rules="passwordRules"
          :loading="authStore.loading"
          class="login-input"
          @keyup.enter="handleLogin"
        >
          <template #prependInner>
            <va-icon name="lock" color="primary" />
          </template>
        </va-input>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="authStore.error" class="error-message">
        <va-alert
          color="danger"
          icon="warning"
          :model-value="true"
          closeable
          @input="clearError"
        >
          {{ authStore.error }}
        </va-alert>
      </div>

      <!-- 로그인 옵션 -->
      <div class="login-options">
        <va-checkbox
          v-model="rememberMe"
          label="로그인 상태 유지"
          class="remember-checkbox"
        />

        <va-button
          preset="plain"
          size="small"
          @click="handleForgotPassword"
          class="forgot-password"
        >
          비밀번호를 잊으셨나요?
        </va-button>
      </div>

      <!-- 로그인 버튼 -->
      <div class="login-actions">
        <va-button
          type="submit"
          :loading="authStore.loading"
          :disabled="!isFormValid"
          size="large"
          class="login-button"
          block
        >
          <va-icon name="login" class="mr-2" />
          로그인
        </va-button>
      </div>
    </va-form>

    <!-- 추가 링크 -->
    <div class="login-footer">
      <p class="text-sm text-gray-600">
        계정이 없으신가요?
        <va-button
          preset="plain"
          size="small"
          @click="handleSignup"
          class="signup-link"
        >
          회원가입
        </va-button>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 폼 데이터
const credentials = ref({
  user_id: '',
  password: ''
})

const rememberMe = ref(false)
const loginForm = ref()

// 유효성 검사 규칙
const usernameRules = [
  (value: string) => !!value || '사용자명을 입력해주세요',
  (value: string) => value.length >= 3 || '사용자명은 3자 이상이어야 합니다'
]

const passwordRules = [
  (value: string) => !!value || '비밀번호를 입력해주세요',
  (value: string) => value.length >= 4 || '비밀번호는 4자 이상이어야 합니다'
]

// 폼 유효성 검사
const isFormValid = computed(() => {
  return credentials.value.user_id.length >= 3 &&
         credentials.value.password.length >= 4
})

// 메서드
const handleLogin = async () => {
  if (!isFormValid.value) return

  const success = await authStore.login(credentials.value)

  if (success) {
    // 로그인 성공 시 리다이렉트 처리
    const redirectPath = router.currentRoute.value.query.redirect as string
    const targetPath = redirectPath || '/admin'
    
    console.log('✅ 로그인 성공 - 리다이렉트:', targetPath)
    await router.push(targetPath)
  }
}

const clearError = () => {
  authStore.error = null
}

const handleForgotPassword = () => {
  // 비밀번호 찾기 페이지로 이동 (미구현)
  router.push({ name: 'ComingSoon' })
}

const handleSignup = () => {
  // 회원가입 페이지로 이동 (미구현)
  router.push({ name: 'ComingSoon' })
}

// 라이프사이클
onMounted(() => {
  // 개발 환경에서 기본값 설정 (실제 운영에서는 제거)
  if (import.meta.env.DEV) {
    credentials.value.user_id = 'user01'
    credentials.value.password = 'test'
  }
})
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 1.5rem;
}

.login-input {
  transition: all 0.3s ease;
}

.login-input:focus-within {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(44, 62, 80, 0.15);
}

.error-message {
  margin-bottom: 1.5rem;
  animation: shake 0.5s ease-in-out;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.remember-checkbox {
  font-size: 0.9rem;
}

.forgot-password {
  color: #2c3e50;
  font-size: 0.9rem;
  text-decoration: none;
  transition: color 0.3s ease;
}

.forgot-password:hover {
  color: #34495e;
  text-decoration: underline;
}

.login-actions {
  margin-bottom: 2rem;
}

.login-button {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  border: none;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 25px rgba(44, 62, 80, 0.3);
}

.login-button:active {
  transform: translateY(0);
}

.login-footer {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.signup-link {
  color: #2c3e50;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.3s ease;
}

.signup-link:hover {
  color: #34495e;
  text-decoration: underline;
}

/* 애니메이션 */
@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-5px);
  }
  75% {
    transform: translateX(5px);
  }
}

/* 로딩 상태 스타일 */
.login-form :deep(.va-input--loading) {
  opacity: 0.7;
}

/* 포커스 상태 개선 */
.login-form :deep(.va-input__container) {
  transition: all 0.3s ease;
}

.login-form :deep(.va-input--focused .va-input__container) {
  border-color: #2c3e50;
  box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.2);
}

/* 반응형 디자인 */
@media (max-width: 480px) {
  .login-form {
    padding: 0 1rem;
  }

  .login-title {
    font-size: 1.5rem;
  }

  .login-options {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}
</style>

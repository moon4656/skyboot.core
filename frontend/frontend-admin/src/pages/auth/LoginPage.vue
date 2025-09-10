<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">SkyBoot Admin</h1>
        <p class="login-subtitle">관리자 시스템에 로그인하세요</p>
      </div>

      <va-form ref="formRef" class="login-form" @submit.prevent="handleLogin">
        <va-input
          v-model="loginForm.username"
          label="사용자명"
          placeholder="사용자명을 입력하세요"
          :rules="[required]"
          class="mb-4"
        >
          <template #prepend>
            <va-icon name="person" />
          </template>
        </va-input>

        <va-input
          v-model="loginForm.password"
          type="password"
          label="비밀번호"
          placeholder="비밀번호를 입력하세요"
          :rules="[required]"
          class="mb-4"
          @keyup.enter="handleLogin"
        >
          <template #prepend>
            <va-icon name="lock" />
          </template>
        </va-input>

        <div class="login-options mb-4">
          <va-checkbox v-model="loginForm.rememberMe" label="로그인 상태 유지" />
        </div>

        <va-button
          :loading="isLoading"
          :disabled="!isFormValid"
          class="login-button"
          @click="handleLogin"
        >
          로그인
        </va-button>
      </va-form>

      <div class="login-footer">
        <p class="text-sm text-gray-500">
          © 2024 SkyBoot Core. All rights reserved.
        </p>
      </div>
    </div>

    <!-- 다크모드 토글 -->
    <va-button
      preset="secondary"
      icon="dark_mode"
      class="theme-toggle"
      @click="toggleTheme"
    >
      {{ isDark ? '라이트 모드' : '다크 모드' }}
    </va-button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { useThemeStore } from '../../stores/theme'
import { useToast } from 'vuestic-ui'

interface LoginForm {
  username: string
  password: string
  rememberMe: boolean
}

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const themeStore = useThemeStore()
const { init } = useToast()

const formRef = ref()
const isLoading = ref(false)

const loginForm = ref<LoginForm>({
  username: '',
  password: '',
  rememberMe: false
})

// 폼 유효성 검사
const required = (value: string) => !!value || '필수 입력 항목입니다'

const isFormValid = computed(() => {
  return loginForm.value.username && loginForm.value.password
})

const isDark = computed(() => themeStore.isDark)

// 로그인 처리
const handleLogin = async () => {
  if (!formRef.value?.validate()) {
    return
  }

  isLoading.value = true

  try {
    await authStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password,
      rememberMe: loginForm.value.rememberMe
    })

    init({
      message: '로그인에 성공했습니다.',
      color: 'success'
    })

    const redirectPath = (route.query.redirect as string) || '/'
    console.log('Attempting redirect to:', redirectPath)
    await router.push(redirectPath)
    console.log('Redirect completed')
  } catch (error: any) {
    init({
      message: error.message || '로그인에 실패했습니다.',
      color: 'danger'
    })
  } finally {
    isLoading.value = false
  }
}

// 테마 토글
const toggleTheme = () => {
  themeStore.toggleTheme()
}

// 컴포넌트 마운트 시 이미 로그인된 사용자 체크
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  position: relative;
}

.login-card {
  background: var(--va-background-primary);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  font-size: 2rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.login-subtitle {
  color: #6b7280;
  font-size: 0.875rem;
}

.login-form {
  margin-bottom: 1.5rem;
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-button {
  width: 100%;
  height: 3rem;
  font-weight: 600;
}

.login-footer {
  text-align: center;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}

.theme-toggle {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

/* 다크 모드 스타일 */
.dark .login-card {
  background: #1f2937;
  color: white;
}

.dark .login-title {
  color: var(--va-text-primary);
}

.dark .login-subtitle {
  color: #9ca3af;
}

.dark .login-footer {
  border-top-color: #374151;
}

/* 반응형 디자인 */
@media (max-width: 640px) {
  .login-container {
    padding: 0.5rem;
  }
  
  .login-card {
    padding: 1.5rem;
  }
  
  .login-title {
    font-size: 1.5rem;
  }
}
</style>
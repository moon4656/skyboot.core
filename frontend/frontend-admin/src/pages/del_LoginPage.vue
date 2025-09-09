<template>
  <div class="login-container">
    <div class="login-card">
      <VaCard class="login-form">
        <VaCardContent>
          <!-- 로고 및 제목 -->
          <div class="text-center mb-6">
            <div class="logo mb-4">
              <VaIcon name="admin_panel_settings" size="4rem" color="primary" />
            </div>
            <h1 class="va-h3 mb-2">SkyBoot Admin</h1>
            <p class="va-text-secondary">관리자 시스템에 로그인하세요</p>
          </div>

          <!-- 로그인 폼 -->
          <form @submit.prevent="handleLogin">
            <div class="mb-4">
              <VaInput
                v-model="loginForm.username"
                label="사용자명"
                placeholder="사용자명을 입력하세요"
                :error="!!errors.username"
                :error-messages="errors.username"
                :disabled="isLoading"
                required
              >
                <template #prependInner>
                  <VaIcon name="person" />
                </template>
              </VaInput>
            </div>

            <div class="mb-4">
              <VaInput
                v-model="loginForm.password"
                type="password"
                label="비밀번호"
                placeholder="비밀번호를 입력하세요"
                :error="!!errors.password"
                :error-messages="errors.password"
                :disabled="isLoading"
                required
              >
                <template #prependInner>
                  <VaIcon name="lock" />
                </template>
              </VaInput>
            </div>

            <div class="mb-4">
              <VaCheckbox
                v-model="loginForm.rememberMe"
                label="로그인 상태 유지"
                :disabled="isLoading"
              />
            </div>

            <!-- 에러 메시지 -->
            <VaAlert
              v-if="errorMessage"
              color="danger"
              class="mb-4"
              closeable
              @close="errorMessage = ''"
            >
              {{ errorMessage }}
            </VaAlert>

            <!-- 로그인 버튼 -->
            <VaButton
              type="submit"
              class="w-full mb-4"
              :loading="isLoading"
              :disabled="!isFormValid"
            >
              로그인
            </VaButton>

            <!-- 원클릭 로그인 (개발용) -->
            <VaButton
              v-if="isDevelopment"
              color="secondary"
              preset="secondary"
              class="w-full"
              :loading="isOneClickLoading"
              @click="handleOneClickLogin"
            >
              원클릭 로그인 (개발용)
            </VaButton>
          </form>
        </VaCardContent>
      </VaCard>

      <!-- 푸터 -->
      <div class="login-footer text-center mt-6">
        <p class="va-text-secondary">
          © 2024 SkyBoot Core. All rights reserved.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useToast } from 'vuestic-ui';
import type { LoginRequest } from '../types/auth';

const router = useRouter();
const authStore = useAuthStore();
const { init: notify } = useToast();

// 폼 데이터
const loginForm = ref<LoginRequest & { rememberMe: boolean }>({
  username: '',
  password: '',
  rememberMe: false,
});

// 상태 관리
const isLoading = ref(false);
const isOneClickLoading = ref(false);
const errorMessage = ref('');
const errors = ref<Record<string, string>>({});

// 개발 환경 체크
const isDevelopment = computed(() => {
  return import.meta.env.DEV;
});

// 폼 유효성 검사
const isFormValid = computed(() => {
  return loginForm.value.username.trim() !== '' && 
         loginForm.value.password.trim() !== '';
});

// 폼 검증
const validateForm = (): boolean => {
  errors.value = {};
  
  if (!loginForm.value.username.trim()) {
    errors.value.username = '사용자명을 입력해주세요.';
  }
  
  if (!loginForm.value.password.trim()) {
    errors.value.password = '비밀번호를 입력해주세요.';
  }
  
  if (loginForm.value.password.length < 4) {
    errors.value.password = '비밀번호는 최소 4자 이상이어야 합니다.';
  }
  
  return Object.keys(errors.value).length === 0;
};

// 로그인 처리
const handleLogin = async () => {
  if (!validateForm()) {
    return;
  }
  
  isLoading.value = true;
  errorMessage.value = '';
  
  try {
    await authStore.login({
      username: loginForm.value.username,
      password: loginForm.value.password,
    });
    
    notify({
      message: '로그인에 성공했습니다.',
      color: 'success',
      duration: 3000,
    });
    
    // 로그인 성공 후 메인 대시보드로 이동
    const redirectPath = router.currentRoute.value.query.redirect as string || '/';
    await router.push(redirectPath);
    
  } catch (error: any) {
    console.error('로그인 실패:', error);
    
    if (error.response?.status === 401) {
      errorMessage.value = '사용자명 또는 비밀번호가 올바르지 않습니다.';
    } else if (error.response?.status === 403) {
      errorMessage.value = '계정이 비활성화되었습니다. 관리자에게 문의하세요.';
    } else {
      errorMessage.value = error.message || '로그인 중 오류가 발생했습니다.';
    }
    
    notify({
      message: errorMessage.value,
      color: 'danger',
      duration: 5000,
    });
  } finally {
    isLoading.value = false;
  }
};

// 원클릭 로그인 (개발용)
const handleOneClickLogin = async () => {
  isOneClickLoading.value = true;
  
  try {
    await authStore.oneClickLogin();
    
    notify({
      message: '원클릭 로그인에 성공했습니다.',
      color: 'success',
      duration: 3000,
    });
    
    await router.push('/');
    
  } catch (error: any) {
    console.error('원클릭 로그인 실패:', error);
    
    notify({
      message: error.message || '원클릭 로그인 중 오류가 발생했습니다.',
      color: 'danger',
      duration: 5000,
    });
  } finally {
    isOneClickLoading.value = false;
  }
};

// 컴포넌트 마운트 시
onMounted(() => {
  // 이미 로그인된 경우 메인 화면으로 리다이렉트
  if (authStore.isAuthenticated) {
    router.push('/');
  }
});
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 400px;
}

.login-form {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  justify-content: center;
  align-items: center;
}

.w-full {
  width: 100%;
}

.login-footer {
  color: rgba(255, 255, 255, 0.8);
}

@media (max-width: 480px) {
  .login-container {
    padding: 0.5rem;
  }
  
  .login-card {
    max-width: 100%;
  }
}
</style>
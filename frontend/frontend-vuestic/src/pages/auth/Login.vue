<template>
  <VaForm ref="formRef" @submit.prevent="submit">
    <h1 class="font-semibold text-4xl mb-4">로그인</h1>
    <p class="text-base mb-4 leading-5">
      아직 계정이 없으신가요?
      <RouterLink :to="{ name: 'signup' }" class="font-semibold text-primary">회원가입</RouterLink>
    </p>
    
    <!-- 에러 메시지 표시 -->
    <VaAlert v-if="errorMessage" color="danger" class="mb-4">
      {{ errorMessage }}
    </VaAlert>
    
    <VaInput
      v-model="formData.user_id"
      :rules="[validators.required]"
      :disabled="authStore.loading"
      class="mb-4"
      label="사용자 ID"
      placeholder="사용자 ID를 입력하세요"
    />
    <VaValue v-slot="isPasswordVisible" :default-value="false">
      <VaInput
        v-model="formData.password"
        :rules="[validators.required]"
        :type="isPasswordVisible.value ? 'text' : 'password'"
        :disabled="authStore.loading"
        class="mb-4"
        label="비밀번호"
        placeholder="비밀번호를 입력하세요"
        @clickAppendInner.stop="isPasswordVisible.value = !isPasswordVisible.value"
      >
        <template #appendInner>
          <VaIcon
            :name="isPasswordVisible.value ? 'mso-visibility_off' : 'mso-visibility'"
            class="cursor-pointer"
            color="secondary"
          />
        </template>
      </VaInput>
    </VaValue>

    <div class="auth-layout__options flex flex-col sm:flex-row items-start sm:items-center justify-between">
      <VaCheckbox 
        v-model="formData.keepLoggedIn" 
        class="mb-2 sm:mb-0" 
        label="로그인 상태 유지" 
        :disabled="authStore.loading"
      />
      <RouterLink :to="{ name: 'recover-password' }" class="mt-2 sm:mt-0 sm:ml-1 font-semibold text-primary">
        비밀번호를 잊으셨나요?
      </RouterLink>
    </div>

    <div class="flex justify-center mt-4">
      <VaButton 
        class="w-full" 
        type="submit"
        :loading="authStore.loading"
        :disabled="authStore.loading"
      > 
        {{ authStore.loading ? '로그인 중...' : '로그인' }}
      </VaButton>
    </div>
  </VaForm>
</template>

<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { validators } from '../../services/utils'
import { useAuthStore } from '../../stores/auth-store'
import { useMenuStore } from '../../stores/menu-store'

const formRef = ref()
const router = useRouter()
const authStore = useAuthStore()
const menuStore = useMenuStore()

const errorMessage = ref('')

const formData = reactive({
  user_id: '',
  password: '',
  keepLoggedIn: false,
})

// 로그인 처리
const submit = async () => {
  if (!formRef.value?.validate()) {
    return
  }

  errorMessage.value = ''

  try {
    const success = await authStore.login({
      user_id: formData.user_id,
      password: formData.password,
    })

    if (success) {
      // 메뉴 데이터 로드
      await menuStore.fetchMenuItems()
      
      // 대시보드로 이동
      await router.push({ name: 'dashboard' })
    }
  } catch (error: any) {
    console.error('로그인 처리 중 오류:', error)
    errorMessage.value = error.message || '로그인 처리 중 오류가 발생했습니다.'
  }
}

// 컴포넌트 마운트 시 이미 로그인된 경우 대시보드로 이동
// 라우터 가드에서 처리하므로 제거
// onMounted(async () => {
//   if (authStore.isLoggedIn) {
//     await router.push({ name: 'dashboard' })
//   }
// })
</script>

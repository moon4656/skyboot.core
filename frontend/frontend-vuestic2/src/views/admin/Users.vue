<template>
  <div class="users-page">
    <ComingSoon
      title="사용자 관리"
      description="사용자 계정을 생성, 수정, 삭제하고 권한을 관리할 수 있는 종합적인 사용자 관리 시스템입니다."
      icon="people"
      :features="[
        '사용자 계정 생성 및 관리',
        '사용자 권한 및 역할 설정',
        '사용자 활동 로그 조회',
        '대량 사용자 등록 (Excel/CSV)',
        '사용자 그룹 관리',
        '비밀번호 정책 설정',
        '사용자 프로필 관리',
        '로그인 이력 추적'
      ]"
      :progress="75"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'Users'
})
</script>

<style scoped>
.users-page {
  width: 100%;
  height: 100%;
}
</style>
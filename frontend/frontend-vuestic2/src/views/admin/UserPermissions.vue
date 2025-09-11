<template>
  <div class="user-permissions-page">
    <ComingSoon
      title="사용자권한 관리"
      description="개별 사용자에게 특별한 권한을 부여하거나 제한하는 세밀한 권한 관리 시스템입니다."
      icon="person_pin"
      :features="[
        '개별 사용자 권한 설정',
        '역할 기반 권한 오버라이드',
        '임시 권한 부여',
        '권한 만료일 설정',
        '권한 위임 기능',
        '사용자별 권한 이력',
        '권한 승인 워크플로우',
        '권한 사용 통계'
      ]"
      :progress="70"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'UserPermissions'
})
</script>

<style scoped>
.user-permissions-page {
  width: 100%;
  height: 100%;
}
</style>
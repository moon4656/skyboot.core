<template>
  <div class="menu-permissions-page">
    <ComingSoon
      title="메뉴권한 관리"
      description="사용자 역할별로 메뉴 접근 권한을 세밀하게 설정하고 관리할 수 있는 권한 관리 시스템입니다."
      icon="security"
      :features="[
        '역할별 메뉴 접근 권한 설정',
        '계층형 메뉴 권한 관리',
        '권한 상속 및 재정의',
        '권한 템플릿 관리',
        '권한 변경 이력 추적',
        '대량 권한 설정',
        '권한 충돌 검사',
        '실시간 권한 적용'
      ]"
      :progress="85"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'MenuPermissions'
})
</script>

<style scoped>
.menu-permissions-page {
  width: 100%;
  height: 100%;
}
</style>
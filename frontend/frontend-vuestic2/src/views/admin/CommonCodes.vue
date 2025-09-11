<template>
  <div class="common-codes-page">
    <ComingSoon
      title="공통코드 관리"
      description="시스템 전반에서 사용되는 공통코드를 체계적으로 관리하고 유지보수할 수 있는 코드 관리 시스템입니다."
      icon="code"
      :features="[
        '코드 그룹별 관리',
        '계층형 코드 구조',
        '코드 사용 현황 추적',
        '코드 변경 이력 관리',
        '다국어 코드명 지원',
        '코드 유효성 검증',
        '대량 코드 등록',
        'API 연동 지원'
      ]"
      :progress="55"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'CommonCodes'
})
</script>

<style scoped>
.common-codes-page {
  width: 100%;
  height: 100%;
}
</style>
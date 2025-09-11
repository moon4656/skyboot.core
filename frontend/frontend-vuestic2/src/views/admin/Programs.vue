<template>
  <div class="programs-page">
    <ComingSoon
      title="프로그램 관리"
      description="시스템에서 사용되는 모든 프로그램과 모듈을 관리하고 설정할 수 있는 통합 관리 시스템입니다."
      icon="apps"
      :features="[
        '프로그램 등록 및 관리',
        '모듈별 권한 설정',
        '프로그램 버전 관리',
        'API 엔드포인트 관리',
        '프로그램 의존성 관리',
        '배포 및 롤백 기능',
        '성능 모니터링',
        '로그 및 오류 추적'
      ]"
      :progress="60"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'Programs'
})
</script>

<style scoped>
.programs-page {
  width: 100%;
  height: 100%;
}
</style>
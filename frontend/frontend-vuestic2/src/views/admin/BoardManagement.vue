<template>
  <div class="board-management-page">
    <ComingSoon
      title="게시판관리"
      description="다양한 유형의 게시판을 생성하고 관리하며, 게시글과 댓글을 효율적으로 운영할 수 있는 게시판 관리 시스템입니다."
      icon="forum"
      :features="[
        '게시판 생성 및 설정',
        '게시글 관리 및 모더레이션',
        '댓글 및 답글 관리',
        '파일 첨부 관리',
        '게시판별 권한 설정',
        '공지사항 관리',
        '게시글 통계 및 분석',
        '스팸 필터링'
      ]"
      :progress="65"
      :show-progress="true"
      :show-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
import ComingSoon from '@/components/ComingSoon.vue'

// 페이지 메타 정보 설정
defineOptions({
  name: 'BoardManagement'
})
</script>

<style scoped>
.board-management-page {
  width: 100%;
  height: 100%;
}
</style>
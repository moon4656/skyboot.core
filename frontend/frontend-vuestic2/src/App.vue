<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// SkyBoot Admin 메인 애플리케이션
// Vue 3 + Vite + TypeScript + Vuestic UI 기반
</script>

<style>
/* 전역 스타일 초기화 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  font-family: 'Inter', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #FDFCF8; /* skybootTheme.colors.backgroundPrimary */
  color: #2C3E50; /* skybootTheme.colors.textPrimary */
  line-height: 1.6;
}

#app {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* 커스텀 테마 CSS 변수 */
:root {
  --skyboot-primary: #2C3E50;
  --skyboot-secondary: #34495E;
  --skyboot-success: #27AE60;
  --skyboot-info: #3498DB;
  --skyboot-warning: #F39C12;
  --skyboot-danger: #E74C3C;
  
  --skyboot-bg-primary: #FDFCF8;
  --skyboot-bg-secondary: #F8F6F0;
  --skyboot-bg-element: #FFFFFF;
  --skyboot-bg-border: #E8E6E0;
  
  --skyboot-text-primary: #2C3E50;
  --skyboot-text-inverted: #FFFFFF;
  
  --skyboot-navy-50: #F7F9FC;
  --skyboot-navy-100: #E3EAF2;
  --skyboot-navy-500: #5A7FA3;
  --skyboot-navy-900: #1E2D3E;
  
  --skyboot-beige-50: #FDFCF8;
  --skyboot-beige-100: #FAF7F0;
  --skyboot-beige-200: #F5F0E8;
  --skyboot-beige-500: #E6DBCE;
  
  --skyboot-shadow-sm: 0 1px 3px 0 rgba(44, 62, 80, 0.1), 0 1px 2px 0 rgba(44, 62, 80, 0.06);
  --skyboot-shadow-md: 0 4px 6px -1px rgba(44, 62, 80, 0.1), 0 2px 4px -1px rgba(44, 62, 80, 0.06);
  --skyboot-shadow-lg: 0 10px 15px -3px rgba(44, 62, 80, 0.1), 0 4px 6px -2px rgba(44, 62, 80, 0.05);
}

/* 스크롤바 스타일링 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--skyboot-beige-100);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: var(--skyboot-beige-500);
  border-radius: 3px;
  transition: background 0.2s ease;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--skyboot-navy-500);
}

/* 유틸리티 클래스 */
.w-100 { width: 100% !important; }
.h-100 { height: 100% !important; }
.d-flex { display: flex !important; }
.flex-column { flex-direction: column !important; }
.flex-row { flex-direction: row !important; }
.justify-center { justify-content: center !important; }
.justify-between { justify-content: space-between !important; }
.align-center { align-items: center !important; }
.text-center { text-align: center !important; }
.text-left { text-align: left !important; }
.text-right { text-align: right !important; }

.text-sm {
  font-size: 0.875rem;
}

.text-lg {
  font-size: 1.125rem;
}

.text-xl {
  font-size: 1.25rem;
}

.text-gray-500 {
  color: #6c757d;
}

.text-gray-600 {
  color: #495057;
}

.text-gray-700 {
  color: #343a40;
}

/* 간격 유틸리티 */
.m-0 { margin: 0 !important; }
.m-1 { margin: 0.25rem !important; }
.m-2 { margin: 0.5rem !important; }
.m-3 { margin: 1rem !important; }
.m-4 { margin: 1.5rem !important; }
.m-5 { margin: 3rem !important; }

.p-0 { padding: 0 !important; }
.p-1 { padding: 0.25rem !important; }
.p-2 { padding: 0.5rem !important; }
.p-3 { padding: 1rem !important; }
.p-4 { padding: 1.5rem !important; }
.p-5 { padding: 3rem !important; }

.mb-0 {
  margin-bottom: 0;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.mb-3 {
  margin-bottom: 1rem;
}

.mb-4 {
  margin-bottom: 1.5rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

.mt-2 {
  margin-top: 0.5rem;
}

.mt-1 { margin-top: 0.25rem !important; }
.mt-3 { margin-top: 1rem !important; }
.mt-4 { margin-top: 1.5rem !important; }
.mt-5 { margin-top: 3rem !important; }

.ml-1 { margin-left: 0.25rem !important; }
.ml-3 { margin-left: 1rem !important; }
.ml-4 { margin-left: 1.5rem !important; }
.ml-5 { margin-left: 3rem !important; }

.mr-1 { margin-right: 0.25rem !important; }
.mr-3 { margin-right: 1rem !important; }
.mr-4 { margin-right: 1.5rem !important; }
.mr-5 { margin-right: 3rem !important; }

/* 색상 유틸리티 클래스 */
.text-primary { color: var(--skyboot-primary) !important; }
.text-secondary { color: var(--skyboot-secondary) !important; }
.text-success { color: var(--skyboot-success) !important; }
.text-info { color: var(--skyboot-info) !important; }
.text-warning { color: var(--skyboot-warning) !important; }
.text-danger { color: var(--skyboot-danger) !important; }

.bg-primary { background-color: var(--skyboot-bg-primary) !important; }
.bg-secondary { background-color: var(--skyboot-bg-secondary) !important; }
.bg-element { background-color: var(--skyboot-bg-element) !important; }

/* 그림자 유틸리티 클래스 */
.shadow-sm { box-shadow: var(--skyboot-shadow-sm) !important; }
.shadow-md { box-shadow: var(--skyboot-shadow-md) !important; }
.shadow-lg { box-shadow: var(--skyboot-shadow-lg) !important; }

/* 애니메이션 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

.scale-enter-active,
.scale-leave-active {
  transition: transform 0.25s ease;
}

.scale-enter-from,
.scale-leave-to {
  transform: scale(0.95);
}

/* 반응형 헬퍼 */
.d-none {
  display: none;
}

.d-block {
  display: block;
}

.justify-content-center {
  justify-content: center;
}

.justify-content-between {
  justify-content: space-between;
}

.align-items-center {
  align-items: center;
}

.flex-wrap {
  flex-wrap: wrap;
}

/* 반응형 미디어 쿼리 */
@media (max-width: 768px) {
  .d-md-none {
    display: none;
  }
  
  .d-md-block {
    display: block;
  }
  
  .mobile-hidden {
    display: none !important;
  }
  
  .mobile-full-width {
    width: 100% !important;
  }
}

@media (max-width: 576px) {
  .d-sm-none {
    display: none;
  }
  
  .d-sm-block {
    display: block;
  }
}

@media (min-width: 769px) {
  .desktop-hidden {
    display: none !important;
  }
}

/* 포커스 스타일 */
.va-input:focus-within,
.va-select:focus-within,
.va-textarea:focus-within {
  box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.2);
  border-color: var(--skyboot-primary);
}

/* 카드 스타일 개선 */
.va-card {
  border-radius: 0.75rem;
  box-shadow: var(--skyboot-shadow-md);
  transition: all 0.25s ease;
  background-color: var(--skyboot-bg-element);
  border: 1px solid var(--skyboot-bg-border);
}

.va-card:hover {
  box-shadow: var(--skyboot-shadow-lg);
  transform: translateY(-2px);
}

/* 버튼 스타일 개선 */
.va-button {
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s ease;
  font-family: inherit;
}

.va-button:hover {
  transform: translateY(-1px);
  box-shadow: var(--skyboot-shadow-md);
}

.va-button--primary {
  background-color: var(--skyboot-primary);
  border-color: var(--skyboot-primary);
}

.va-button--secondary {
  background-color: var(--skyboot-secondary);
  border-color: var(--skyboot-secondary);
}

/* 테이블 스타일 개선 */
.va-data-table {
  border-radius: 0.75rem;
  overflow: hidden;
  background-color: var(--skyboot-bg-element);
  box-shadow: var(--skyboot-shadow-sm);
}

.va-data-table th {
  background-color: var(--skyboot-bg-secondary);
  font-weight: 600;
  color: var(--skyboot-text-primary);
  border-bottom: 1px solid var(--skyboot-bg-border);
}

.va-data-table tr:nth-child(even) {
  background-color: var(--skyboot-bg-primary);
}

.va-data-table tr:hover {
  background-color: var(--skyboot-beige-100);
}

/* 모달 스타일 개선 */
.va-modal .va-modal__container {
  border-radius: 0.75rem;
  background-color: var(--skyboot-bg-element);
  box-shadow: var(--skyboot-shadow-lg);
}

.va-modal .va-modal__backdrop {
  background-color: rgba(44, 62, 80, 0.5);
}

/* 사이드바 스타일 개선 */
.va-sidebar {
  background: linear-gradient(180deg, var(--skyboot-primary) 0%, var(--skyboot-secondary) 100%);
  box-shadow: var(--skyboot-shadow-lg);
}

.va-sidebar .va-sidebar-item {
  transition: all 0.2s ease;
}

.va-sidebar .va-sidebar-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.va-sidebar .va-sidebar-item--active {
  background-color: rgba(255, 255, 255, 0.15);
  border-right: 3px solid var(--skyboot-bg-element);
}

/* 입력 필드 스타일 개선 */
.va-input,
.va-select,
.va-textarea {
  border-radius: 0.5rem;
  background-color: var(--skyboot-bg-element);
  border-color: var(--skyboot-bg-border);
  transition: all 0.2s ease;
}

.va-input:hover,
.va-select:hover,
.va-textarea:hover {
  border-color: var(--skyboot-navy-500);
}

/* 알림 스타일 개선 */
.va-alert {
  border-radius: 0.5rem;
  font-weight: 500;
  box-shadow: var(--skyboot-shadow-sm);
}

/* 배지 스타일 개선 */
.va-badge {
  border-radius: 0.375rem;
  font-weight: 500;
  font-size: 0.75rem;
}

/* 호버 효과 */
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: var(--skyboot-shadow-lg);
}

/* 로딩 스피너 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(253, 252, 248, 0.9);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* 상태별 색상 클래스 */
.status-active {
  color: var(--skyboot-success);
  background-color: rgba(39, 174, 96, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-inactive {
  color: #95A5A6;
  background-color: rgba(149, 165, 166, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.status-coming-soon {
  color: var(--skyboot-warning);
  background-color: rgba(243, 156, 18, 0.1);
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
}

/* 커스텀 스크롤 영역 */
.custom-scroll {
  scrollbar-width: thin;
  scrollbar-color: var(--skyboot-beige-500) var(--skyboot-beige-100);
}

/* 글래스모피즘 효과 */
.glass-effect {
  background: rgba(255, 255, 255, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
}

/* 텍스트 그라데이션 */
.text-gradient {
  background: linear-gradient(135deg, var(--skyboot-primary) 0%, var(--skyboot-info) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
</style>

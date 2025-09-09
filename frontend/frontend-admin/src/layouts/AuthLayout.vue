<template>
  <div class="auth-layout">
    <div class="auth-container">
      <!-- 배경 장식 -->
      <div class="background-decoration">
        <div class="decoration-circle circle-1"></div>
        <div class="decoration-circle circle-2"></div>
        <div class="decoration-circle circle-3"></div>
      </div>

      <!-- 메인 콘텐츠 -->
      <div class="auth-content">
        <!-- 로고 및 브랜딩 영역 -->
        <div class="auth-header">
          <div class="logo-section">
            <VaIcon
              name="admin_panel_settings"
              size="3rem"
              color="primary"
            />
            <h1 class="brand-title">SkyBoot Admin</h1>
            <p class="brand-subtitle">관리자 시스템에 오신 것을 환영합니다</p>
          </div>
        </div>

        <!-- 인증 폼 영역 -->
        <div class="auth-form-container">
          <VaCard class="auth-card">
            <VaCardContent class="auth-card-content">
              <router-view />
            </VaCardContent>
          </VaCard>
        </div>

        <!-- 푸터 정보 -->
        <div class="auth-footer">
          <div class="footer-links">
            <a href="#" class="footer-link">이용약관</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">개인정보처리방침</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">고객지원</a>
          </div>
          <div class="footer-copyright">
            © 2024 SkyBoot Core. All rights reserved.
          </div>
        </div>
      </div>

      <!-- 다크모드 토글 -->
      <div class="theme-toggle">
        <VaButton
          preset="secondary"
          :icon="themeStore.isDark ? 'light_mode' : 'dark_mode'"
          @click="themeStore.toggleTheme"
          round
          size="large"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useThemeStore } from '../stores/theme';

const themeStore = useThemeStore();
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.auth-container {
  width: 100%;
  max-width: 1200px;
  position: relative;
  z-index: 1;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  top: 60%;
  right: 15%;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  left: 20%;
  animation-delay: 4s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(180deg);
  }
}

.auth-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  min-height: 80vh;
}

.auth-header {
  text-align: center;
  color: white;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.brand-title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: 1.25rem;
  opacity: 0.9;
  margin: 0;
  max-width: 400px;
  line-height: 1.6;
}

.auth-form-container {
  display: flex;
  justify-content: center;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.auth-card-content {
  padding: 3rem;
}

.auth-footer {
  grid-column: 1 / -1;
  text-align: center;
  color: white;
  margin-top: 2rem;
}

.footer-links {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.footer-link {
  color: white;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.3s ease;
}

.footer-link:hover {
  opacity: 1;
  text-decoration: underline;
}

.footer-separator {
  opacity: 0.6;
}

.footer-copyright {
  font-size: 0.875rem;
  opacity: 0.7;
}

.theme-toggle {
  position: absolute;
  top: 2rem;
  right: 2rem;
  z-index: 10;
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .auth-content {
    grid-template-columns: 1fr;
    gap: 3rem;
    text-align: center;
  }
  
  .brand-title {
    font-size: 2.5rem;
  }
}

@media (max-width: 768px) {
  .auth-layout {
    padding: 1rem;
  }
  
  .auth-content {
    gap: 2rem;
    min-height: auto;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-subtitle {
    font-size: 1rem;
  }
  
  .auth-card-content {
    padding: 2rem;
  }
  
  .theme-toggle {
    top: 1rem;
    right: 1rem;
  }
  
  .footer-links {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .footer-separator {
    display: none;
  }
}

@media (max-width: 480px) {
  .auth-card-content {
    padding: 1.5rem;
  }
  
  .brand-title {
    font-size: 1.75rem;
  }
}

/* 다크 모드 지원 */
.va-dark {
  .auth-layout {
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  }
  
  .auth-card {
    background: rgba(45, 55, 72, 0.95);
    color: white;
  }
  
  .decoration-circle {
    background: rgba(255, 255, 255, 0.05);
  }
}

/* 애니메이션 */
.auth-card {
  animation: slideUp 0.6s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logo-section {
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
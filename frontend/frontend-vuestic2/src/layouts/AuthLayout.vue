<template>
  <div class="auth-layout">
    <div class="auth-container">
      <!-- 로고 및 브랜딩 영역 -->
      <div class="brand-section">
        <div class="brand-content">
          <div class="logo">
            <va-icon name="admin_panel_settings" size="4rem" color="primary" />
          </div>
          <h1 class="brand-title">SkyBoot Admin</h1>
          <p class="brand-subtitle">
            관리자 시스템에 오신 것을 환영합니다
          </p>
        </div>
        
        <!-- 배경 장식 -->
        <div class="background-decoration">
          <div class="decoration-circle circle-1"></div>
          <div class="decoration-circle circle-2"></div>
          <div class="decoration-circle circle-3"></div>
        </div>
      </div>

      <!-- 인증 폼 영역 -->
      <div class="auth-section">
        <div class="auth-card">
          <router-view />
        </div>
        
        <!-- 푸터 정보 -->
        <div class="auth-footer">
          <p class="text-sm text-gray-500">
            © 2024 SkyBoot Core. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// 인증 레이아웃 컴포넌트
// 로그인, 회원가입 등 인증 관련 페이지에서 사용
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f5dc 0%, #e8e8e8 50%, #2c3e50 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.auth-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  max-width: 1200px;
  width: 100%;
  min-height: 600px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.brand-section {
  position: relative;
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: white;
}

.brand-content {
  text-align: center;
  z-index: 2;
  position: relative;
}

.logo {
  margin-bottom: 2rem;
  animation: float 3s ease-in-out infinite;
}

.brand-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #f5f5dc, #ffffff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.6;
  max-width: 300px;
  margin: 0 auto;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(245, 245, 220, 0.1);
  animation: float 6s ease-in-out infinite;
}

.circle-1 {
  width: 200px;
  height: 200px;
  top: -100px;
  right: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 150px;
  height: 150px;
  bottom: -75px;
  left: -75px;
  animation-delay: 2s;
}

.circle-3 {
  width: 100px;
  height: 100px;
  top: 50%;
  right: 20px;
  animation-delay: 4s;
}

.auth-section {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 3rem;
  background: #fafafa;
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e9ecef;
}

.auth-footer {
  text-align: center;
  margin-top: 2rem;
}

/* 애니메이션 */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 0.1;
  }
  50% {
    opacity: 0.2;
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .auth-layout {
    padding: 1rem;
  }
  
  .auth-container {
    grid-template-columns: 1fr;
    max-width: 400px;
    min-height: auto;
  }
  
  .brand-section {
    padding: 2rem;
    min-height: 200px;
  }
  
  .brand-title {
    font-size: 2rem;
  }
  
  .brand-subtitle {
    font-size: 1rem;
  }
  
  .auth-section {
    padding: 2rem;
  }
  
  .auth-card {
    padding: 2rem;
  }
  
  .decoration-circle {
    display: none;
  }
}

@media (max-width: 480px) {
  .auth-layout {
    padding: 0.5rem;
  }
  
  .brand-section {
    padding: 1.5rem;
  }
  
  .auth-section {
    padding: 1.5rem;
  }
  
  .auth-card {
    padding: 1.5rem;
  }
}

/* 부드러운 전환 효과 */
.auth-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.auth-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
}
</style>
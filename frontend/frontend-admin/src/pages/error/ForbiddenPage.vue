<template>
  <div class="error-container">
    <div class="error-content">
      <!-- 에러 일러스트레이션 -->
      <div class="error-illustration">
        <VaIcon
          name="block"
          size="8rem"
          color="danger"
        />
      </div>

      <!-- 에러 정보 -->
      <div class="error-info">
        <h1 class="error-code">403</h1>
        <h2 class="error-title">접근 권한이 없습니다</h2>
        <p class="error-description">
          요청하신 페이지에 접근할 권한이 없습니다.<br>
          관리자에게 문의하거나 다른 페이지를 이용해 주세요.
        </p>
      </div>

      <!-- 액션 버튼 -->
      <div class="error-actions">
        <VaButton
          color="primary"
          size="large"
          @click="goBack"
        >
          <VaIcon name="arrow_back" class="mr-2" />
          이전 페이지로
        </VaButton>
        
        <VaButton
          color="secondary"
          preset="secondary"
          size="large"
          @click="goHome"
        >
          <VaIcon name="home" class="mr-2" />
          홈으로 가기
        </VaButton>
      </div>

      <!-- 추가 도움말 -->
      <div class="error-help">
        <VaCard class="help-card">
          <VaCardContent>
            <h3 class="help-title">
              <VaIcon name="help_outline" class="mr-2" />
              도움이 필요하신가요?
            </h3>
            <ul class="help-list">
              <li>로그인 상태를 확인해 주세요</li>
              <li>올바른 권한이 있는지 확인해 주세요</li>
              <li>관리자에게 권한 요청을 문의해 주세요</li>
            </ul>
            
            <div class="contact-info">
              <VaButton
                preset="secondary"
                size="small"
                @click="contactAdmin"
              >
                <VaIcon name="email" class="mr-1" />
                관리자 문의
              </VaButton>
            </div>
          </VaCardContent>
        </VaCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useToast } from 'vuestic-ui';

const router = useRouter();
const authStore = useAuthStore();
const { init: notify } = useToast();

// 이전 페이지로 이동
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    goHome();
  }
};

// 홈으로 이동
const goHome = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard');
  } else {
    router.push('/login');
  }
};

// 관리자 문의
const contactAdmin = () => {
  notify({
    message: '관리자 문의 기능은 준비 중입니다.',
    color: 'info',
    duration: 3000,
  });
};
</script>

<style scoped>
.error-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.error-content {
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.error-illustration {
  margin-bottom: 2rem;
  animation: bounce 2s infinite;
}

.error-info {
  margin-bottom: 3rem;
}

.error-code {
  font-size: 6rem;
  font-weight: 900;
  color: #f44336;
  margin: 0;
  line-height: 1;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 1rem 0;
}

.error-description {
  font-size: 1.125rem;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.error-help {
  max-width: 400px;
  margin: 0 auto;
}

.help-card {
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.help-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.help-list {
  list-style: none;
  padding: 0;
  margin: 0 0 1.5rem 0;
}

.help-list li {
  padding: 0.5rem 0;
  color: #666;
  position: relative;
  padding-left: 1.5rem;
}

.help-list li::before {
  content: '•';
  color: #1976d2;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.contact-info {
  text-align: center;
}

.mr-1 {
  margin-right: 0.25rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-10px);
  }
  60% {
    transform: translateY(-5px);
  }
}

@media (max-width: 768px) {
  .error-container {
    padding: 1rem;
  }
  
  .error-code {
    font-size: 4rem;
  }
  
  .error-title {
    font-size: 1.5rem;
  }
  
  .error-description {
    font-size: 1rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .va-button {
    width: 100%;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  .error-container {
    padding: 0.5rem;
  }
  
  .error-illustration {
    margin-bottom: 1rem;
  }
  
  .error-illustration .va-icon {
    font-size: 4rem !important;
  }
  
  .error-code {
    font-size: 3rem;
  }
  
  .error-info {
    margin-bottom: 2rem;
  }
  
  .error-actions {
    margin-bottom: 2rem;
  }
}
</style>
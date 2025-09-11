<template>
  <div class="unauthorized-container">
    <va-card class="unauthorized-card">
      <va-card-content class="text-center">
        <!-- 아이콘 섹션 -->
        <div class="icon-section">
          <va-icon 
            name="block" 
            size="4rem" 
            color="warning"
            class="unauthorized-icon"
          />
        </div>
        
        <!-- 메시지 섹션 -->
        <div class="message-section">
          <h1 class="unauthorized-title">
            접근 권한이 없습니다
          </h1>
          
          <p class="unauthorized-description">
            죄송합니다. 이 페이지에 접근할 권한이 없습니다.<br>
            필요한 권한이 있다면 관리자에게 문의해 주세요.
          </p>
          
          <div class="user-info" v-if="currentUser">
            <va-chip color="info" size="small">
              <va-icon name="person" size="small" class="mr-1" />
              {{ currentUser.username }}
            </va-chip>
            
            <va-chip 
              v-for="role in userRoles" 
              :key="role.id"
              color="secondary" 
              size="small"
              class="ml-2"
            >
              <va-icon name="admin_panel_settings" size="small" class="mr-1" />
              {{ role.name }}
            </va-chip>
          </div>
        </div>
        
        <!-- 액션 버튼 섹션 -->
        <div class="action-section">
          <va-button 
            @click="goToDashboard"
            color="primary"
            class="mr-3"
          >
            <va-icon name="dashboard" class="mr-2" />
            대시보드로 이동
          </va-button>
          
          <va-button 
            @click="goBack"
            color="secondary"
            preset="secondary"
          >
            <va-icon name="arrow_back" class="mr-2" />
            이전 페이지
          </va-button>
        </div>
        
        <!-- 도움말 섹션 -->
        <div class="help-section">
          <va-alert 
            color="info" 
            border="left"
            border-color="info"
            class="text-left"
          >
            <template #icon>
              <va-icon name="info" />
            </template>
            
            <div class="help-content">
              <strong>권한 요청 방법:</strong>
              <ul class="help-list">
                <li>시스템 관리자에게 연락</li>
                <li>필요한 권한과 사용 목적 설명</li>
                <li>승인 후 페이지 접근 가능</li>
              </ul>
            </div>
          </va-alert>
        </div>
        
        <!-- 연락처 정보 -->
        <div class="contact-section">
          <p class="contact-text">
            <va-icon name="support_agent" class="mr-2" />
            문의사항이 있으시면 
            <a href="mailto:admin@skyboot.com" class="contact-link">
              admin@skyboot.com
            </a>
            으로 연락해 주세요.
          </p>
        </div>
      </va-card-content>
    </va-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

// 계산된 속성
const currentUser = computed(() => authStore.user)
const userRoles = computed(() => authStore.userRoles || [])

/**
 * 대시보드로 이동
 */
const goToDashboard = () => {
  router.push({ name: 'Dashboard' })
}

/**
 * 이전 페이지로 이동
 */
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    goToDashboard()
  }
}
</script>

<style scoped>
.unauthorized-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, 
    var(--skyboot-bg-primary) 0%, 
    var(--skyboot-bg-secondary) 100%);
}

.unauthorized-card {
  max-width: 600px;
  width: 100%;
  box-shadow: var(--skyboot-shadow-xl);
  border-radius: 1rem;
  overflow: hidden;
  background: var(--skyboot-bg-element);
  border: 1px solid var(--skyboot-bg-border);
}

.icon-section {
  margin-bottom: 2rem;
}

.unauthorized-icon {
  animation: pulse 2s infinite;
  filter: drop-shadow(0 4px 8px rgba(255, 193, 7, 0.3));
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.8;
  }
}

.message-section {
  margin-bottom: 2rem;
}

.unauthorized-title {
  font-size: 2rem;
  font-weight: 700;
  color: var(--skyboot-text-primary);
  margin-bottom: 1rem;
  background: linear-gradient(135deg, 
    var(--skyboot-primary) 0%, 
    var(--skyboot-warning) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.unauthorized-description {
  font-size: 1.1rem;
  color: var(--skyboot-navy-600);
  line-height: 1.6;
  margin-bottom: 1.5rem;
}

.user-info {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.action-section {
  margin-bottom: 2rem;
}

.action-section .va-button {
  min-width: 140px;
  font-weight: 600;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.action-section .va-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--skyboot-shadow-md);
}

.help-section {
  margin-bottom: 1.5rem;
  text-align: left;
}

.help-content {
  font-size: 0.95rem;
}

.help-list {
  margin: 0.5rem 0 0 1rem;
  padding: 0;
}

.help-list li {
  margin-bottom: 0.25rem;
  color: var(--skyboot-navy-600);
}

.contact-section {
  padding-top: 1rem;
  border-top: 1px solid var(--skyboot-bg-border);
}

.contact-text {
  font-size: 0.9rem;
  color: var(--skyboot-navy-500);
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
}

.contact-link {
  color: var(--skyboot-primary);
  text-decoration: none;
  font-weight: 600;
  transition: color 0.2s ease;
}

.contact-link:hover {
  color: var(--skyboot-info);
  text-decoration: underline;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .unauthorized-container {
    padding: 1rem;
  }
  
  .unauthorized-title {
    font-size: 1.5rem;
  }
  
  .unauthorized-description {
    font-size: 1rem;
  }
  
  .action-section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .action-section .va-button {
    width: 100%;
    margin: 0;
  }
  
  .contact-text {
    text-align: center;
    line-height: 1.5;
  }
  
  .user-info {
    justify-content: center;
  }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .unauthorized-card {
    background: var(--skyboot-navy-800);
    border-color: var(--skyboot-navy-700);
  }
  
  .unauthorized-title {
    color: var(--skyboot-beige-100);
  }
  
  .unauthorized-description {
    color: var(--skyboot-beige-200);
  }
  
  .contact-text {
    color: var(--skyboot-beige-300);
  }
}

/* 애니메이션 효과 */
.unauthorized-card {
  animation: slideInUp 0.6s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 호버 효과 */
.unauthorized-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--skyboot-shadow-2xl);
  transition: all 0.3s ease;
}
</style>
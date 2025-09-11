<template>
  <div class="coming-soon-container">
    <va-card class="coming-soon-card">
      <va-card-content class="text-center">
        <!-- 아이콘 섹션 -->
        <div class="icon-section">
          <va-icon 
            :name="icon" 
            size="4rem" 
            color="primary"
            class="coming-soon-icon"
          />
        </div>
        
        <!-- 메시지 섹션 -->
        <div class="message-section">
          <h1 class="coming-soon-title">
            {{ title }}
          </h1>
          
          <p class="coming-soon-description">
            {{ description }}
          </p>
          
          <!-- 기능 목록 -->
          <div v-if="features && features.length > 0" class="features-section">
            <h3 class="features-title">예정된 기능</h3>
            <ul class="features-list">
              <li 
                v-for="(feature, index) in features" 
                :key="index"
                class="feature-item"
              >
                <va-icon name="check_circle" color="success" size="small" class="mr-2" />
                {{ feature }}
              </li>
            </ul>
          </div>
        </div>
        
        <!-- 진행률 섹션 -->
        <div v-if="showProgress" class="progress-section">
          <div class="progress-info">
            <span class="progress-label">개발 진행률</span>
            <span class="progress-value">{{ progress }}%</span>
          </div>
          <va-progress-bar 
            :model-value="progress" 
            color="primary"
            class="progress-bar"
          />
        </div>
        
        <!-- 알림 신청 섹션 -->
        <div v-if="showNotification" class="notification-section">
          <va-alert 
            color="info" 
            border="left"
            border-color="info"
            class="notification-alert"
          >
            <template #icon>
              <va-icon name="notifications" />
            </template>
            
            <div class="notification-content">
              <strong>출시 알림 받기</strong>
              <p class="notification-text">
                이 기능이 출시되면 알림을 받고 싶으시다면 관리자에게 문의해 주세요.
              </p>
            </div>
          </va-alert>
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
import { withDefaults } from 'vue'
import { useRouter } from 'vue-router'

// Props 인터페이스 정의
interface Props {
  title?: string
  description?: string
  icon?: string
  features?: string[]
  progress?: number
  showProgress?: boolean
  showNotification?: boolean
}

// Props 기본값 설정
const props = withDefaults(defineProps<Props>(), {
  title: '곧 출시됩니다!',
  description: '이 기능은 현재 개발 중입니다. 빠른 시일 내에 만나보실 수 있도록 최선을 다하고 있습니다.',
  icon: 'construction',
  features: () => [],
  progress: 0,
  showProgress: false,
  showNotification: true
})

const router = useRouter()

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
.coming-soon-container {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.coming-soon-card {
  max-width: 700px;
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

.coming-soon-icon {
  animation: bounce 2s infinite;
  filter: drop-shadow(0 4px 8px rgba(var(--skyboot-primary-rgb), 0.3));
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

.message-section {
  margin-bottom: 2rem;
}

.coming-soon-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--skyboot-text-primary);
  margin-bottom: 1rem;
  background: linear-gradient(135deg, 
    var(--skyboot-primary) 0%, 
    var(--skyboot-info) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.coming-soon-description {
  font-size: 1.2rem;
  color: var(--skyboot-navy-600);
  line-height: 1.6;
  margin-bottom: 2rem;
}

.features-section {
  text-align: left;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--skyboot-bg-secondary);
  border-radius: 0.75rem;
  border: 1px solid var(--skyboot-bg-border);
}

.features-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--skyboot-text-primary);
  margin-bottom: 1rem;
  text-align: center;
}

.features-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.feature-item {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
  color: var(--skyboot-navy-700);
  font-size: 1rem;
  transition: all 0.2s ease;
}

.feature-item:hover {
  color: var(--skyboot-primary);
  transform: translateX(5px);
}

.progress-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: var(--skyboot-bg-secondary);
  border-radius: 0.75rem;
  border: 1px solid var(--skyboot-bg-border);
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-label {
  font-weight: 600;
  color: var(--skyboot-text-primary);
}

.progress-value {
  font-weight: 700;
  color: var(--skyboot-primary);
  font-size: 1.1rem;
}

.progress-bar {
  height: 8px;
  border-radius: 4px;
}

.notification-section {
  margin-bottom: 2rem;
  text-align: left;
}

.notification-content {
  font-size: 0.95rem;
}

.notification-text {
  margin: 0.5rem 0 0 0;
  color: var(--skyboot-navy-600);
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

.contact-section {
  padding-top: 1.5rem;
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
  .coming-soon-container {
    padding: 1rem;
  }
  
  .coming-soon-title {
    font-size: 2rem;
  }
  
  .coming-soon-description {
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
  
  .features-section,
  .progress-section {
    padding: 1rem;
  }
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .coming-soon-card {
    background: var(--skyboot-navy-800);
    border-color: var(--skyboot-navy-700);
  }
  
  .features-section,
  .progress-section {
    background: var(--skyboot-navy-700);
    border-color: var(--skyboot-navy-600);
  }
}

/* 애니메이션 효과 */
.coming-soon-card {
  animation: fadeInUp 0.8s ease-out;
}

@keyframes fadeInUp {
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
.coming-soon-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--skyboot-shadow-2xl);
  transition: all 0.3s ease;
}

/* 글로우 효과 */
.coming-soon-icon {
  position: relative;
}

.coming-soon-icon::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120%;
  height: 120%;
  background: radial-gradient(circle, 
    rgba(var(--skyboot-primary-rgb), 0.2) 0%, 
    transparent 70%);
  border-radius: 50%;
  z-index: -1;
  animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    opacity: 0.5;
    transform: translate(-50%, -50%) scale(1);
  }
  to {
    opacity: 0.8;
    transform: translate(-50%, -50%) scale(1.1);
  }
}
</style>
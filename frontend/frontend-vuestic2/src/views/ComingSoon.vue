<template>
  <div class="coming-soon-page">
    <div class="coming-soon-container">
      <!-- 애니메이션 아이콘 -->
      <div class="icon-section">
        <div class="icon-wrapper">
          <va-icon name="schedule" size="6rem" color="primary" class="main-icon" />
          <div class="pulse-ring"></div>
          <div class="pulse-ring pulse-ring-delay"></div>
        </div>
      </div>

      <!-- 메인 콘텐츠 -->
      <div class="content-section">
        <h1 class="coming-soon-title">
          곧 출시됩니다
        </h1>
        
        <p class="coming-soon-subtitle">
          이 기능은 현재 개발 중입니다.
        </p>
        
        <div class="feature-description">
          <p>
            더 나은 사용자 경험을 위해 열심히 개발하고 있습니다.
            조금만 기다려 주시면 곧 만나보실 수 있습니다.
          </p>
        </div>

        <!-- 개발 진행 상황 -->
        <div class="progress-section">
          <div class="progress-info">
            <span class="progress-label">개발 진행률</span>
            <span class="progress-value">{{ developmentProgress }}%</span>
          </div>
          <va-progress-bar
            :model-value="developmentProgress"
            color="primary"
            size="large"
            class="progress-bar"
          />
        </div>

        <!-- 예상 출시일 -->
        <div class="timeline-section">
          <va-card class="timeline-card">
            <va-card-content>
              <div class="timeline-content">
                <va-icon name="event" color="primary" class="timeline-icon" />
                <div class="timeline-text">
                  <h3>예상 출시일</h3>
                  <p>{{ estimatedReleaseDate }}</p>
                </div>
              </div>
            </va-card-content>
          </va-card>
        </div>

        <!-- 기능 미리보기 -->
        <div class="features-preview">
          <h3 class="preview-title">출시 예정 기능</h3>
          <div class="features-grid">
            <div
              v-for="feature in upcomingFeatures"
              :key="feature.id"
              class="feature-item"
            >
              <va-icon :name="feature.icon" :color="feature.color" size="2rem" />
              <h4>{{ feature.title }}</h4>
              <p>{{ feature.description }}</p>
            </div>
          </div>
        </div>

        <!-- 액션 버튼 -->
        <div class="action-section">
          <va-button
            preset="primary"
            size="large"
            icon="arrow_back"
            @click="goBack"
            class="back-button"
          >
            이전 페이지로
          </va-button>
          
          <va-button
            preset="secondary"
            size="large"
            icon="home"
            @click="goHome"
            class="home-button"
          >
            홈으로
          </va-button>
        </div>

        <!-- 알림 신청 -->
        <div class="notification-section">
          <va-card class="notification-card">
            <va-card-content>
              <div class="notification-content">
                <va-icon name="notifications" color="warning" class="notification-icon" />
                <div class="notification-text">
                  <h4>출시 알림 받기</h4>
                  <p>새로운 기능이 출시되면 알려드릴게요!</p>
                </div>
                <va-button
                  preset="primary"
                  icon="notification_add"
                  @click="subscribeNotification"
                >
                  알림 신청
                </va-button>
              </div>
            </va-card-content>
          </va-card>
        </div>
      </div>
    </div>

    <!-- 배경 장식 -->
    <div class="background-decoration">
      <div class="decoration-circle circle-1"></div>
      <div class="decoration-circle circle-2"></div>
      <div class="decoration-circle circle-3"></div>
      <div class="decoration-circle circle-4"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 반응형 데이터
const developmentProgress = ref(0)
const estimatedReleaseDate = ref('2024년 3월 예정')

// 출시 예정 기능들
const upcomingFeatures = ref([
  {
    id: 1,
    title: '고급 검색',
    description: '더 정확하고 빠른 검색 기능',
    icon: 'search',
    color: 'primary'
  },
  {
    id: 2,
    title: '실시간 알림',
    description: '중요한 업데이트를 즉시 알림',
    icon: 'notifications_active',
    color: 'warning'
  },
  {
    id: 3,
    title: '데이터 분석',
    description: '상세한 통계 및 분석 리포트',
    icon: 'analytics',
    color: 'info'
  },
  {
    id: 4,
    title: '모바일 최적화',
    description: '모든 기기에서 완벽한 경험',
    icon: 'phone_android',
    color: 'success'
  }
])

// 메서드
const goBack = () => {
  router.go(-1)
}

const goHome = () => {
  router.push('/')
}

const subscribeNotification = () => {
  // 실제 구현에서는 알림 신청 API 호출
  console.log('알림 신청')
  // 성공 메시지 표시 등
}

// 진행률 애니메이션
const animateProgress = () => {
  const targetProgress = 75 // 실제 개발 진행률
  const duration = 2000 // 2초
  const steps = 60
  const increment = targetProgress / steps
  let currentStep = 0

  const timer = setInterval(() => {
    currentStep++
    developmentProgress.value = Math.min(currentStep * increment, targetProgress)
    
    if (currentStep >= steps) {
      clearInterval(timer)
    }
  }, duration / steps)
}

// 라이프사이클
onMounted(() => {
  // 페이지 로드 후 진행률 애니메이션 시작
  setTimeout(() => {
    animateProgress()
  }, 500)
})
</script>

<style scoped>
.coming-soon-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f5dc 0%, #e8e8e8 50%, #2c3e50 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
}

.coming-soon-container {
  max-width: 800px;
  width: 100%;
  text-align: center;
  position: relative;
  z-index: 2;
}

.icon-section {
  margin-bottom: 3rem;
  position: relative;
  display: inline-block;
}

.icon-wrapper {
  position: relative;
  display: inline-block;
}

.main-icon {
  position: relative;
  z-index: 3;
  animation: float 3s ease-in-out infinite;
}

.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 120px;
  height: 120px;
  border: 3px solid rgba(52, 152, 219, 0.3);
  border-radius: 50%;
  animation: pulse 2s ease-out infinite;
}

.pulse-ring-delay {
  animation-delay: 1s;
  border-color: rgba(52, 152, 219, 0.2);
}

.content-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 3rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.coming-soon-title {
  font-size: 3rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #2c3e50, #3498db);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.coming-soon-subtitle {
  font-size: 1.25rem;
  color: #6c757d;
  margin-bottom: 2rem;
}

.feature-description {
  margin-bottom: 3rem;
}

.feature-description p {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #495057;
  max-width: 600px;
  margin: 0 auto;
}

.progress-section {
  margin-bottom: 3rem;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-label {
  font-weight: 600;
  color: #2c3e50;
}

.progress-value {
  font-weight: 700;
  color: #3498db;
  font-size: 1.1rem;
}

.progress-bar {
  border-radius: 10px;
  overflow: hidden;
}

.timeline-section {
  margin-bottom: 3rem;
}

.timeline-card {
  max-width: 400px;
  margin: 0 auto;
  border-left: 4px solid #3498db;
}

.timeline-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.timeline-icon {
  font-size: 2rem;
}

.timeline-text h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.timeline-text p {
  margin: 0;
  color: #6c757d;
  font-weight: 600;
}

.features-preview {
  margin-bottom: 3rem;
}

.preview-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.feature-item {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.feature-item h4 {
  margin: 1rem 0 0.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.feature-item p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
  line-height: 1.4;
}

.action-section {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
}

.back-button,
.home-button {
  min-width: 150px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.back-button:hover,
.home-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.notification-section {
  max-width: 500px;
  margin: 0 auto;
}

.notification-card {
  border: 2px solid #f39c12;
  background: linear-gradient(135deg, #fff9e6, #ffffff);
}

.notification-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  text-align: left;
}

.notification-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.notification-text {
  flex: 1;
}

.notification-text h4 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.notification-text p {
  margin: 0;
  color: #6c757d;
  font-size: 0.9rem;
}

.background-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 1;
}

.decoration-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(245, 245, 220, 0.1);
  animation: float 8s ease-in-out infinite;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -150px;
  right: -150px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  bottom: -100px;
  left: -100px;
  animation-delay: 2s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  top: 20%;
  left: 10%;
  animation-delay: 4s;
}

.circle-4 {
  width: 100px;
  height: 100px;
  bottom: 20%;
  right: 10%;
  animation-delay: 6s;
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
  0% {
    transform: translate(-50%, -50%) scale(0.8);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(1.2);
    opacity: 0;
  }
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .coming-soon-page {
    padding: 1rem;
  }
  
  .content-section {
    padding: 2rem;
  }
  
  .coming-soon-title {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .action-section {
    flex-direction: column;
    align-items: center;
  }
  
  .notification-content {
    flex-direction: column;
    text-align: center;
  }
  
  .timeline-content {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .coming-soon-title {
    font-size: 1.75rem;
  }
  
  .main-icon {
    font-size: 4rem;
  }
  
  .pulse-ring {
    width: 80px;
    height: 80px;
  }
  
  .decoration-circle {
    display: none;
  }
}
</style>
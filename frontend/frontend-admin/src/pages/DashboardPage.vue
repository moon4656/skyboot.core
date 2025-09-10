<template>
  <div class="dashboard-container">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <h1 class="page-title">대시보드</h1>
      <p class="page-subtitle">시스템 현황을 한눈에 확인하세요</p>
    </div>

    <!-- 통계 카드 -->
    <div class="stats-grid">
      <va-card
        v-for="stat in stats"
        :key="stat.title"
        class="stat-card"
        :color="stat.color"
        stripe
      >
        <va-card-content>
          <div class="stat-content">
            <div class="stat-icon">
              <va-icon :name="stat.icon" size="2rem" />
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ stat.value || 'No Title1'}}</h3> 
              <p class="stat-title">{{ stat.title || 'No Title2' }}</p>
              <div class="stat-change" :class="stat.changeType">
                <va-icon :name="stat.changeIcon" size="small" />
                <span>{{ stat.change }}</span>
              </div>
            </div>
          </div>
        </va-card-content>
      </va-card>
    </div>

    <!-- 차트 및 활동 로그 -->
    <div class="content-grid">
      <!-- 사용자 활동 차트 -->
      <va-card class="chart-card">
        <va-card-title>사용자 활동</va-card-title>
        <va-card-content>
          <div class="chart-container">
            <canvas ref="activityChartRef" width="400" height="200"></canvas>
          </div>
        </va-card-content>
      </va-card>

      <!-- 최근 활동 로그 -->
      <va-card class="activity-card">
        <va-card-title>
          <div class="card-title-with-action">
            <span>최근 활동</span>
            <va-button preset="secondary" size="small" @click="refreshActivities">
              <va-icon name="refresh" />
              새로고침
            </va-button>
          </div>
        </va-card-title>
        <va-card-content>
          <div class="activity-list">
            <div
              v-for="activity in recentActivities"
              :key="activity.id"
              class="activity-item"
            >
              <div class="activity-avatar">
                <va-avatar :color="activity.color" size="small">
                  <va-icon :name="activity.icon" />
                </va-avatar>
              </div>
              <div class="activity-content">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ formatTime(activity.time) }}</span>
              </div>
            </div>
          </div>
        </va-card-content>
      </va-card>
    </div>

    <!-- 시스템 상태 -->
    <va-card class="system-status-card">
      <va-card-title>시스템 상태</va-card-title>
      <va-card-content>
        <div class="status-grid">
          <div
            v-for="status in systemStatus"
            :key="status.name"
            class="status-item"
          >
            <div class="status-header">
              <span class="status-name">{{ status.name }}</span>
              <va-badge
                :color="status.status === 'healthy' ? 'success' : status.status === 'warning' ? 'warning' : 'danger'"
                :text="status.statusText"
              />
            </div>
            <va-progress-bar
              :model-value="status.value"
              :color="status.status === 'healthy' ? 'success' : status.status === 'warning' ? 'warning' : 'danger'"
              class="mt-2"
            />
            <div class="status-details">
              <span>{{ status.value }}% 사용 중</span>
              <span>{{ status.details }}</span>
            </div>
          </div>
        </div>
      </va-card-content>
    </va-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'

interface Stat {
  title: string
  value: string
  icon: string
  color: string
  change: string
  changeType: 'positive' | 'negative' | 'neutral'
  changeIcon: string
}

interface Activity {
  id: number
  text: string
  time: Date
  icon: string
  color: string
}

interface SystemStatus {
  name: string
  value: number
  status: 'healthy' | 'warning' | 'critical'
  statusText: string
  details: string
}

const authStore = useAuthStore()
const activityChartRef = ref<HTMLCanvasElement>()

// 통계 데이터
const stats = ref<Stat[]>([
  {
    title: '총 사용자',
    value: '1,234',
    icon: 'people',
    color: 'primary',
    change: '+12%',
    changeType: 'positive',
    changeIcon: 'trending_up'
  },
  {
    title: '활성 세션',
    value: '89',
    icon: 'computer',
    color: 'success',
    change: '+5%',
    changeType: 'positive',
    changeIcon: 'trending_up'
  },
  {
    title: '오늘 로그인',
    value: '456',
    icon: 'login',
    color: 'info',
    change: '-3%',
    changeType: 'negative',
    changeIcon: 'trending_down'
  },
  {
    title: '시스템 상태',
    value: '정상',
    icon: 'check_circle',
    color: 'success',
    change: '안정',
    changeType: 'neutral',
    changeIcon: 'check'
  }
])

// 최근 활동
const recentActivities = ref<Activity[]>([
  {
    id: 1,
    text: '관리자가 새로운 사용자를 생성했습니다.',
    time: new Date(Date.now() - 5 * 60 * 1000),
    icon: 'person_add',
    color: 'primary'
  },
  {
    id: 2,
    text: '시스템 백업이 완료되었습니다.',
    time: new Date(Date.now() - 15 * 60 * 1000),
    icon: 'backup',
    color: 'success'
  },
  {
    id: 3,
    text: '새로운 게시글이 등록되었습니다.',
    time: new Date(Date.now() - 30 * 60 * 1000),
    icon: 'article',
    color: 'info'
  },
  {
    id: 4,
    text: '사용자 권한이 업데이트되었습니다.',
    time: new Date(Date.now() - 45 * 60 * 1000),
    icon: 'security',
    color: 'warning'
  },
  {
    id: 5,
    text: '데이터베이스 최적화가 실행되었습니다.',
    time: new Date(Date.now() - 60 * 60 * 1000),
    icon: 'storage',
    color: 'secondary'
  }
])

// 시스템 상태
const systemStatus = ref<SystemStatus[]>([
  {
    name: 'CPU 사용률',
    value: 45,
    status: 'healthy',
    statusText: '정상',
    details: '4 cores'
  },
  {
    name: '메모리 사용률',
    value: 72,
    status: 'warning',
    statusText: '주의',
    details: '8GB / 16GB'
  },
  {
    name: '디스크 사용률',
    value: 35,
    status: 'healthy',
    statusText: '정상',
    details: '350GB / 1TB'
  },
  {
    name: '네트워크',
    value: 20,
    status: 'healthy',
    statusText: '정상',
    details: '100Mbps'
  }
])

// 현재 사용자 정보
const currentUser = computed(() => authStore.user)

// 시간 포맷팅
const formatTime = (time: Date): string => {
  const now = new Date()
  const diff = now.getTime() - time.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return '방금 전'
  if (minutes < 60) return `${minutes}분 전`
  if (hours < 24) return `${hours}시간 전`
  return `${days}일 전`
}

// 활동 새로고침
const refreshActivities = async () => {
  // 실제 구현에서는 API 호출
  console.log('활동 로그 새로고침')
}

// 차트 초기화
const initChart = () => {
  if (!activityChartRef.value) return

  const ctx = activityChartRef.value.getContext('2d')
  if (!ctx) return

  // 간단한 차트 그리기 (실제로는 Chart.js 등 사용)
  ctx.fillStyle = '#3b82f6'
  ctx.fillRect(50, 150, 30, 50)
  ctx.fillRect(100, 120, 30, 80)
  ctx.fillRect(150, 100, 30, 100)
  ctx.fillRect(200, 80, 30, 120)
  ctx.fillRect(250, 60, 30, 140)
  ctx.fillRect(300, 90, 30, 110)

  // 라벨
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px Arial'
  ctx.fillText('월', 60, 220)
  ctx.fillText('화', 110, 220)
  ctx.fillText('수', 160, 220)
  ctx.fillText('목', 210, 220)
  ctx.fillText('금', 260, 220)
  ctx.fillText('토', 310, 220)
}

// 컴포넌트 마운트
onMounted(() => {
  initChart()
})
</script>

<style scoped>
.dashboard-container {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  color: var(--va-text-primary);
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: var(--va-text-secondary);
  font-size: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.stat-title {
  color: var(--va-text-secondary);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.stat-change.positive {
  color: var(--va-success);
}

.stat-change.negative {
  color: var(--va-danger);
}

.stat-change.neutral {
  color: var(--va-text-secondary);
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  min-height: 300px;
}

.chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 250px;
}

.activity-card {
  min-height: 300px;
}

.card-title-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.activity-list {
  max-height: 250px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--va-background-border);
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-avatar {
  flex-shrink: 0;
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.875rem;
  margin-bottom: 0.25rem;
}

.activity-time {
  font-size: 0.75rem;
  color: var(--va-text-secondary);
}

.system-status-card {
  margin-bottom: 2rem;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.status-item {
  padding: 1rem;
  border: 1px solid var(--va-background-border);
  border-radius: 0.5rem;
  background: var(--va-background-secondary);
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.status-name {
  font-weight: 500;
}

.status-details {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--va-text-secondary);
  margin-top: 0.5rem;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .status-grid {
    grid-template-columns: 1fr;
  }
}
</style>
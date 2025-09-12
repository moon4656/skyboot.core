<template>
  <div class="dashboard">
    <!-- 대시보드 헤더 -->
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="dashboard-title">
          <va-icon name="dashboard" class="title-icon" />
          대시보드
        </h1>
        <p class="dashboard-subtitle">
          {{ currentUser?.username }}님, 환영합니다! 시스템 현황을 확인하세요.
        </p>
      </div>
      <div class="header-actions">
        <va-button
          preset="secondary"
          icon="refresh"
          @click="refreshData"
          :loading="loading"
        >
          새로고침
        </va-button>
      </div>
    </div>

    <!-- 통계 카드 섹션 -->
    <div class="stats-grid">
      <va-card
        v-for="stat in stats"
        :key="stat.id"
        class="stat-card"
        :class="`stat-card--${stat.color}`"
      >
        <va-card-content>
          <div class="stat-content">
            <div class="stat-icon">
              <va-icon :name="stat.icon" size="2rem" :color="stat.color" />
            </div>
            <div class="stat-info">
              <h3 class="stat-value">{{ stat.value }}</h3>
              <p class="stat-label">{{ stat.label }}</p>
              <div class="stat-change" :class="stat.changeType">
                <va-icon 
                  :name="stat.changeType === 'increase' ? 'trending_up' : 'trending_down'"
                  size="small"
                />
                <span>{{ stat.change }}</span>
              </div>
            </div>
          </div>
        </va-card-content>
      </va-card>
    </div>

    <!-- 차트 및 활동 섹션 -->
    <div class="dashboard-content">
      <div class="content-grid">
        <!-- 활동 차트 -->
        <va-card class="chart-card">
          <va-card-title>
            <va-icon name="bar_chart" class="mr-2" />
            시스템 활동
          </va-card-title>
          <va-card-content>
            <div class="chart-placeholder">
              <va-icon name="insert_chart" size="4rem" color="secondary" />
              <p class="chart-message">차트 데이터를 로딩 중...</p>
              <va-progress-circle indeterminate size="small" />
            </div>
          </va-card-content>
        </va-card>

        <!-- 최근 활동 -->
        <va-card class="activity-card">
          <va-card-title>
            <va-icon name="history" class="mr-2" />
            최근 활동
          </va-card-title>
          <va-card-content>
            <div class="activity-list">
              <div
                v-for="activity in recentActivities"
                :key="activity.id"
                class="activity-item"
              >
                <div class="activity-icon">
                  <va-icon :name="activity.icon" :color="activity.color" />
                </div>
                <div class="activity-content">
                  <p class="activity-text">{{ activity.user }} - {{ activity.action }}</p>
                  <span class="activity-time">{{ activity.time }}</span>
                </div>
              </div>
            </div>
          </va-card-content>
        </va-card>
      </div>
    </div>

    <!-- 빠른 액션 섹션 -->
    <div class="quick-actions">
      <va-card>
        <va-card-title>
          <va-icon name="flash_on" class="mr-2" />
          빠른 작업
        </va-card-title>
        <va-card-content>
          <div class="actions-grid">
            <va-button
              v-for="action in quickActions"
              :key="action.id"
              :preset="action.preset"
              :icon="action.icon"
              @click="handleQuickAction(action)"
              class="action-button"
            >
              {{ action.label }}
            </va-button>
          </div>
        </va-card-content>
      </va-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { dashboardApi, type DashboardSummary } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// 반응형 데이터
const loading = ref(false)

// 현재 사용자 정보
const currentUser = computed(() => authStore.user)

// 대시보드 데이터
const dashboardData = ref<DashboardSummary | null>(null)

// 통계 데이터 (computed로 변경)
const stats = computed(() => {
  if (!dashboardData.value) {
    return [
      {
        id: 1,
        label: '총 사용자',
        value: '로딩중...',
        change: '',
        changeType: 'increase',
        icon: 'people',
        color: 'primary'
      },
      {
        id: 2,
        label: '활성 사용자',
        value: '로딩중...',
        change: '',
        changeType: 'increase',
        icon: 'computer',
        color: 'success'
      },
      {
        id: 3,
        label: '오늘 요청수',
        value: '로딩중...',
        change: '',
        changeType: 'increase',
        icon: 'visibility',
        color: 'info'
      },
      {
        id: 4,
        label: '오류 요청수',
        value: '로딩중...',
        change: '',
        changeType: 'increase',
        icon: 'error',
        color: 'warning'
      }
    ]
  }
  
  // 백엔드 응답 구조에 맞게 직접 접근
  const data = dashboardData.value
  return [
    {
      id: 1,
      label: '총 사용자',
      value: data?.total_users?.toLocaleString() || '0',
      change: '+12%',
      changeType: 'increase',
      icon: 'people',
      color: 'primary'
    },
    {
      id: 2,
      label: '활성 사용자',
      value: data?.active_users_today?.toString() || '0',
      change: '+5%',
      changeType: 'increase',
      icon: 'computer',
      color: 'success'
    },
    {
      id: 3,
      label: '오늘 요청수',
      value: data?.total_requests_today?.toLocaleString() || '0',
      change: '+8%',
      changeType: 'increase',
      icon: 'visibility',
      color: 'info'
    },
    {
      id: 4,
      label: '오류 요청수',
      value: data?.error_requests_today?.toString() || '0',
      change: data?.error_requests_today === 0 ? '0%' : '+' + ((data?.error_requests_today || 0) / (data?.total_requests_today || 1) * 100).toFixed(1) + '%',
      changeType: (data?.error_requests_today || 0) === 0 ? 'increase' : 'decrease',
      icon: 'error',
      color: (data?.error_requests_today || 0) === 0 ? 'success' : 'warning'
    }
  ]
})

// 최근 활동 데이터 (computed로 변경)
const recentActivities = computed(() => {
  if (!dashboardData.value || !dashboardData.value.recent_activities) {
    return [
      {
        id: 1,
        user: '로딩중...',
        action: '로딩중...',
        time: '로딩중...',
        icon: 'hourglass_empty',
        color: 'info'
      }
    ]
  }
  
  return dashboardData.value.recent_activities.map((activity, index) => ({
    id: index + 1,
    user: activity.user_name || '알 수 없음',
    action: `${activity.menu_name} - ${activity.action}`,
    time: activity.timestamp ? new Date(activity.timestamp).toLocaleString('ko-KR') : '알 수 없음',
    icon: activity.icon || 'info',
    color: activity.color || 'primary'
  }))
})

// 빠른 액션 데이터
const quickActions = ref([
  {
    id: 1,
    label: '사용자 추가',
    icon: 'person_add',
    preset: 'primary',
    route: '/admin/users'
  },
  {
    id: 2,
    label: '게시글 작성',
    icon: 'edit',
    preset: 'secondary',
    route: '/admin/boards'
  },
  {
    id: 3,
    label: '시스템 설정',
    icon: 'settings',
    preset: 'plain',
    route: '/admin/settings'
  },
  {
    id: 4,
    label: '로그 확인',
    icon: 'description',
    preset: 'plain',
    route: '/admin/logs'
  }
])

// 대시보드 데이터 로드
const loadDashboardData = async () => {
  loading.value = true
  try {
    const response = await dashboardApi.getDashboardSummary()
    dashboardData.value = response
    console.log('대시보드 데이터 로드 완료:', response)
  } catch (error) {
    console.error('대시보드 데이터 로드 실패:', error)
    // 에러 발생 시 기본 데이터 설정
    dashboardData.value = {
      stats: {
        total_users: 0,
        active_sessions: 0,
        today_visitors: 0,
        system_status: '확인 중'
      },
      recent_activities: [],
      system_health: {
        status: '확인 중',
        uptime: '0',
        memory_usage: 0,
        cpu_usage: 0
      }
    }
  } finally {
    loading.value = false
  }
}

// 메서드
const refreshData = async () => {
  await loadDashboardData()
}

const handleQuickAction = (action: any) => {
  if (action.route) {
    router.push(action.route)
  }
}

// 라이프사이클
onMounted(() => {
  console.log('대시보드 로드됨')
  loadDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  min-height: 100%;
  background: #f8f9fa;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.header-content {
  flex: 1;
}

.dashboard-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-icon {
  color: #3498db;
}

.dashboard-subtitle {
  color: #6c757d;
  font-size: 1rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border-left: 4px solid transparent;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.stat-card--primary {
  border-left-color: #3498db;
}

.stat-card--success {
  border-left-color: #27ae60;
}

.stat-card--info {
  border-left-color: #17a2b8;
}

.stat-card--warning {
  border-left-color: #f39c12;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  padding: 1rem;
  border-radius: 12px;
  background: rgba(52, 152, 219, 0.1);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
}

.stat-label {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0 0 0.5rem 0;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8rem;
  font-weight: 600;
}

.stat-change.increase {
  color: #27ae60;
}

.stat-change.decrease {
  color: #e74c3c;
}

.dashboard-content {
  margin-bottom: 2rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
}

.chart-card,
.activity-card {
  height: 400px;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #6c757d;
  gap: 1rem;
}

.chart-message {
  font-size: 1rem;
  margin: 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: 8px;
  background: #f8f9fa;
  transition: background-color 0.2s ease;
}

.activity-item:hover {
  background: #e9ecef;
}

.activity-icon {
  padding: 0.5rem;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.activity-content {
  flex: 1;
}

.activity-text {
  font-size: 0.9rem;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.activity-time {
  font-size: 0.8rem;
  color: #6c757d;
}

.quick-actions {
  margin-bottom: 2rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-button {
  height: 60px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* 반응형 디자인 */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card,
  .activity-card {
    height: auto;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .activity-item {
    flex-direction: column;
    text-align: center;
  }
}

/* 스크롤바 스타일링 */
.activity-list::-webkit-scrollbar {
  width: 6px;
}

.activity-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.activity-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.activity-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
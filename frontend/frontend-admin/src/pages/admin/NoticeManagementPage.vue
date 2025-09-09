<template>
  <div class="notice-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="campaign" class="mr-2" />
            공지사항 관리
          </h1>
          <p class="page-description">
            중요한 공지사항을 작성하고 관리합니다. 사용자에게 전달할 중요한 정보를 게시할 수 있습니다.
          </p>
        </div>
        
        <div class="header-actions">
          <VaButton
            preset="secondary"
            icon="refresh"
            @click="loadNotices"
            :loading="loading"
          >
            새로고침
          </VaButton>
          
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            공지사항 작성
          </VaButton>
        </div>
      </div>
    </div>
    
    <!-- 필터 및 검색 -->
    <VaCard class="filter-card">
      <VaCardContent>
        <div class="filter-section">
          <div class="filter-row">
            <div class="filter-item">
              <VaInput
                v-model="filters.search"
                placeholder="제목, 내용 검색..."
                clearable
                class="search-input"
              >
                <template #prependInner>
                  <VaIcon name="search" />
                </template>
              </VaInput>
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="filters.category"
                :options="categoryOptions"
                placeholder="카테고리 선택"
                clearable
                class="category-select"
              />
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="filters.priority"
                :options="priorityOptions"
                placeholder="우선순위 선택"
                clearable
                class="priority-select"
              />
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="filters.status"
                :options="statusOptions"
                placeholder="상태 선택"
                clearable
                class="status-select"
              />
            </div>
            
            <div class="filter-item">
              <VaDateInput
                v-model="filters.dateRange"
                mode="range"
                placeholder="작성일 범위"
                clearable
                class="date-range"
              />
            </div>
            
            <div class="filter-actions">
              <VaButton
                preset="secondary"
                icon="clear"
                @click="resetFilters"
              >
                초기화
              </VaButton>
            </div>
          </div>
        </div>
      </VaCardContent>
    </VaCard>
    
    <!-- 공지사항 목록 -->
    <VaCard class="notices-card">
      <VaCardContent>
        <div class="notices-header">
          <div class="notices-info">
            <span class="total-count">총 {{ totalNotices }}개 공지사항</span>
            <span class="published-count">게시 중 {{ publishedNotices }}개</span>
          </div>
          
          <div class="notices-actions">
            <VaButton
              preset="secondary"
              icon="download"
              @click="exportNotices"
            >
              내보내기
            </VaButton>
            
            <VaButton
              preset="secondary"
              icon="publish"
              @click="bulkPublish"
              :disabled="selectedNotices.length === 0"
            >
              일괄 게시
            </VaButton>
            
            <VaButton
              preset="secondary"
              icon="unpublished_with_notes"
              @click="bulkUnpublish"
              :disabled="selectedNotices.length === 0"
            >
              일괄 비게시
            </VaButton>
          </div>
        </div>
        
        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <VaProgressCircular indeterminate />
          <span class="loading-text">공지사항 목록을 불러오는 중...</span>
        </div>
        
        <!-- 빈 상태 -->
        <div v-else-if="filteredNotices.length === 0" class="empty-state">
          <VaIcon name="campaign" size="4rem" color="secondary" />
          <h3>공지사항이 없습니다</h3>
          <p>새로운 공지사항을 작성해보세요.</p>
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            공지사항 작성
          </VaButton>
        </div>
        
        <!-- 공지사항 테이블 -->
        <VaDataTable
          v-else
          v-model:selected="selectedNotices"
          :items="paginatedNotices"
          :columns="tableColumns"
          :loading="loading"
          selectable
          striped
          hoverable
          class="notices-table"
        >
          <template #cell(priority)="{ rowData }">
            <VaChip
              :color="getPriorityColor(rowData.priority)"
              size="small"
              outline
            >
              {{ getPriorityLabel(rowData.priority) }}
            </VaChip>
          </template>
          
          <template #cell(title)="{ rowData }">
            <div class="notice-title-cell">
              <div class="title-content">
                <VaIcon
                  v-if="rowData.is_pinned"
                  name="push_pin"
                  color="warning"
                  size="0.875rem"
                  class="pin-icon"
                />
                
                <span class="title">{{ rowData.title }}</span>
                
                <VaChip
                  v-if="rowData.is_urgent"
                  color="danger"
                  size="small"
                  outline
                >
                  긴급
                </VaChip>
              </div>
              
              <div class="title-meta">
                <span class="category">{{ getCategoryLabel(rowData.category) }}</span>
                <span class="views">조회 {{ formatNumber(rowData.view_count) }}</span>
              </div>
            </div>
          </template>
          
          <template #cell(author)="{ rowData }">
            <div class="author-cell">
              <VaAvatar
                :src="rowData.author.avatar"
                :fallback-text="rowData.author.name"
                size="small"
              />
              <span class="author-name">{{ rowData.author.name }}</span>
            </div>
          </template>
          
          <template #cell(publish_date)="{ rowData }">
            <div class="date-cell">
              <span class="date">{{ formatDate(rowData.publish_date) }}</span>
              <span v-if="rowData.end_date" class="end-date">
                ~ {{ formatDate(rowData.end_date) }}
              </span>
            </div>
          </template>
          
          <template #cell(status)="{ rowData }">
            <VaChip
              :color="getStatusColor(rowData.status)"
              size="small"
              outline
            >
              {{ getStatusLabel(rowData.status) }}
            </VaChip>
          </template>
          
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <VaButton
                preset="secondary"
                size="small"
                icon="visibility"
                @click="previewNotice(rowData)"
                title="미리보기"
              />
              
              <VaButton
                preset="secondary"
                size="small"
                icon="edit"
                @click="editNotice(rowData)"
                title="수정"
              />
              
              <VaButton
                preset="secondary"
                size="small"
                :icon="rowData.status === 'published' ? 'unpublished_with_notes' : 'publish'"
                @click="toggleNoticeStatus(rowData)"
                :title="rowData.status === 'published' ? '비게시' : '게시'"
              />
              
              <VaButton
                preset="secondary"
                color="danger"
                size="small"
                icon="delete"
                @click="deleteNotice(rowData)"
                title="삭제"
              />
            </div>
          </template>
        </VaDataTable>
        
        <!-- 페이지네이션 -->
        <div v-if="totalPages > 1" class="pagination-container">
          <VaPagination
            v-model="currentPage"
            :pages="totalPages"
            :visible-pages="5"
            buttons-preset="secondary"
          />
        </div>
      </VaCardContent>
    </VaCard>
    
    <!-- 공지사항 작성/수정 모달 -->
    <VaModal
      v-model="modals.notice"
      :title="noticeForm.id ? '공지사항 수정' : '공지사항 작성'"
      size="large"
      @ok="saveNotice"
      @cancel="closeNoticeModal"
    >
      <VaForm ref="noticeFormRef" @submit.prevent="saveNotice">
        <div class="form-grid">
          <div class="form-row">
            <VaInput
              v-model="noticeForm.title"
              label="제목"
              placeholder="공지사항 제목을 입력하세요"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="noticeForm.category"
              label="카테고리"
              :options="categoryOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="noticeForm.priority"
              label="우선순위"
              :options="priorityOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaTextarea
              v-model="noticeForm.content"
              label="내용"
              placeholder="공지사항 내용을 입력하세요"
              :min-rows="8"
              :max-rows="15"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-section">
            <h4 class="section-title">게시 설정</h4>
            
            <div class="publish-settings">
              <div class="date-row">
                <VaDateInput
                  v-model="noticeForm.publish_date"
                  label="게시 시작일"
                  :rules="[required]"
                  required
                />
                
                <VaDateInput
                  v-model="noticeForm.end_date"
                  label="게시 종료일 (선택)"
                  clearable
                />
              </div>
              
              <div class="options-row">
                <VaCheckbox
                  v-model="noticeForm.is_pinned"
                  label="상단 고정"
                />
                
                <VaCheckbox
                  v-model="noticeForm.is_urgent"
                  label="긴급 공지"
                />
                
                <VaCheckbox
                  v-model="noticeForm.allow_comments"
                  label="댓글 허용"
                />
                
                <VaCheckbox
                  v-model="noticeForm.send_notification"
                  label="알림 발송"
                />
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h4 class="section-title">대상 설정</h4>
            
            <div class="target-settings">
              <VaSelect
                v-model="noticeForm.target_type"
                label="대상 유형"
                :options="targetTypeOptions"
                :rules="[required]"
                required
              />
              
              <VaSelect
                v-if="noticeForm.target_type === 'specific'"
                v-model="noticeForm.target_groups"
                label="대상 그룹"
                :options="groupOptions"
                multiple
                searchable
              />
            </div>
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="noticeForm.status"
              label="상태"
              :options="statusOptions"
              :rules="[required]"
              required
            />
          </div>
        </div>
      </VaForm>
    </VaModal>
    
    <!-- 공지사항 미리보기 모달 -->
    <VaModal
      v-model="modals.preview"
      title="공지사항 미리보기"
      size="large"
      hide-default-actions
    >
      <div v-if="previewNoticeData" class="notice-preview">
        <div class="preview-header">
          <div class="preview-meta">
            <VaChip
              :color="getCategoryColor(previewNoticeData.category)"
              size="small"
              outline
            >
              {{ getCategoryLabel(previewNoticeData.category) }}
            </VaChip>
            
            <VaChip
              :color="getPriorityColor(previewNoticeData.priority)"
              size="small"
              outline
            >
              {{ getPriorityLabel(previewNoticeData.priority) }}
            </VaChip>
            
            <VaChip
              v-if="previewNoticeData.is_urgent"
              color="danger"
              size="small"
              outline
            >
              긴급
            </VaChip>
          </div>
          
          <h2 class="preview-title">
            <VaIcon
              v-if="previewNoticeData.is_pinned"
              name="push_pin"
              color="warning"
              class="mr-2"
            />
            {{ previewNoticeData.title }}
          </h2>
          
          <div class="preview-info">
            <div class="author-info">
              <VaAvatar
                :src="previewNoticeData.author.avatar"
                :fallback-text="previewNoticeData.author.name"
                size="small"
              />
              <span class="author-name">{{ previewNoticeData.author.name }}</span>
            </div>
            
            <div class="date-info">
              <span>{{ formatDate(previewNoticeData.publish_date) }}</span>
              <span class="views">조회 {{ formatNumber(previewNoticeData.view_count) }}</span>
            </div>
          </div>
        </div>
        
        <div class="preview-content">
          <div class="content-text" v-html="formatContent(previewNoticeData.content)"></div>
        </div>
        
        <div class="preview-footer">
          <div class="footer-actions">
            <VaButton
              preset="secondary"
              icon="edit"
              @click="editNoticeFromPreview"
            >
              수정
            </VaButton>
            
            <VaButton
              preset="secondary"
              icon="close"
              @click="modals.preview = false"
            >
              닫기
            </VaButton>
          </div>
        </div>
      </div>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vuestic-ui';
import type { Notice } from '../../types/auth';

// 컴포저블
const { init: initToast } = useToast();

// 상태 관리
const loading = ref(false);
const notices = ref<Notice[]>([]);
const selectedNotices = ref<Notice[]>([]);
const currentPage = ref(1);
const itemsPerPage = ref(10);
const previewNoticeData = ref<Notice | null>(null);

// 필터 상태
const filters = ref({
  search: '',
  category: null as string | null,
  priority: null as string | null,
  status: null as string | null,
  dateRange: null as [Date, Date] | null,
});

// 모달 상태
const modals = ref({
  notice: false,
  preview: false,
});

// 폼 상태
const noticeForm = ref({
  id: null as number | null,
  title: '',
  content: '',
  category: 'general',
  priority: 'normal' as 'low' | 'normal' | 'high' | 'urgent',
  publish_date: new Date(),
  end_date: null as Date | null,
  is_pinned: false,
  is_urgent: false,
  allow_comments: true,
  send_notification: false,
  target_type: 'all' as 'all' | 'specific' | 'admin',
  target_groups: [] as string[],
  status: 'draft' as 'draft' | 'published' | 'archived' | 'expired' | 'unpublished',
});

// 폼 참조
const noticeFormRef = ref();

// 옵션 데이터
const categoryOptions = [
  { text: '일반 공지', value: 'general' },
  { text: '시스템 점검', value: 'maintenance' },
  { text: '업데이트', value: 'update' },
  { text: '이벤트', value: 'event' },
  { text: '정책 변경', value: 'policy' },
  { text: '긴급 공지', value: 'urgent' },
];

const priorityOptions = [
  { text: '낮음', value: 'low' },
  { text: '보통', value: 'normal' },
  { text: '높음', value: 'high' },
  { text: '긴급', value: 'urgent' },
];

const statusOptions = [
  { text: '임시저장', value: 'draft' },
  { text: '게시 중', value: 'published' },
  { text: '게시 종료', value: 'expired' },
  { text: '비게시', value: 'unpublished' },
];

const targetTypeOptions = [
  { text: '전체 사용자', value: 'all' },
  { text: '특정 그룹', value: 'specific' },
  { text: '관리자만', value: 'admin' },
];

const groupOptions = [
  { text: '일반 사용자', value: 'users' },
  { text: '프리미엄 사용자', value: 'premium' },
  { text: '관리자', value: 'admin' },
  { text: '개발팀', value: 'dev' },
];

// 테이블 컬럼
const tableColumns = [
  { key: 'priority', label: '우선순위', width: '100px' },
  { key: 'title', label: '제목', sortable: true },
  { key: 'author', label: '작성자', width: '120px' },
  { key: 'publish_date', label: '게시일', sortable: true, width: '150px' },
  { key: 'status', label: '상태', sortable: true, width: '100px' },
  { key: 'actions', label: '작업', width: '160px' },
];

// 계산된 속성
const filteredNotices = computed(() => {
  let result = [...notices.value];
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    result = result.filter(notice => 
      notice.title.toLowerCase().includes(search) ||
      notice.content.toLowerCase().includes(search)
    );
  }
  
  if (filters.value.category) {
    result = result.filter(notice => notice.category === filters.value.category);
  }
  
  if (filters.value.priority) {
    result = result.filter(notice => notice.priority === filters.value.priority);
  }
  
  if (filters.value.status) {
    result = result.filter(notice => notice.status === filters.value.status);
  }
  
  if (filters.value.dateRange) {
    const [startDate, endDate] = filters.value.dateRange;
    result = result.filter(notice => {
      const publishDate = new Date(notice.publish_date);
      return publishDate >= startDate && publishDate <= endDate;
    });
  }
  
  // 우선순위 정렬 (고정 > 긴급 > 높음 > 보통 > 낮음)
  result.sort((a, b) => {
    if (a.is_pinned !== b.is_pinned) {
      return a.is_pinned ? -1 : 1;
    }
    
    const priorityOrder = { urgent: 4, high: 3, normal: 2, low: 1 };
    const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder] || 0;
    const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder] || 0;
    
    if (aPriority !== bPriority) {
      return bPriority - aPriority;
    }
    
    return new Date(b.publish_date).getTime() - new Date(a.publish_date).getTime();
  });
  
  return result;
});

const totalNotices = computed(() => notices.value.length);

const publishedNotices = computed(() => {
  return notices.value.filter(notice => notice.status === 'published').length;
});

const totalPages = computed(() => {
  return Math.ceil(filteredNotices.value.length / itemsPerPage.value);
});

const paginatedNotices = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredNotices.value.slice(start, end);
});

// 유틸리티 함수
const getCategoryLabel = (category: string): string => {
  const labelMap: Record<string, string> = {
    general: '일반 공지',
    maintenance: '시스템 점검',
    update: '업데이트',
    event: '이벤트',
    policy: '정책 변경',
    urgent: '긴급 공지',
  };
  return labelMap[category] || category;
};

const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    general: 'primary',
    maintenance: 'warning',
    update: 'info',
    event: 'success',
    policy: 'secondary',
    urgent: 'danger',
  };
  return colorMap[category] || 'secondary';
};

const getPriorityLabel = (priority: string): string => {
  const labelMap: Record<string, string> = {
    low: '낮음',
    normal: '보통',
    high: '높음',
    urgent: '긴급',
  };
  return labelMap[priority] || priority;
};

const getPriorityColor = (priority: string): string => {
  const colorMap: Record<string, string> = {
    low: 'secondary',
    normal: 'primary',
    high: 'warning',
    urgent: 'danger',
  };
  return colorMap[priority] || 'secondary';
};

const getStatusLabel = (status: string): string => {
  const labelMap: Record<string, string> = {
    draft: '임시저장',
    published: '게시 중',
    expired: '게시 종료',
    unpublished: '비게시',
  };
  return labelMap[status] || status;
};

const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    draft: 'secondary',
    published: 'success',
    expired: 'warning',
    unpublished: 'danger',
  };
  return colorMap[status] || 'secondary';
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
};

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

const formatContent = (content: string): string => {
  return content.replace(/\n/g, '<br>');
};

// 검증 규칙
const required = (value: string | number | Date) => !!value || '필수 입력 항목입니다.';

// 메서드
const loadNotices = async () => {
  try {
    loading.value = true;
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    notices.value = [
      {
        id: 1,
        title: '시스템 정기 점검 안내',
        content: '안녕하세요.\n\n시스템 정기 점검으로 인해 서비스가 일시 중단됩니다.\n\n점검 일시: 2024년 1월 15일 오전 2시 ~ 6시\n점검 내용: 서버 업그레이드 및 보안 패치\n\n이용에 불편을 드려 죄송합니다.',
        type: 'warning',
        category: 'maintenance',
        priority: 'high',
        is_active: true,
        publish_date: '2024-01-10T00:00:00Z',
        end_date: '2024-01-20T00:00:00Z',
        is_pinned: true,
        is_urgent: false,
        allow_comments: false,
        send_notification: true,
        target_type: 'all',
        target_groups: [],
        status: 'published',
        view_count: 1250,
        author: {
          id: 1,
          name: '관리자',
          avatar: '',
        },
        created_at: '2024-01-10T00:00:00Z',
        updated_at: '2024-01-10T00:00:00Z',
      },
      {
        id: 2,
        title: '새로운 기능 업데이트 안내',
        content: '새로운 기능이 추가되었습니다.\n\n주요 업데이트 내용:\n- 다크 모드 지원\n- 알림 기능 개선\n- 성능 최적화\n\n자세한 내용은 업데이트 노트를 확인해주세요.',
        type: 'info',
        category: 'update',
        priority: 'normal',
        is_active: true,
        publish_date: '2024-01-08T00:00:00Z',
        end_date: null,
        is_pinned: false,
        is_urgent: false,
        allow_comments: true,
        send_notification: false,
        target_type: 'all',
        target_groups: [],
        status: 'published',
        view_count: 890,
        author: {
          id: 2,
          name: '개발팀',
          avatar: '',
        },
        created_at: '2024-01-08T00:00:00Z',
        updated_at: '2024-01-08T00:00:00Z',
      },
      {
        id: 3,
        title: '신년 이벤트 안내',
        content: '새해를 맞이하여 특별 이벤트를 진행합니다.\n\n이벤트 기간: 2024년 1월 1일 ~ 1월 31일\n혜택: 프리미엄 기능 무료 체험\n\n많은 참여 부탁드립니다.',
        type: 'success',
        category: 'event',
        priority: 'normal',
        is_active: true,
        publish_date: '2024-01-01T00:00:00Z',
        end_date: '2024-01-31T00:00:00Z',
        is_pinned: false,
        is_urgent: false,
        allow_comments: true,
        send_notification: true,
        target_type: 'all',
        target_groups: [],
        status: 'published',
        view_count: 2100,
        author: {
          id: 3,
          name: '마케팅팀',
          avatar: '',
        },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }
    ];
  } catch (error) {
    console.error('공지사항 목록 로드 실패:', error);
    initToast({
      message: '공지사항 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  resetNoticeForm();
  modals.value.notice = true;
};

const editNotice = (notice: Notice) => {
  noticeForm.value = {
    id: notice.id,
    title: notice.title,
    content: notice.content,
    category: notice.category,
    priority: notice.priority,
    publish_date: new Date(notice.publish_date),
    end_date: notice.end_date ? new Date(notice.end_date) : null,
    is_pinned: notice.is_pinned,
    is_urgent: notice.is_urgent,
    allow_comments: notice.allow_comments,
    send_notification: notice.send_notification,
    target_type: notice.target_type as 'all' | 'specific' | 'admin',
    target_groups: notice.target_groups,
    status: notice.status,
  };
  modals.value.notice = true;
};

const editNoticeFromPreview = () => {
  if (previewNoticeData.value) {
    editNotice(previewNoticeData.value);
    modals.value.preview = false;
  }
};

const previewNotice = (notice: Notice) => {
  previewNoticeData.value = notice;
  modals.value.preview = true;
};

const saveNotice = async () => {
  try {
    // 폼 검증
    if (!noticeFormRef.value?.validate()) {
      return;
    }
    
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const isEdit = !!noticeForm.value.id;
    
    if (isEdit) {
      // 수정
      const index = notices.value.findIndex(notice => notice.id === noticeForm.value.id);
      if (index !== -1) {
        notices.value[index] = {
          ...notices.value[index],
          ...noticeForm.value,
          publish_date: noticeForm.value.publish_date.toISOString(),
          end_date: noticeForm.value.end_date?.toISOString() || null,
          updated_at: new Date().toISOString(),
        };
      }
    } else {
      // 생성
      const newNotice: Notice = {
        ...noticeForm.value,
        id: Date.now(),
        type: 'info',
        priority: noticeForm.value.priority as 'low' | 'normal' | 'high' | 'urgent',
        is_active: true,
        publish_date: noticeForm.value.publish_date.toISOString(),
        end_date: noticeForm.value.end_date?.toISOString() || null,
        view_count: 0,
        author: {
          id: 1,
          name: '관리자',
          avatar: '',
        },
        status: noticeForm.value.status as 'draft' | 'published' | 'archived' | 'expired' | 'unpublished',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      notices.value.push(newNotice);
    }
    
    initToast({
      message: `공지사항이 성공적으로 ${isEdit ? '수정' : '작성'}되었습니다.`,
      color: 'success',
    });
    
    closeNoticeModal();
  } catch (error) {
    console.error('공지사항 저장 실패:', error);
    initToast({
      message: '공지사항 저장에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const toggleNoticeStatus = async (notice: Notice) => {
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = notices.value.findIndex(n => n.id === notice.id);
    if (index !== -1) {
      const newStatus = notice.status === 'published' ? 'unpublished' : 'published';
      notices.value[index].status = newStatus;
      notices.value[index].updated_at = new Date().toISOString();
    }
    
    initToast({
      message: `공지사항이 ${notice.status === 'published' ? '비게시' : '게시'}되었습니다.`,
      color: 'success',
    });
  } catch (error) {
    console.error('공지사항 상태 변경 실패:', error);
    initToast({
      message: '공지사항 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const deleteNotice = async (notice: Notice) => {
  if (!confirm(`'${notice.title}' 공지사항을 삭제하시겠습니까?`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = notices.value.findIndex(n => n.id === notice.id);
    if (index !== -1) {
      notices.value.splice(index, 1);
    }
    
    initToast({
      message: '공지사항이 삭제되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('공지사항 삭제 실패:', error);
    initToast({
      message: '공지사항 삭제에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const bulkPublish = async () => {
  if (selectedNotices.value.length === 0) return;
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    selectedNotices.value.forEach(selectedNotice => {
      const index = notices.value.findIndex(n => n.id === selectedNotice.id);
      if (index !== -1) {
        notices.value[index].status = 'published';
        notices.value[index].updated_at = new Date().toISOString();
      }
    });
    
    initToast({
      message: `${selectedNotices.value.length}개 공지사항이 게시되었습니다.`,
      color: 'success',
    });
    
    selectedNotices.value = [];
  } catch (error) {
    console.error('일괄 게시 실패:', error);
    initToast({
      message: '일괄 게시에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const bulkUnpublish = async () => {
  if (selectedNotices.value.length === 0) return;
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    selectedNotices.value.forEach(selectedNotice => {
      const index = notices.value.findIndex(n => n.id === selectedNotice.id);
      if (index !== -1) {
        notices.value[index].status = 'unpublished';
        notices.value[index].updated_at = new Date().toISOString();
      }
    });
    
    initToast({
      message: `${selectedNotices.value.length}개 공지사항이 비게시되었습니다.`,
      color: 'success',
    });
    
    selectedNotices.value = [];
  } catch (error) {
    console.error('일괄 비게시 실패:', error);
    initToast({
      message: '일괄 비게시에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const resetNoticeForm = () => {
  noticeForm.value = {
    id: null,
    title: '',
    content: '',
    category: '',
    priority: 'normal',
    publish_date: new Date(),
    end_date: null,
    is_pinned: false,
    is_urgent: false,
    allow_comments: true,
    send_notification: false,
    target_type: 'all',
    target_groups: [],
    status: 'draft',
  };
};

const closeNoticeModal = () => {
  modals.value.notice = false;
  resetNoticeForm();
};

const resetFilters = () => {
  filters.value = {
    search: '',
    category: null,
    priority: null,
    status: null,
    dateRange: null,
  };
};

const exportNotices = () => {
  // 공지사항 목록 내보내기 구현
  initToast({
    message: '공지사항 목록을 내보내는 기능은 준비 중입니다.',
    color: 'info',
  });
};

// 감시자
watch(() => filters.value, () => {
  currentPage.value = 1; // 필터 변경 시 첫 페이지로
}, { deep: true });

// 라이프사이클
onMounted(() => {
  loadNotices();
});
</script>

<style scoped>
.notice-management {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
}

.header-info {
  flex: 1;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
}

.page-description {
  color: #666;
  font-size: 1rem;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
}

.filter-card {
  margin-bottom: 1.5rem;
}

.filter-section {
  padding: 0.5rem 0;
}

.filter-row {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-item {
  flex: 1;
  min-width: 200px;
}

.search-input {
  min-width: 300px;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.notices-card {
  margin-bottom: 1.5rem;
}

.notices-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.notices-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.total-count,
.published-count {
  font-weight: 500;
  color: #666;
}

.notices-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.loading-text {
  color: #666;
  font-size: 0.875rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
  gap: 1rem;
}

.empty-state h3 {
  margin: 0;
  color: #666;
}

.empty-state p {
  margin: 0;
  color: #999;
}

.notices-table {
  margin-bottom: 2rem;
}

.notice-title-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.title-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pin-icon {
  flex-shrink: 0;
}

.title {
  font-weight: 600;
  flex: 1;
}

.title-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.category,
.views {
  font-size: 0.75rem;
}

.author-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.author-name {
  font-size: 0.875rem;
  font-weight: 500;
}

.date-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.date {
  font-weight: 500;
}

.end-date {
  font-size: 0.75rem;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 2rem;
}

.form-grid {
  display: grid;
  gap: 1.5rem;
}

.form-row {
  display: flex;
  flex-direction: column;
}

.form-section {
  border-top: 1px solid #e0e0e0;
  padding-top: 1.5rem;
}

.section-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: #333;
}

.publish-settings {
  display: grid;
  gap: 1rem;
}

.date-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.options-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.target-settings {
  display: grid;
  gap: 1rem;
}

.notice-preview {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-header {
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1.5rem;
  margin-bottom: 1.5rem;
}

.preview-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.preview-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 0 1rem 0;
  color: #333;
  display: flex;
  align-items: center;
}

.preview-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.875rem;
  color: #666;
}

.preview-content {
  margin-bottom: 2rem;
}

.content-text {
  line-height: 1.6;
  color: #333;
  white-space: pre-wrap;
}

.preview-footer {
  border-top: 1px solid #e0e0e0;
  padding-top: 1rem;
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.mr-2 {
  margin-right: 0.5rem;
}

@media (max-width: 768px) {
  .notice-management {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .header-actions {
    flex-wrap: wrap;
  }
  
  .filter-row {
    flex-direction: column;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .notices-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .notices-actions {
    flex-wrap: wrap;
  }
  
  .date-row {
    grid-template-columns: 1fr;
  }
  
  .options-row {
    grid-template-columns: 1fr;
  }
  
  .preview-info {
    flex-direction: column;
    align-items: stretch;
  }
}

@media (max-width: 480px) {
  .notice-management {
    padding: 0.75rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .notices-actions {
    flex-direction: column;
  }
  
  .title-meta {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
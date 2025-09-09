<template>
  <div class="board-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="forum" class="mr-2" />
            게시판 관리
          </h1>
          <p class="page-description">
            게시판을 생성하고 관리합니다. 카테고리별로 게시판을 구성할 수 있습니다.
          </p>
        </div>
        
        <div class="header-actions">
          <VaButton
            preset="secondary"
            icon="refresh"
            @click="loadBoards"
            :loading="loading"
          >
            새로고침
          </VaButton>
          
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            게시판 생성
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
                placeholder="게시판명, 설명 검색..."
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
                v-model="filters.status"
                :options="statusOptions"
                placeholder="상태 선택"
                clearable
                class="status-select"
              />
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="filters.type"
                :options="typeOptions"
                placeholder="게시판 유형 선택"
                clearable
                class="type-select"
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
    
    <!-- 게시판 목록 -->
    <VaCard class="boards-card">
      <VaCardContent>
        <div class="boards-header">
          <div class="boards-info">
            <span class="total-count">총 {{ totalBoards }}개 게시판</span>
            <span class="active-count">활성 {{ activeBoards }}개</span>
          </div>
          
          <div class="boards-actions">
            <VaButton
              preset="secondary"
              icon="view_module"
              :color="viewMode === 'grid' ? 'primary' : 'secondary'"
              @click="viewMode = 'grid'"
              title="그리드 보기"
            />
            
            <VaButton
              preset="secondary"
              icon="view_list"
              :color="viewMode === 'list' ? 'primary' : 'secondary'"
              @click="viewMode = 'list'"
              title="목록 보기"
            />
            
            <VaButton
              preset="secondary"
              icon="download"
              @click="exportBoards"
            >
              내보내기
            </VaButton>
          </div>
        </div>
        
        <!-- 로딩 상태 -->
        <div v-if="loading" class="loading-container">
          <VaProgressCircular indeterminate />
          <span class="loading-text">게시판 목록을 불러오는 중...</span>
        </div>
        
        <!-- 빈 상태 -->
        <div v-else-if="filteredBoards.length === 0" class="empty-state">
          <VaIcon name="forum" size="4rem" color="secondary" />
          <h3>게시판이 없습니다</h3>
          <p>새로운 게시판을 생성해보세요.</p>
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            게시판 생성
          </VaButton>
        </div>
        
        <!-- 그리드 보기 -->
        <div v-else-if="viewMode === 'grid'" class="boards-grid">
          <div
            v-for="board in paginatedBoards"
            :key="board.id"
            class="board-card"
            :class="{ 'inactive': !board.is_active }"
          >
            <div class="board-card-header">
              <div class="board-icon">
                <VaIcon 
                  :name="getBoardIcon(board.type)"
                  :color="board.is_active ? 'primary' : 'secondary'"
                  size="2rem"
                />
              </div>
              
              <div class="board-actions">
                <VaButton
                  preset="plain"
                  size="small"
                  icon="edit"
                  @click="editBoard(board)"
                  title="수정"
                />
                
                <VaButton
                  preset="plain"
                  size="small"
                  :icon="board.is_active ? 'visibility_off' : 'visibility'"
                  @click="toggleBoardStatus(board)"
                  :title="board.is_active ? '비활성화' : '활성화'"
                />
                
                <VaButton
                  preset="plain"
                  size="small"
                  icon="delete"
                  color="danger"
                  @click="deleteBoard(board)"
                  title="삭제"
                  :disabled="board.post_count > 0"
                />
              </div>
            </div>
            
            <div class="board-info">
              <h3 class="board-name">{{ board.name }}</h3>
              
              <div class="board-meta">
                <VaChip
                  :color="getCategoryColor(board.category)"
                  size="small"
                  outline
                >
                  {{ board.category }}
                </VaChip>
                
                <VaChip
                  :color="getTypeColor(board.type)"
                  size="small"
                  outline
                >
                  {{ getTypeLabel(board.type) }}
                </VaChip>
              </div>
              
              <p v-if="board.description" class="board-description">
                {{ board.description }}
              </p>
              
              <div class="board-stats">
                <div class="stat-item">
                  <VaIcon name="article" size="0.875rem" />
                  <span>{{ board.post_count || 0 }}개 게시글</span>
                </div>
                
                <div class="stat-item">
                  <VaIcon name="visibility" size="0.875rem" />
                  <span>{{ formatNumber(board.view_count || 0) }} 조회</span>
                </div>
              </div>
              
              <div class="board-footer">
                <span class="created-date">
                  {{ formatDate(board.created_at) }}
                </span>
                
                <VaChip
                  :color="board.is_active ? 'success' : 'danger'"
                  size="small"
                  outline
                >
                  {{ board.is_active ? '활성' : '비활성' }}
                </VaChip>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 목록 보기 -->
        <VaDataTable
          v-else
          :items="paginatedBoards"
          :columns="tableColumns"
          :loading="loading"
          striped
          hoverable
          class="boards-table"
        >
          <template #cell(icon)="{ rowData }">
            <VaIcon 
              :name="getBoardIcon(rowData.type)"
              :color="rowData.is_active ? 'primary' : 'secondary'"
              size="1.5rem"
            />
          </template>
          
          <template #cell(name)="{ rowData }">
            <div class="board-name-cell">
              <span class="name">{{ rowData.name }}</span>
              <span v-if="rowData.description" class="description">
                {{ rowData.description }}
              </span>
            </div>
          </template>
          
          <template #cell(category)="{ rowData }">
            <VaChip
              :color="getCategoryColor(rowData.category)"
              size="small"
              outline
            >
              {{ rowData.category }}
            </VaChip>
          </template>
          
          <template #cell(type)="{ rowData }">
            <VaChip
              :color="getTypeColor(rowData.type)"
              size="small"
              outline
            >
              {{ getTypeLabel(rowData.type) }}
            </VaChip>
          </template>
          
          <template #cell(stats)="{ rowData }">
            <div class="stats-cell">
              <span class="stat">{{ rowData.post_count || 0 }}개 글</span>
              <span class="stat">{{ formatNumber(rowData.view_count || 0) }} 조회</span>
            </div>
          </template>
          
          <template #cell(is_active)="{ rowData }">
            <VaChip
              :color="rowData.is_active ? 'success' : 'danger'"
              size="small"
              outline
            >
              {{ rowData.is_active ? '활성' : '비활성' }}
            </VaChip>
          </template>
          
          <template #cell(created_at)="{ rowData }">
            {{ formatDate(rowData.created_at) }}
          </template>
          
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <VaButton
                preset="secondary"
                size="small"
                icon="edit"
                @click="editBoard(rowData)"
                title="수정"
              />
              
              <VaButton
                preset="secondary"
                size="small"
                :icon="rowData.is_active ? 'visibility_off' : 'visibility'"
                @click="toggleBoardStatus(rowData)"
                :title="rowData.is_active ? '비활성화' : '활성화'"
              />
              
              <VaButton
                preset="secondary"
                color="danger"
                size="small"
                icon="delete"
                @click="deleteBoard(rowData)"
                title="삭제"
                :disabled="rowData.post_count > 0"
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
    
    <!-- 게시판 생성/수정 모달 -->
    <VaModal
      v-model="modals.board"
      :title="boardForm.id ? '게시판 수정' : '게시판 생성'"
      size="large"
      @ok="saveBoard"
      @cancel="closeBoardModal"
    >
      <VaForm ref="boardFormRef" @submit.prevent="saveBoard">
        <div class="form-grid">
          <div class="form-row">
            <VaInput
              v-model="boardForm.name"
              label="게시판명"
              placeholder="게시판명을 입력하세요"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="boardForm.slug"
              label="URL 슬러그"
              placeholder="board-slug"
              :rules="[required, slugRule]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="boardForm.category"
              label="카테고리"
              :options="categoryOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="boardForm.type"
              label="게시판 유형"
              :options="typeOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model.number="boardForm.sort_order"
              label="정렬 순서"
              type="number"
              :min="0"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaTextarea
              v-model="boardForm.description"
              label="설명"
              placeholder="게시판에 대한 설명을 입력하세요"
              :min-rows="3"
              :max-rows="5"
            />
          </div>
          
          <div class="form-section">
            <h4 class="section-title">권한 설정</h4>
            
            <div class="permission-grid">
              <VaCheckbox
                v-model="boardForm.allow_anonymous"
                label="익명 게시 허용"
              />
              
              <VaCheckbox
                v-model="boardForm.require_approval"
                label="게시글 승인 필요"
              />
              
              <VaCheckbox
                v-model="boardForm.allow_comments"
                label="댓글 허용"
              />
              
              <VaCheckbox
                v-model="boardForm.allow_attachments"
                label="첨부파일 허용"
              />
            </div>
          </div>
          
          <div class="form-section">
            <h4 class="section-title">기타 설정</h4>
            
            <div class="settings-grid">
              <VaInput
                v-model.number="boardForm.max_file_size"
                label="최대 파일 크기 (MB)"
                type="number"
                :min="1"
                :max="100"
              />
              
              <VaInput
                v-model.number="boardForm.posts_per_page"
                label="페이지당 게시글 수"
                type="number"
                :min="5"
                :max="100"
              />
            </div>
          </div>
          
          <div class="form-row">
            <VaCheckbox
              v-model="boardForm.is_active"
              label="활성 상태"
            />
          </div>
        </div>
      </VaForm>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vuestic-ui';
import type { Board } from '../../types/auth';

// 컴포저블
const { init: initToast } = useToast();

// 상태 관리
const loading = ref(false);
const boards = ref<Board[]>([]);
const viewMode = ref<'grid' | 'list'>('grid');
const currentPage = ref(1);
const itemsPerPage = ref(12);

// 필터 상태
const filters = ref({
  search: '',
  category: null as string | null,
  status: null as boolean | null,
  type: null as string | null,
});

// 모달 상태
const modals = ref({
  board: false,
});

// 폼 상태
const boardForm = ref({
  id: null as number | null,
  name: '',
  slug: '',
  description: '',
  category: '',
  type: '',
  sort_order: 0,
  allow_anonymous: false,
  require_approval: false,
  allow_comments: true,
  allow_attachments: true,
  max_file_size: 10,
  posts_per_page: 20,
  is_active: true,
});

// 폼 참조
const boardFormRef = ref();

// 옵션 데이터
const categoryOptions = [
  { text: '공지사항', value: 'notice' },
  { text: '자유게시판', value: 'free' },
  { text: 'Q&A', value: 'qna' },
  { text: '자료실', value: 'data' },
  { text: '갤러리', value: 'gallery' },
  { text: '이벤트', value: 'event' },
];

const statusOptions = [
  { text: '활성', value: true },
  { text: '비활성', value: false },
];

const typeOptions = [
  { text: '일반 게시판', value: 'general' },
  { text: '이미지 게시판', value: 'image' },
  { text: '파일 게시판', value: 'file' },
  { text: 'Q&A 게시판', value: 'qna' },
  { text: '공지 게시판', value: 'notice' },
];

// 테이블 컬럼
const tableColumns = [
  { key: 'icon', label: '', width: '50px' },
  { key: 'name', label: '게시판명', sortable: true },
  { key: 'category', label: '카테고리', sortable: true },
  { key: 'type', label: '유형', sortable: true },
  { key: 'stats', label: '통계' },
  { key: 'is_active', label: '상태', sortable: true },
  { key: 'created_at', label: '생성일', sortable: true },
  { key: 'actions', label: '작업', width: '120px' },
];

// 계산된 속성
const filteredBoards = computed(() => {
  let result = [...boards.value];
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    result = result.filter(board => 
      board.name.toLowerCase().includes(search) ||
      board.description?.toLowerCase().includes(search) ||
      board.slug.toLowerCase().includes(search)
    );
  }
  
  if (filters.value.category) {
    result = result.filter(board => board.category === filters.value.category);
  }
  
  if (filters.value.status !== null) {
    result = result.filter(board => board.is_active === filters.value.status);
  }
  
  if (filters.value.type) {
    result = result.filter(board => board.type === filters.value.type);
  }
  
  return result;
});

const totalBoards = computed(() => boards.value.length);

const activeBoards = computed(() => {
  return boards.value.filter(board => board.is_active).length;
});

const totalPages = computed(() => {
  return Math.ceil(filteredBoards.value.length / itemsPerPage.value);
});

const paginatedBoards = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value;
  const end = start + itemsPerPage.value;
  return filteredBoards.value.slice(start, end);
});

// 유틸리티 함수
const getBoardIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    general: 'forum',
    image: 'photo_library',
    file: 'folder',
    qna: 'help',
    notice: 'campaign',
  };
  return iconMap[type] || 'forum';
};

const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    notice: 'danger',
    free: 'primary',
    qna: 'info',
    data: 'success',
    gallery: 'warning',
    event: 'secondary',
  };
  return colorMap[category] || 'secondary';
};

const getTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    general: 'primary',
    image: 'warning',
    file: 'success',
    qna: 'info',
    notice: 'danger',
  };
  return colorMap[type] || 'secondary';
};

const getTypeLabel = (type: string): string => {
  const labelMap: Record<string, string> = {
    general: '일반',
    image: '이미지',
    file: '파일',
    qna: 'Q&A',
    notice: '공지',
  };
  return labelMap[type] || type;
};

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('ko-KR');
};

const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  }
  return num.toString();
};

// 검증 규칙
const required = (value: string | number) => !!value || '필수 입력 항목입니다.';
const slugRule = (value: string) => {
  if (!value) return true;
  const pattern = /^[a-z0-9-]+$/;
  return pattern.test(value) || 'URL 슬러그는 소문자, 숫자, 하이픈만 사용 가능합니다.';
};

// 메서드
const loadBoards = async () => {
  try {
    loading.value = true;
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    boards.value = [
      {
        id: 1,
        name: '공지사항',
        slug: 'notice',
        description: '중요한 공지사항을 게시하는 게시판입니다.',
        category: 'notice',
        type: 'notice',
        sort_order: 1,
        allow_anonymous: false,
        require_approval: true,
        allow_comments: false,
        allow_attachments: true,
        max_file_size: 10,
        posts_per_page: 20,
        is_active: true,
        post_count: 15,
        view_count: 2500,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        name: '자유게시판',
        slug: 'free',
        description: '자유롭게 의견을 나누는 게시판입니다.',
        category: 'free',
        type: 'general',
        sort_order: 2,
        allow_anonymous: true,
        require_approval: false,
        allow_comments: true,
        allow_attachments: true,
        max_file_size: 5,
        posts_per_page: 15,
        is_active: true,
        post_count: 128,
        view_count: 15600,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 3,
        name: 'Q&A',
        slug: 'qna',
        description: '질문과 답변을 위한 게시판입니다.',
        category: 'qna',
        type: 'qna',
        sort_order: 3,
        allow_anonymous: false,
        require_approval: false,
        allow_comments: true,
        allow_attachments: true,
        max_file_size: 10,
        posts_per_page: 20,
        is_active: true,
        post_count: 67,
        view_count: 8900,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
  } catch (error) {
    console.error('게시판 목록 로드 실패:', error);
    initToast({
      message: '게시판 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  resetBoardForm();
  modals.value.board = true;
};

const editBoard = (board: Board) => {
  boardForm.value = {
    id: board.id,
    name: board.name,
    slug: board.slug,
    description: board.description || '',
    category: board.category,
    type: board.type,
    sort_order: board.sort_order,
    allow_anonymous: board.allow_anonymous,
    require_approval: board.require_approval,
    allow_comments: board.allow_comments,
    allow_attachments: board.allow_attachments,
    max_file_size: board.max_file_size,
    posts_per_page: board.posts_per_page,
    is_active: board.is_active,
  };
  modals.value.board = true;
};

const saveBoard = async () => {
  try {
    // 폼 검증
    if (!boardFormRef.value?.validate()) {
      return;
    }
    
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const isEdit = !!boardForm.value.id;
    
    if (isEdit) {
      // 수정
      const index = boards.value.findIndex(board => board.id === boardForm.value.id);
      if (index !== -1) {
        boards.value[index] = {
          ...boards.value[index],
          ...boardForm.value,
          updated_at: new Date().toISOString(),
        };
      }
    } else {
      // 생성
      const newBoard: Board = {
        ...boardForm.value,
        id: Date.now(),
        post_count: 0,
        view_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      boards.value.push(newBoard);
    }
    
    initToast({
      message: `게시판이 성공적으로 ${isEdit ? '수정' : '생성'}되었습니다.`,
      color: 'success',
    });
    
    closeBoardModal();
  } catch (error) {
    console.error('게시판 저장 실패:', error);
    initToast({
      message: '게시판 저장에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const toggleBoardStatus = async (board: Board) => {
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = boards.value.findIndex(b => b.id === board.id);
    if (index !== -1) {
      boards.value[index].is_active = !boards.value[index].is_active;
      boards.value[index].updated_at = new Date().toISOString();
    }
    
    initToast({
      message: `게시판이 ${board.is_active ? '비활성화' : '활성화'}되었습니다.`,
      color: 'success',
    });
  } catch (error) {
    console.error('게시판 상태 변경 실패:', error);
    initToast({
      message: '게시판 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const deleteBoard = async (board: Board) => {
  if (board.post_count > 0) {
    initToast({
      message: '게시글이 있는 게시판은 삭제할 수 없습니다.',
      color: 'warning',
    });
    return;
  }
  
  if (!confirm(`'${board.name}' 게시판을 삭제하시겠습니까?`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = boards.value.findIndex(b => b.id === board.id);
    if (index !== -1) {
      boards.value.splice(index, 1);
    }
    
    initToast({
      message: '게시판이 삭제되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('게시판 삭제 실패:', error);
    initToast({
      message: '게시판 삭제에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const resetBoardForm = () => {
  boardForm.value = {
    id: null,
    name: '',
    slug: '',
    description: '',
    category: '',
    type: '',
    sort_order: 0,
    allow_anonymous: false,
    require_approval: false,
    allow_comments: true,
    allow_attachments: true,
    max_file_size: 10,
    posts_per_page: 20,
    is_active: true,
  };
};

const closeBoardModal = () => {
  modals.value.board = false;
  resetBoardForm();
};

const resetFilters = () => {
  filters.value = {
    search: '',
    category: null,
    status: null,
    type: null,
  };
};

const exportBoards = () => {
  // 게시판 목록 내보내기 구현
  initToast({
    message: '게시판 목록을 내보내는 기능은 준비 중입니다.',
    color: 'info',
  });
};

// 감시자
watch(() => filters.value, () => {
  currentPage.value = 1; // 필터 변경 시 첫 페이지로
}, { deep: true });

watch(() => boardForm.value.name, (newName) => {
  if (newName && !boardForm.value.id) {
    // 새 게시판 생성 시 이름에서 슬러그 자동 생성
    boardForm.value.slug = newName
      .toLowerCase()
      .replace(/[^a-z0-9가-힣]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
  }
});

// 라이프사이클
onMounted(() => {
  loadBoards();
});
</script>

<style scoped>
.board-management {
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

.boards-card {
  margin-bottom: 1.5rem;
}

.boards-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.boards-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.total-count,
.active-count {
  font-weight: 500;
  color: #666;
}

.boards-actions {
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

.boards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.board-card {
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  background: #fff;
  transition: all 0.2s ease;
  position: relative;
}

.board-card:hover {
  border-color: #ccc;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.board-card.inactive {
  background: #f8f9fa;
  opacity: 0.8;
}

.board-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.board-icon {
  flex-shrink: 0;
}

.board-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.board-card:hover .board-actions {
  opacity: 1;
}

.board-info {
  flex: 1;
}

.board-name {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.75rem 0;
  color: #333;
}

.board-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.board-description {
  color: #666;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 1rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.board-stats {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  color: #666;
}

.board-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.created-date {
  font-size: 0.75rem;
  color: #999;
}

.boards-table {
  margin-bottom: 2rem;
}

.board-name-cell .name {
  font-weight: 600;
  display: block;
}

.board-name-cell .description {
  font-size: 0.875rem;
  color: #666;
  margin-top: 0.25rem;
  display: block;
}

.stats-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stats-cell .stat {
  font-size: 0.875rem;
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

.permission-grid,
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

@media (max-width: 768px) {
  .board-management {
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
  
  .boards-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .boards-grid {
    grid-template-columns: 1fr;
  }
  
  .board-actions {
    opacity: 1;
  }
  
  .permission-grid,
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .board-management {
    padding: 0.75rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .board-card {
    padding: 1rem;
  }
  
  .board-name {
    font-size: 1.125rem;
  }
  
  .board-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>
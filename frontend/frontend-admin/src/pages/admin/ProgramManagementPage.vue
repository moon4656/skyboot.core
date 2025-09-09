<template>
  <div class="program-management-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">프로그램 관리</h1>
        <p class="page-subtitle">시스템 프로그램을 관리합니다</p>
      </div>
      <div class="header-actions">
        <va-button
          icon="add"
          @click="openCreateModal"
        >
          프로그램 추가
        </va-button>
      </div>
    </div>

    <!-- 필터 및 검색 -->
    <va-card class="filter-card">
      <va-card-content>
        <div class="filter-row">
          <div class="filter-group">
            <va-select
              v-model="filters.status"
              label="상태"
              :options="statusOptions"
              placeholder="전체"
              clearable
            />
            <va-select
              v-model="filters.category"
              label="카테고리"
              :options="categoryOptions"
              placeholder="전체"
              clearable
            />
          </div>
          <div class="search-group">
            <va-input
              v-model="filters.search"
              label="검색"
              placeholder="프로그램명, 설명 검색..."
              clearable
            >
              <template #append>
                <va-button
                  preset="secondary"
                  icon="search"
                  @click="handleSearch"
                />
              </template>
            </va-input>
          </div>
        </div>
      </va-card-content>
    </va-card>

    <!-- 프로그램 목록 -->
    <va-card>
      <va-card-content>
        <va-data-table
          :items="paginatedPrograms"
          :columns="columns"
          :loading="isLoading"
          striped
          hoverable
        >
          <template #cell(status)="{ rowData }">
            <va-badge
              :color="getStatusColor(rowData.status)"
              :text="getStatusText(rowData.status)"
            />
          </template>
          
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <va-button
                preset="secondary"
                size="small"
                icon="edit"
                @click="openEditModal(rowData)"
              />
              <va-button
                preset="secondary"
                size="small"
                icon="visibility"
                @click="viewProgram(rowData)"
              />
              <va-button
                preset="secondary"
                size="small"
                icon="delete"
                @click="confirmDelete(rowData)"
              />
            </div>
          </template>
        </va-data-table>

        <!-- 페이지네이션 -->
        <div class="pagination-wrapper">
          <va-pagination
            v-model="currentPage"
            :pages="totalPages"
            :visible-pages="5"
          />
        </div>
      </va-card-content>
    </va-card>

    <!-- 프로그램 생성/수정 모달 -->
    <va-modal
      v-model="showModal"
      title="프로그램 정보"
      size="large"
      max-width="800px"
    >
      <va-form ref="formRef">
        <div class="modal-form">
          <div class="form-row">
            <va-input
              v-model="formData.name"
              label="프로그램명"
              :rules="[required]"
              placeholder="프로그램명을 입력하세요"
            />
            <va-input
              v-model="formData.code"
              label="프로그램 코드"
              :rules="[required]"
              placeholder="프로그램 코드를 입력하세요"
            />
          </div>
          
          <div class="form-row">
            <va-select
              v-model="formData.category"
              label="카테고리"
              :options="categoryOptions"
              :rules="[required]"
            />
            <va-select
              v-model="formData.status"
              label="상태"
              :options="statusOptions"
              :rules="[required]"
            />
          </div>
          
          <va-textarea
            v-model="formData.description"
            label="설명"
            placeholder="프로그램 설명을 입력하세요"
            rows="3"
          />
          
          <div class="form-row">
            <va-input
              v-model="formData.url"
              label="URL"
              placeholder="프로그램 URL을 입력하세요"
            />
            <va-input
              v-model="formData.icon"
              label="아이콘"
              placeholder="아이콘명을 입력하세요"
            />
          </div>
          
          <div class="form-row">
            <va-input
              v-model.number="formData.sortOrder"
              type="number"
              label="정렬 순서"
              placeholder="정렬 순서를 입력하세요"
            />
            <va-checkbox
              v-model="formData.isActive"
              label="활성화"
            />
          </div>
        </div>
      </va-form>
      
      <template #footer>
        <div class="modal-actions">
          <va-button
            preset="secondary"
            @click="closeModal"
          >
            취소
          </va-button>
          <va-button
            :loading="isSaving"
            @click="handleSave"
          >
            {{ isEditMode ? '수정' : '생성' }}
          </va-button>
        </div>
      </template>
    </va-modal>

    <!-- 프로그램 상세 모달 -->
    <va-modal
      v-model="showDetailModal"
      title="프로그램 상세 정보"
      size="large"
    >
      <div v-if="selectedProgram" class="detail-content">
        <div class="detail-section">
          <h3>기본 정보</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>프로그램명:</label>
              <span>{{ selectedProgram.name }}</span>
            </div>
            <div class="detail-item">
              <label>프로그램 코드:</label>
              <span>{{ selectedProgram.code }}</span>
            </div>
            <div class="detail-item">
              <label>카테고리:</label>
              <span>{{ selectedProgram.category }}</span>
            </div>
            <div class="detail-item">
              <label>상태:</label>
              <va-badge
                :color="getStatusColor(selectedProgram.status)"
                :text="getStatusText(selectedProgram.status)"
              />
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h3>추가 정보</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>URL:</label>
              <span>{{ selectedProgram.url || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>아이콘:</label>
              <span>{{ selectedProgram.icon || '-' }}</span>
            </div>
            <div class="detail-item">
              <label>정렬 순서:</label>
              <span>{{ selectedProgram.sortOrder }}</span>
            </div>
            <div class="detail-item">
              <label>활성화:</label>
              <span>{{ selectedProgram.isActive ? '예' : '아니오' }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h3>설명</h3>
          <p>{{ selectedProgram.description || '설명이 없습니다.' }}</p>
        </div>
        
        <div class="detail-section">
          <h3>생성/수정 정보</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>생성일:</label>
              <span>{{ formatDate(selectedProgram.createdAt) }}</span>
            </div>
            <div class="detail-item">
              <label>수정일:</label>
              <span>{{ formatDate(selectedProgram.updatedAt) }}</span>
            </div>
          </div>
        </div>
      </div>
    </va-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from 'vuestic-ui'

interface Program {
  id: number
  name: string
  code: string
  description?: string
  category: string
  status: 'active' | 'inactive' | 'development'
  url?: string
  icon?: string
  sortOrder: number
  isActive: boolean
  createdAt: string
  updatedAt: string
}

interface ProgramForm {
  name: string
  code: string
  description: string
  category: string
  status: 'active' | 'inactive' | 'development'
  url: string
  icon: string
  sortOrder: number
  isActive: boolean
}

interface Filters {
  status: string
  category: string
  search: string
}

const { init } = useToast()
const formRef = ref()

// 상태 관리
const isLoading = ref(false)
const isSaving = ref(false)
const showModal = ref(false)
const showDetailModal = ref(false)
const isEditMode = ref(false)
const selectedProgram = ref<Program | null>(null)
const currentPage = ref(1)
const itemsPerPage = ref(10)

// 필터 상태
const filters = ref<Filters>({
  status: '',
  category: '',
  search: ''
})

// 폼 상태
const formData = ref<ProgramForm>({
  name: '',
  code: '',
  description: '',
  category: '',
  status: 'active',
  url: '',
  icon: '',
  sortOrder: 0,
  isActive: true
})

// 옵션 데이터
const statusOptions = [
  { text: '활성', value: 'active' },
  { text: '비활성', value: 'inactive' },
  { text: '개발중', value: 'development' }
]

const categoryOptions = [
  { text: '시스템 관리', value: 'system' },
  { text: '사용자 관리', value: 'user' },
  { text: '콘텐츠 관리', value: 'content' },
  { text: '보고서', value: 'report' },
  { text: '설정', value: 'setting' }
]

// 테이블 컬럼
const columns = [
  { key: 'name', label: '프로그램명', sortable: true },
  { key: 'code', label: '코드', sortable: true },
  { key: 'category', label: '카테고리', sortable: true },
  { key: 'status', label: '상태', sortable: true },
  { key: 'sortOrder', label: '순서', sortable: true },
  { key: 'actions', label: '작업', width: '120px' }
]

// 목 데이터
const programs = ref<Program[]>([
  {
    id: 1,
    name: '사용자 관리',
    code: 'USER_MGMT',
    description: '시스템 사용자를 관리하는 프로그램',
    category: 'user',
    status: 'active',
    url: '/admin/users',
    icon: 'people',
    sortOrder: 1,
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 2,
    name: '메뉴 관리',
    code: 'MENU_MGMT',
    description: '시스템 메뉴를 관리하는 프로그램',
    category: 'system',
    status: 'active',
    url: '/admin/menus',
    icon: 'menu',
    sortOrder: 2,
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  },
  {
    id: 3,
    name: '권한 관리',
    code: 'PERM_MGMT',
    description: '사용자 권한을 관리하는 프로그램',
    category: 'user',
    status: 'active',
    url: '/admin/permissions',
    icon: 'security',
    sortOrder: 3,
    isActive: true,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T00:00:00Z'
  }
])

// 계산된 속성
const filteredPrograms = computed(() => {
  let result = programs.value

  if (filters.value.status) {
    result = result.filter(program => program.status === filters.value.status)
  }

  if (filters.value.category) {
    result = result.filter(program => program.category === filters.value.category)
  }

  if (filters.value.search) {
    const search = filters.value.search.toLowerCase()
    result = result.filter(program => 
      program.name.toLowerCase().includes(search) ||
      program.code.toLowerCase().includes(search) ||
      (program.description && program.description.toLowerCase().includes(search))
    )
  }

  return result
})

const totalPages = computed(() => {
  return Math.ceil(filteredPrograms.value.length / itemsPerPage.value)
})

const paginatedPrograms = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredPrograms.value.slice(start, end)
})

// 유틸리티 함수
const getStatusColor = (status: string): string => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'danger'
    case 'development': return 'warning'
    default: return 'secondary'
  }
}

const getStatusText = (status: string): string => {
  switch (status) {
    case 'active': return '활성'
    case 'inactive': return '비활성'
    case 'development': return '개발중'
    default: return '알 수 없음'
  }
}

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleString('ko-KR')
}

// 검증 규칙
const required = (value: string) => !!value || '필수 입력 항목입니다'

// 메서드
const handleSearch = () => {
  currentPage.value = 1
}

const openCreateModal = () => {
  isEditMode.value = false
  formData.value = {
    name: '',
    code: '',
    description: '',
    category: '',
    status: 'active',
    url: '',
    icon: '',
    sortOrder: 0,
    isActive: true
  }
  showModal.value = true
}

const openEditModal = (program: Program) => {
  isEditMode.value = true
  formData.value = {
    name: program.name,
    code: program.code,
    description: program.description || '',
    category: program.category,
    status: program.status,
    url: program.url || '',
    icon: program.icon || '',
    sortOrder: program.sortOrder,
    isActive: program.isActive
  }
  selectedProgram.value = program
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedProgram.value = null
}

const handleSave = async () => {
  if (!formRef.value?.validate()) {
    return
  }

  isSaving.value = true

  try {
    if (isEditMode.value) {
      // 수정 로직
      const index = programs.value.findIndex(p => p.id === selectedProgram.value?.id)
      if (index !== -1) {
        programs.value[index] = {
          ...programs.value[index],
          ...formData.value,
          updatedAt: new Date().toISOString()
        }
      }
      
      init({
        message: '프로그램이 성공적으로 수정되었습니다.',
        color: 'success'
      })
    } else {
      // 생성 로직
      const newProgram: Program = {
        id: Date.now(),
        ...formData.value,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      programs.value.push(newProgram)
      
      init({
        message: '프로그램이 성공적으로 생성되었습니다.',
        color: 'success'
      })
    }

    closeModal()
  } catch (error) {
    init({
      message: '작업 중 오류가 발생했습니다.',
      color: 'danger'
    })
  } finally {
    isSaving.value = false
  }
}

const viewProgram = (program: Program) => {
  selectedProgram.value = program
  showDetailModal.value = true
}

const confirmDelete = (program: Program) => {
  if (confirm(`'${program.name}' 프로그램을 삭제하시겠습니까?`)) {
    deleteProgram(program)
  }
}

const deleteProgram = (program: Program) => {
  const index = programs.value.findIndex(p => p.id === program.id)
  if (index !== -1) {
    programs.value.splice(index, 1)
    init({
      message: '프로그램이 성공적으로 삭제되었습니다.',
      color: 'success'
    })
  }
}

// 감시자
watch([() => filters.value.status, () => filters.value.category], () => {
  currentPage.value = 1
})

// 라이프사이클
onMounted(() => {
  // 초기 데이터 로드
})
</script>

<style scoped>
.program-management-page {
  padding: 1.5rem;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}

.header-content h1 {
  font-size: 1.75rem;
  font-weight: bold;
  margin-bottom: 0.25rem;
}

.header-content p {
  color: var(--va-text-secondary);
}

.filter-card {
  margin-bottom: 1.5rem;
}

.filter-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  align-items: end;
}

.filter-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.search-group {
  display: flex;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: var(--va-primary);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-weight: 500;
  color: var(--va-text-secondary);
  font-size: 0.875rem;
}

.detail-item span {
  color: var(--va-text-primary);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .filter-row {
    grid-template-columns: 1fr;
  }
  
  .filter-group {
    grid-template-columns: 1fr;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
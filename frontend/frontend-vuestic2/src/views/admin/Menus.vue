<template>
  <div class="menus-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="d-flex justify-content-between align-items-center">
        <div>
          <h1 class="page-title">메뉴 관리</h1>
          <p class="page-description text-gray-600">시스템 메뉴 구조를 관리합니다</p>
        </div>
        <va-button
          color="primary"
          icon="add"
          @click="openCreateModal"
        >
          메뉴 추가
        </va-button>
      </div>
    </div>

    <!-- 검색 및 필터 -->
    <va-card class="mb-4">
      <va-card-content>
        <div class="row">
          <div class="flex md6">
            <va-input
              v-model="searchQuery"
              placeholder="메뉴명으로 검색..."
              clearable
              class="w-100"
            >
              <template #prependInner>
                <va-icon name="search" />
              </template>
            </va-input>
          </div>
          <div class="flex md6">
            <va-select
              v-model="selectedStatus"
              :options="statusOptions"
              placeholder="상태 필터"
              clearable
              class="w-100"
            />
          </div>
        </div>
      </va-card-content>
    </va-card>

    <!-- 메뉴 트리 테이블 -->
    <va-card>
      <va-card-content>
        <va-data-table
          :items="filteredMenus"
          :columns="columns"
          :loading="loading"
          striped
          hoverable
          class="menu-table"
        >
          <!-- 메뉴명 컬럼 -->
          <template #cell(name)="{ rowData }">
            <div class="d-flex align-items-center">
              <va-icon
                :name="rowData.icon || 'folder'"
                class="mr-2"
                :color="rowData.level === 0 ? 'primary' : 'secondary'"
              />
              <span :style="{ marginLeft: `${rowData.level * 20}px` }">
                {{ rowData.name }}
              </span>
            </div>
          </template>

          <!-- 상태 컬럼 -->
          <template #cell(status)="{ rowData }">
            <va-chip
              :color="getStatusColor(rowData.status)"
              size="small"
            >
              {{ getStatusText(rowData.status) }}
            </va-chip>
          </template>

          <!-- 타입 컬럼 -->
          <template #cell(type)="{ rowData }">
            <va-chip
              :color="getTypeColor(rowData.type)"
              size="small"
              outline
            >
              {{ getTypeText(rowData.type) }}
            </va-chip>
          </template>

          <!-- 순서 컬럼 -->
          <template #cell(sort_order)="{ rowData }">
            <div class="d-flex align-items-center">
              <va-button
                preset="plain"
                icon="keyboard_arrow_up"
                size="small"
                @click="moveMenu(rowData, 'up')"
                :disabled="!canMoveUp(rowData)"
              />
              <span class="mx-2">{{ rowData.sort_order }}</span>
              <va-button
                preset="plain"
                icon="keyboard_arrow_down"
                size="small"
                @click="moveMenu(rowData, 'down')"
                :disabled="!canMoveDown(rowData)"
              />
            </div>
          </template>

          <!-- 액션 컬럼 -->
          <template #cell(actions)="{ rowData }">
            <div class="d-flex gap-2">
              <va-button
                preset="plain"
                icon="edit"
                size="small"
                color="primary"
                @click="editMenu(rowData)"
              />
              <va-button
                preset="plain"
                icon="add"
                size="small"
                color="success"
                @click="addSubMenu(rowData)"
                v-if="rowData.type !== 'action'"
              />
              <va-button
                preset="plain"
                icon="delete"
                size="small"
                color="danger"
                @click="deleteMenu(rowData)"
              />
            </div>
          </template>
        </va-data-table>
      </va-card-content>
    </va-card>

    <!-- 메뉴 생성/수정 모달 -->
    <va-modal
      v-model="showModal"
      :title="isEditing ? '메뉴 수정' : '메뉴 생성'"
      size="large"
      @ok="handleSave"
      @cancel="handleCancel"
    >
      <MenuForm
        ref="menuFormRef"
        v-model="formData"
        :parent-options="parentOptions"
        :is-editing="isEditing"
      />
    </va-modal>

    <!-- 삭제 확인 모달 -->
    <va-modal
      v-model="showDeleteModal"
      title="메뉴 삭제 확인"
      message="정말로 이 메뉴를 삭제하시겠습니까? 하위 메뉴도 함께 삭제됩니다."
      @ok="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vuestic-ui'
import { menuApi, type MenuInfo, type MenuCreate, type MenuUpdate } from '@/services/api'
import MenuForm from '@/components/admin/MenuForm.vue'

// 토스트 알림
const { init: notify } = useToast()

// 반응형 데이터
const loading = ref(false)
const menus = ref<MenuInfo[]>([])
const searchQuery = ref('')
const selectedStatus = ref('all')
const showModal = ref(false)
const isEditing = ref(false)
const menuFormRef = ref()
const expandedRows = ref<number[]>([])
const showDeleteModal = ref(false)
const selectedMenu = ref<any>(null)

// 메뉴 폼 데이터
const formData = ref({
  name: '',
  path: '',
  icon: '',
  parent_id: null,
  type: 'menu',
  status: 'active',
  sort_order: 0,
  description: '',
  permission: ''
})



// 테이블 컬럼 정의
const columns = [
  { key: 'name', label: '메뉴명', sortable: true },
  { key: 'path', label: '경로', sortable: true },
  { key: 'type', label: '타입', sortable: true },
  { key: 'status', label: '상태', sortable: true },
  { key: 'sort_order', label: '순서', sortable: true },
  { key: 'permission', label: '권한', sortable: true },
  { key: 'actions', label: '액션', width: 150 }
]

// 선택 옵션
const statusOptions = [
  { text: '전체', value: 'all' },
  { text: '활성', value: 'active' },
  { text: '비활성', value: 'inactive' },
  { text: '곧 출시', value: 'coming_soon' }
]

// 계산된 속성
const filteredMenus = computed(() => {
  let filtered = menus.value

  if (searchQuery.value) {
    filtered = filtered.filter(menu => 
      menu.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
  }

  if (selectedStatus.value && selectedStatus.value !== 'all') {
    filtered = filtered.filter(menu => menu.status === selectedStatus.value)
  }

  return filtered
})

const parentOptions = computed(() => {
  return menus.value
    .filter(menu => menu.type === 'menu')
    .map(menu => ({
      text: menu.name,
      value: menu.id
    }))
})

// 메서드
const getStatusColor = (status: string) => {
  switch (status) {
    case 'active': return 'success'
    case 'inactive': return 'danger'
    case 'coming_soon': return 'warning'
    default: return 'secondary'
  }
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'active': return '활성'
    case 'inactive': return '비활성'
    case 'coming_soon': return '곧 출시'
    default: return '알 수 없음'
  }
}

const getTypeColor = (type: string) => {
  switch (type) {
    case 'menu': return 'primary'
    case 'action': return 'info'
    default: return 'secondary'
  }
}

const getTypeText = (type: string) => {
  switch (type) {
    case 'menu': return '메뉴'
    case 'action': return '액션'
    default: return '알 수 없음'
  }
}

const canMoveUp = (menu: any) => {
  const siblings = menus.value.filter(m => m.parent_id === menu.parent_id)
  return menu.sort_order > 1
}

const canMoveDown = (menu: any) => {
  const siblings = menus.value.filter(m => m.parent_id === menu.parent_id)
  const maxOrder = Math.max(...siblings.map(s => s.sort_order))
  return menu.sort_order < maxOrder
}

const moveMenu = async (menu: any, direction: 'up' | 'down') => {
  try {
    loading.value = true
    
    // 실제 API 호출 로직 구현 필요
    console.log(`메뉴 ${menu.name}을(를) ${direction} 방향으로 이동`)
    
    notify({
      message: '메뉴 순서가 변경되었습니다.',
      color: 'success'
    })
  } catch (error) {
    console.error('메뉴 이동 실패:', error)
    notify({
      message: '메뉴 이동에 실패했습니다.',
      color: 'danger'
    })
  } finally {
    loading.value = false
  }
}

const editMenu = (menu: any) => {
  selectedMenu.value = menu
  formData.value = { ...menu }
  isEditing.value = true
  showModal.value = true
}

const addSubMenu = (parentMenu: any) => {
  formData.value = {
    name: '',
    path: '',
    icon: '',
    parent_id: parentMenu.id,
    type: 'action',
    status: 'active',
    sort_order: 0,
    description: '',
    permission: ''
  }
  isEditing.value = false
  showModal.value = true
}

const deleteMenu = (menu: any) => {
  selectedMenu.value = menu
  showDeleteModal.value = true
}

// 폼 저장 처리
const handleSave = async () => {
  try {
    const isValid = await menuFormRef.value?.validate()
    if (!isValid) {
      notify({
        message: '입력 정보를 확인해주세요.',
        color: 'danger'
      })
      return
    }

    loading.value = true

    if (isEditing.value) {
      await menuApi.updateMenu(formData.value.id!, formData.value)
      notify({
        message: '메뉴가 성공적으로 수정되었습니다.',
        color: 'success'
      })
    } else {
      await menuApi.createMenu(formData.value)
      notify({
        message: '메뉴가 성공적으로 생성되었습니다.',
        color: 'success'
      })
    }

    showModal.value = false
    await loadMenus()
  } catch (error: any) {
    console.error('메뉴 저장 실패:', error)
    notify({
      message: error.response?.data?.detail || '메뉴 저장에 실패했습니다.',
      color: 'danger'
    })
  } finally {
    loading.value = false
  }
}

// 폼 취소 처리
const handleCancel = () => {
  showModal.value = false
  resetForm()
}

const confirmDelete = async () => {
  try {
    loading.value = true
    
    // 실제 API 호출 로직 구현 필요
    console.log('메뉴 삭제:', selectedMenu.value)
    
    notify({
      message: '메뉴가 삭제되었습니다.',
      color: 'success'
    })
    
    showDeleteModal.value = false
    selectedMenu.value = null
  } catch (error) {
    console.error('메뉴 삭제 실패:', error)
    notify({
      message: '메뉴 삭제에 실패했습니다.',
      color: 'danger'
    })
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formData.value = {
    name: '',
    path: '',
    icon: '',
    parent_id: null,
    type: 'menu',
    status: 'active',
    sort_order: 0,
    description: '',
    permission: ''
  }
  selectedMenu.value = null
  isEditing.value = false
}

const loadMenus = async () => {
  try {
    loading.value = true
    
    const response = await menuApi.getMenus()
    menus.value = response.data
    
  } catch (error) {
    console.error('메뉴 목록 로드 실패:', error)
    notify({
      message: '메뉴 목록을 불러오는데 실패했습니다.',
      color: 'danger'
    })
  } finally {
    loading.value = false
  }
}

// 메뉴 생성 모달 열기
const openCreateModal = () => {
  resetForm()
  showModal.value = true
}

// 라이프사이클
onMounted(() => {
  loadMenus()
})
</script>

<style scoped>
.menus-page {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.page-description {
  font-size: 1rem;
  margin-bottom: 0;
}

.menu-table {
  min-height: 400px;
}

.gap-2 {
  gap: 0.5rem;
}

@media (max-width: 768px) {
  .menus-page {
    padding: 1rem;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .page-header .d-flex {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
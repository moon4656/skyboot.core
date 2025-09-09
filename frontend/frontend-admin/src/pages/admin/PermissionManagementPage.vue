<template>
  <div class="permission-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="security" class="mr-2" />
            권한 관리
          </h1>
          <p class="page-description">
            시스템 권한을 관리하고 사용자에게 권한을 할당합니다.
          </p>
        </div>
        
        <div class="header-actions">
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            권한 추가
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
                placeholder="권한명, 설명 검색..."
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
            
            <div class="filter-actions">
              <VaButton
                preset="secondary"
                icon="refresh"
                @click="resetFilters"
              >
                초기화
              </VaButton>
            </div>
          </div>
        </div>
      </VaCardContent>
    </VaCard>
    
    <!-- 권한 목록 -->
    <VaCard class="permissions-card">
      <VaCardContent>
        <div class="table-header">
          <div class="table-info">
            <span class="total-count">총 {{ filteredPermissions.length }}개 권한</span>
          </div>
          
          <div class="table-actions">
            <VaButton
              preset="secondary"
              icon="download"
              @click="exportPermissions"
            >
              내보내기
            </VaButton>
          </div>
        </div>
        
        <VaDataTable
          :items="paginatedPermissions"
          :columns="columns"
          :loading="loading"
          :per-page="pagination.perPage"
          :current-page="pagination.currentPage"
          @update:current-page="pagination.currentPage = $event"
          striped
          hoverable
        >
          <template #cell(name)="{ rowData }">
            <div class="permission-name">
              <VaIcon
                :name="getCategoryIcon(rowData.category)"
                :color="getCategoryColor(rowData.category)"
                class="mr-2"
              />
              <span class="name-text">{{ rowData.name }}</span>
            </div>
          </template>
          
          <template #cell(code)="{ rowData }">
            <VaChip
              color="info"
              size="small"
              outline
            >
              {{ rowData.code }}
            </VaChip>
          </template>
          
          <template #cell(category)="{ rowData }">
            <VaChip
              :color="getCategoryColor(rowData.category)"
              size="small"
              outline
            >
              {{ getCategoryLabel(rowData.category) }}
            </VaChip>
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
          
          <template #cell(user_count)="{ rowData }">
            <VaButton
              preset="plain"
              size="small"
              @click="showPermissionUsers(rowData)"
            >
              {{ rowData.user_count }}명
            </VaButton>
          </template>
          
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <VaButton
                preset="secondary"
                size="small"
                icon="edit"
                @click="editPermission(rowData)"
                title="수정"
              />
              
              <VaButton
                :preset="rowData.is_active ? 'secondary' : 'primary'"
                :color="rowData.is_active ? 'warning' : 'success'"
                size="small"
                :icon="rowData.is_active ? 'visibility_off' : 'visibility'"
                @click="togglePermissionStatus(rowData)"
                :title="rowData.is_active ? '비활성화' : '활성화'"
              />
              
              <VaButton
                preset="secondary"
                color="danger"
                size="small"
                icon="delete"
                @click="deletePermission(rowData)"
                title="삭제"
                :disabled="rowData.user_count > 0"
              />
            </div>
          </template>
        </VaDataTable>
        
        <!-- 페이지네이션 -->
        <div class="pagination-wrapper">
          <VaPagination
            v-model="pagination.currentPage"
            :pages="totalPages"
            :visible-pages="5"
            buttons-preset="secondary"
          />
        </div>
      </VaCardContent>
    </VaCard>
    
    <!-- 권한 생성/수정 모달 -->
    <VaModal
      v-model="modals.permission"
      title="권한 정보"
      size="large"
      @ok="savePermission"
      @cancel="closePermissionModal"
    >
      <VaForm ref="permissionForm" @submit.prevent="savePermission">
        <div class="form-grid">
          <div class="form-row">
            <VaInput
              v-model="permissionForm.name"
              label="권한명"
              placeholder="권한명을 입력하세요"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="permissionForm.code"
              label="권한 코드"
              placeholder="PERMISSION_CODE"
              :rules="[required, permissionCodeRule]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="permissionForm.category"
              label="카테고리"
              :options="categoryOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaTextarea
              v-model="permissionForm.description"
              label="설명"
              placeholder="권한에 대한 설명을 입력하세요"
              :min-rows="3"
              :max-rows="5"
            />
          </div>
          
          <div class="form-row">
            <VaCheckbox
              v-model="permissionForm.is_active"
              label="활성 상태"
            />
          </div>
        </div>
      </VaForm>
    </VaModal>
    
    <!-- 권한 사용자 목록 모달 -->
    <VaModal
      v-model="modals.users"
      title="권한 보유 사용자"
      size="large"
      hide-default-actions
    >
      <div class="users-modal-content">
        <div class="users-header">
          <h3>{{ selectedPermission?.name }} 권한 보유 사용자</h3>
          <VaInput
            v-model="userSearch"
            placeholder="사용자 검색..."
            clearable
            class="user-search"
          >
            <template #prependInner>
              <VaIcon name="search" />
            </template>
          </VaInput>
        </div>
        
        <VaDataTable
          :items="filteredPermissionUsers"
          :columns="userColumns"
          :loading="loadingUsers"
          striped
          hoverable
        >
          <template #cell(avatar)="{ rowData }">
            <VaAvatar
              :src="rowData.avatar"
              :fallback-text="rowData.username.charAt(0).toUpperCase()"
              size="small"
            />
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
          
          <template #cell(actions)="{ rowData }">
            <VaButton
              preset="secondary"
              color="danger"
              size="small"
              icon="remove_circle"
              @click="removeUserPermission(rowData)"
              title="권한 제거"
            />
          </template>
        </VaDataTable>
      </div>
      
      <template #footer>
        <VaButton
          preset="secondary"
          @click="modals.users = false"
        >
          닫기
        </VaButton>
      </template>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vuestic-ui';
import type { Permission, User } from '../../types/auth';

// 컴포저블
const { init: initToast } = useToast();

// 상태 관리
const loading = ref(false);
const loadingUsers = ref(false);
const permissions = ref<Permission[]>([]);
const permissionUsers = ref<User[]>([]);
const selectedPermission = ref<Permission | null>(null);
const userSearch = ref('');

// 필터 상태
const filters = ref({
  search: '',
  category: null as string | null,
  status: null as boolean | null,
});

// 페이지네이션
const pagination = ref({
  currentPage: 1,
  perPage: 10,
});

// 모달 상태
const modals = ref({
  permission: false,
  users: false,
});

// 폼 상태
const permissionForm = ref({
  id: null as number | null,
  name: '',
  code: '',
  category: '',
  resource: '',
  action: '',
  description: '',
  is_active: true,
});

// 폼 참조
const permissionFormRef = ref();

// 옵션 데이터
const categoryOptions = [
  { text: '시스템 관리', value: 'system' },
  { text: '사용자 관리', value: 'user' },
  { text: '메뉴 관리', value: 'menu' },
  { text: '권한 관리', value: 'permission' },
  { text: '게시판 관리', value: 'board' },
  { text: '콘텐츠 관리', value: 'content' },
  { text: '기타', value: 'other' },
];

const statusOptions = [
  { text: '활성', value: true },
  { text: '비활성', value: false },
];

// 테이블 컬럼
const columns = [
  { key: 'name', label: '권한명', sortable: true },
  { key: 'code', label: '권한 코드', sortable: true },
  { key: 'category', label: '카테고리', sortable: true },
  { key: 'description', label: '설명' },
  { key: 'user_count', label: '사용자 수', sortable: true },
  { key: 'is_active', label: '상태', sortable: true },
  { key: 'actions', label: '작업', width: '120px' },
];

const userColumns = [
  { key: 'avatar', label: '', width: '50px' },
  { key: 'username', label: '사용자명', sortable: true },
  { key: 'email', label: '이메일', sortable: true },
  { key: 'full_name', label: '이름', sortable: true },
  { key: 'is_active', label: '상태', sortable: true },
  { key: 'actions', label: '작업', width: '80px' },
];

// 계산된 속성
const filteredPermissions = computed(() => {
  let result = [...permissions.value];
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    result = result.filter(permission => 
      permission.name.toLowerCase().includes(search) ||
      permission.code.toLowerCase().includes(search) ||
      permission.description?.toLowerCase().includes(search)
    );
  }
  
  if (filters.value.category) {
    result = result.filter(permission => permission.category === filters.value.category);
  }
  
  if (filters.value.status !== null) {
    result = result.filter(permission => permission.is_active === filters.value.status);
  }
  
  return result;
});

const paginatedPermissions = computed(() => {
  const start = (pagination.value.currentPage - 1) * pagination.value.perPage;
  const end = start + pagination.value.perPage;
  return filteredPermissions.value.slice(start, end);
});

const totalPages = computed(() => {
  return Math.ceil(filteredPermissions.value.length / pagination.value.perPage);
});

const filteredPermissionUsers = computed(() => {
  if (!userSearch.value) return permissionUsers.value;
  
  const search = userSearch.value.toLowerCase();
  return permissionUsers.value.filter(user => 
    user.username.toLowerCase().includes(search) ||
    user.email.toLowerCase().includes(search) ||
    user.full_name?.toLowerCase().includes(search)
  );
});

// 유틸리티 함수
const getCategoryIcon = (category: string): string => {
  const iconMap: Record<string, string> = {
    system: 'settings',
    user: 'person',
    menu: 'menu',
    permission: 'security',
    board: 'forum',
    content: 'article',
    other: 'category',
  };
  return iconMap[category] || 'circle';
};

const getCategoryColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    system: 'danger',
    user: 'primary',
    menu: 'info',
    permission: 'warning',
    board: 'success',
    content: 'secondary',
    other: 'textPrimary',
  };
  return colorMap[category] || 'primary';
};

const getCategoryLabel = (category: string): string => {
  const option = categoryOptions.find(opt => opt.value === category);
  return option?.text || category;
};

// 검증 규칙
const required = (value: string) => !!value || '필수 입력 항목입니다.';
const permissionCodeRule = (value: string) => {
  if (!value) return true;
  const pattern = /^[A-Z_]+$/;
  return pattern.test(value) || '권한 코드는 대문자와 언더스코어만 사용 가능합니다.';
};

// 메서드
const loadPermissions = async () => {
  try {
    loading.value = true;
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    permissions.value = [
      {
        id: 1,
        name: '사용자 조회',
        code: 'USER_READ',
        category: 'user',
        resource: 'users',
        action: 'read',
        description: '사용자 정보를 조회할 수 있는 권한',
        is_active: true,
        user_count: 15,
        created_at: '2024-01-15T09:00:00Z',
        updated_at: '2024-01-15T09:00:00Z',
      },
      {
        id: 2,
        name: '사용자 생성',
        code: 'USER_CREATE',
        category: 'user',
        resource: 'users',
        action: 'create',
        description: '새로운 사용자를 생성할 수 있는 권한',
        is_active: true,
        user_count: 8,
        created_at: '2024-01-15T09:00:00Z',
        updated_at: '2024-01-15T09:00:00Z',
      },
      {
        id: 3,
        name: '시스템 설정',
        code: 'SYSTEM_CONFIG',
        category: 'system',
        resource: 'system',
        action: 'config',
        description: '시스템 설정을 변경할 수 있는 권한',
        is_active: true,
        user_count: 3,
        created_at: '2024-01-15T09:00:00Z',
        updated_at: '2024-01-15T09:00:00Z',
      },
    ];
  } catch (error) {
    console.error('권한 목록 로드 실패:', error);
    initToast({
      message: '권한 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const openCreateModal = () => {
  resetPermissionForm();
  modals.value.permission = true;
};

const editPermission = (permission: Permission) => {
  permissionForm.value = {
    id: permission.id,
    name: permission.name,
    code: permission.code || '',
    category: permission.category || '',
    resource: permission.resource,
    action: permission.action,
    description: permission.description || '',
    is_active: permission.is_active || true,
  };
  modals.value.permission = true;
};

const savePermission = async () => {
  try {
    // 폼 검증
    if (!permissionFormRef.value?.validate()) {
      return;
    }
    
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const isEdit = !!permissionForm.value.id;
    
    if (isEdit) {
      // 수정
      const index = permissions.value.findIndex(p => p.id === permissionForm.value.id);
      if (index !== -1) {
        permissions.value[index] = {
          ...permissions.value[index],
          ...permissionForm.value,
          updated_at: new Date().toISOString(),
        };
      }
    } else {
      // 생성
      const newPermission: Permission = {
        ...permissionForm.value,
        id: Date.now(),
        resource: permissionForm.value.resource || 'default',
        action: permissionForm.value.action || 'read',
        user_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      permissions.value.unshift(newPermission);
    }
    
    initToast({
      message: `권한이 성공적으로 ${isEdit ? '수정' : '생성'}되었습니다.`,
      color: 'success',
    });
    
    closePermissionModal();
  } catch (error) {
    console.error('권한 저장 실패:', error);
    initToast({
      message: '권한 저장에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const togglePermissionStatus = async (permission: Permission) => {
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = permissions.value.findIndex(p => p.id === permission.id);
    if (index !== -1) {
      permissions.value[index].is_active = !permissions.value[index].is_active;
      permissions.value[index].updated_at = new Date().toISOString();
    }
    
    initToast({
      message: `권한이 ${permission.is_active ? '비활성화' : '활성화'}되었습니다.`,
      color: 'success',
    });
  } catch (error) {
    console.error('권한 상태 변경 실패:', error);
    initToast({
      message: '권한 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const deletePermission = async (permission: Permission) => {
  if (permission.user_count > 0) {
    initToast({
      message: '사용자가 보유한 권한은 삭제할 수 없습니다.',
      color: 'warning',
    });
    return;
  }
  
  if (!confirm(`'${permission.name}' 권한을 삭제하시겠습니까?`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = permissions.value.findIndex(p => p.id === permission.id);
    if (index !== -1) {
      permissions.value.splice(index, 1);
    }
    
    initToast({
      message: '권한이 삭제되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('권한 삭제 실패:', error);
    initToast({
      message: '권한 삭제에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const showPermissionUsers = async (permission: Permission) => {
  selectedPermission.value = permission;
  modals.value.users = true;
  
  try {
    loadingUsers.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    permissionUsers.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        full_name: '관리자',
        is_active: true,
        avatar: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        username: 'user1',
        email: 'user1@example.com',
        full_name: '사용자1',
        is_active: true,
        avatar: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
  } catch (error) {
    console.error('권한 사용자 목록 로드 실패:', error);
    initToast({
      message: '권한 사용자 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loadingUsers.value = false;
  }
};

const removeUserPermission = async (user: User) => {
  if (!confirm(`${user.full_name || user.username}님의 권한을 제거하시겠습니까?`)) {
    return;
  }
  
  try {
    loadingUsers.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = permissionUsers.value.findIndex(u => u.id === user.id);
    if (index !== -1) {
      permissionUsers.value.splice(index, 1);
    }
    
    // 권한의 사용자 수 업데이트
    if (selectedPermission.value) {
      const permissionIndex = permissions.value.findIndex(p => p.id === selectedPermission.value!.id);
      if (permissionIndex !== -1) {
        permissions.value[permissionIndex].user_count--;
      }
    }
    
    initToast({
      message: '사용자 권한이 제거되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('사용자 권한 제거 실패:', error);
    initToast({
      message: '사용자 권한 제거에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loadingUsers.value = false;
  }
};

const resetPermissionForm = () => {
  permissionForm.value = {
    id: null,
    name: '',
    code: '',
    category: '',
    resource: '',
    action: '',
    description: '',
    is_active: true,
  };
};

const closePermissionModal = () => {
  modals.value.permission = false;
  resetPermissionForm();
};

const resetFilters = () => {
  filters.value = {
    search: '',
    category: null,
    status: null,
  };
  pagination.value.currentPage = 1;
};

const exportPermissions = () => {
  // 권한 목록 내보내기 구현
  initToast({
    message: '권한 목록을 내보내는 기능은 준비 중입니다.',
    color: 'info',
  });
};

// 감시자
watch(() => filters.value, () => {
  pagination.value.currentPage = 1;
}, { deep: true });

// 라이프사이클
onMounted(() => {
  loadPermissions();
});
</script>

<style scoped>
.permission-management {
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

.permissions-card {
  margin-bottom: 1.5rem;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.table-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.total-count {
  font-weight: 500;
  color: #666;
}

.table-actions {
  display: flex;
  gap: 0.5rem;
}

.permission-name {
  display: flex;
  align-items: center;
}

.name-text {
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.form-grid {
  display: grid;
  gap: 1.5rem;
}

.form-row {
  display: flex;
  flex-direction: column;
}

.users-modal-content {
  max-height: 60vh;
  overflow-y: auto;
}

.users-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.users-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.user-search {
  width: 300px;
}

.mr-2 {
  margin-right: 0.5rem;
}

@media (max-width: 768px) {
  .permission-management {
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
  
  .filter-row {
    flex-direction: column;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .table-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .users-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .user-search {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .permission-management {
    padding: 0.75rem;
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
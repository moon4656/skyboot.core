<template>
  <div class="user-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="people" class="mr-2" />
            사용자 관리
          </h1>
          <p class="page-description">시스템 사용자 계정을 관리합니다.</p>
        </div>
        
        <div class="header-actions">
          <VaButton
            color="primary"
            icon="add"
            @click="openCreateModal"
          >
            사용자 추가
          </VaButton>
        </div>
      </div>
    </div>

    <!-- 검색 및 필터 -->
    <VaCard class="filter-card">
      <VaCardContent>
        <div class="filter-section">
          <div class="filter-row">
            <div class="filter-item">
              <VaInput
                v-model="searchQuery"
                placeholder="사용자명, 이메일로 검색..."
                clearable
                @input="handleSearch"
              >
                <template #prepend>
                  <VaIcon name="search" />
                </template>
              </VaInput>
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="statusFilter"
                :options="statusOptions"
                placeholder="상태 필터"
                clearable
                @update:model-value="handleFilter"
              />
            </div>
            
            <div class="filter-item">
              <VaSelect
                v-model="roleFilter"
                :options="roleOptions"
                placeholder="역할 필터"
                clearable
                @update:model-value="handleFilter"
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

    <!-- 사용자 테이블 -->
    <VaCard class="table-card">
      <VaCardContent>
        <VaDataTable
          :items="filteredUsers"
          :columns="columns"
          :loading="loading"
          :per-page="perPage"
          :current-page="currentPage"
          @update:current-page="currentPage = $event"
          striped
          hoverable
        >
          <!-- 아바타 컬럼 -->
          <template #cell(avatar)="{ rowData }">
            <VaAvatar
              :src="rowData.avatar"
              :fallback-text="rowData.username.charAt(0).toUpperCase()"
              size="small"
            />
          </template>
          
          <!-- 상태 컬럼 -->
          <template #cell(status)="{ rowData }">
            <VaChip
              :color="getStatusColor(rowData.is_active)"
              size="small"
              outline
            >
              {{ rowData.is_active ? '활성' : '비활성' }}
            </VaChip>
          </template>
          
          <!-- 역할 컬럼 -->
          <template #cell(roles)="{ rowData }">
            <div class="roles-container">
              <VaChip
                v-for="role in rowData.roles"
                :key="role.id"
                :color="getRoleColor(role.name)"
                size="small"
                class="mr-1 mb-1"
              >
                {{ role.display_name }}
              </VaChip>
            </div>
          </template>
          
          <!-- 마지막 로그인 컬럼 -->
          <template #cell(last_login)="{ rowData }">
            <span v-if="rowData.last_login">
              {{ formatDateTime(rowData.last_login) }}
            </span>
            <span v-else class="text-muted">로그인 기록 없음</span>
          </template>
          
          <!-- 액션 컬럼 -->
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <VaButton
                preset="secondary"
                size="small"
                icon="edit"
                @click="openEditModal(rowData)"
              />
              
              <VaButton
                preset="secondary"
                size="small"
                icon="security"
                @click="openPermissionModal(rowData)"
              />
              
              <VaButton
                :preset="rowData.is_active ? 'secondary' : 'primary'"
                :color="rowData.is_active ? 'warning' : 'success'"
                size="small"
                :icon="rowData.is_active ? 'block' : 'check_circle'"
                @click="toggleUserStatus(rowData)"
              />
              
              <VaButton
                preset="secondary"
                color="danger"
                size="small"
                icon="delete"
                @click="confirmDelete(rowData)"
              />
            </div>
          </template>
        </VaDataTable>
        
        <!-- 페이지네이션 -->
        <div class="pagination-container">
          <VaPagination
            v-model="currentPage"
            :pages="totalPages"
            :visible-pages="5"
          />
          
          <div class="pagination-info">
            <VaSelect
              v-model="perPage"
              :options="perPageOptions"
              style="width: 80px;"
            />
            <span class="ml-2">개씩 보기</span>
          </div>
        </div>
      </VaCardContent>
    </VaCard>

    <!-- 사용자 생성/수정 모달 -->
    <VaModal
      v-model="showUserModal"
      :title="isEditMode ? '사용자 수정' : '사용자 생성'"
      size="large"
      @ok="saveUser"
      @cancel="closeUserModal"
    >
      <VaForm ref="userForm" @submit.prevent="saveUser">
        <div class="modal-content">
          <div class="form-row">
            <div class="form-col">
              <VaInput
                v-model="userForm.username"
                label="사용자명"
                :rules="[required, minLength(3)]"
                required
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="userForm.email"
                label="이메일"
                type="email"
                :rules="[required, emailRule]"
                required
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaInput
                v-model="userForm.first_name"
                label="이름"
                :rules="[required]"
                required
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="userForm.last_name"
                label="성"
                :rules="[required]"
                required
              />
            </div>
          </div>
          
          <div class="form-row" v-if="!isEditMode">
            <div class="form-col">
              <VaInput
                v-model="userForm.password"
                label="비밀번호"
                type="password"
                :rules="[required, minLength(8)]"
                required
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="userForm.confirm_password"
                label="비밀번호 확인"
                type="password"
                :rules="[required, passwordMatch]"
                required
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaSelect
                v-model="userForm.roles"
                :options="availableRoles"
                label="역할"
                multiple
                text-by="display_name"
                value-by="id"
                required
              />
            </div>
            
            <div class="form-col">
              <VaSelect
                v-model="userForm.organization_id"
                :options="organizations"
                label="조직"
                text-by="name"
                value-by="id"
                clearable
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaTextarea
                v-model="userForm.description"
                label="설명"
                rows="3"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaCheckbox
                v-model="userForm.is_active"
                label="활성 상태"
              />
            </div>
            
            <div class="form-col">
              <VaCheckbox
                v-model="userForm.email_verified"
                label="이메일 인증됨"
              />
            </div>
          </div>
        </div>
      </VaForm>
    </VaModal>

    <!-- 권한 관리 모달 -->
    <VaModal
      v-model="showPermissionModal"
      title="사용자 권한 관리"
      size="large"
      @ok="savePermissions"
      @cancel="closePermissionModal"
    >
      <div class="permission-content" v-if="selectedUser">
        <div class="user-info">
          <VaAvatar
            :src="selectedUser.avatar"
            :fallback-text="selectedUser.username.charAt(0).toUpperCase()"
            size="large"
            class="mr-3"
          />
          <div>
            <h3>{{ selectedUser.username }}</h3>
            <p class="text-muted">{{ selectedUser.email }}</p>
          </div>
        </div>
        
        <VaDivider />
        
        <div class="permission-section">
          <h4>역할 권한</h4>
          <div class="role-permissions">
            <div
              v-for="role in selectedUser.roles"
              :key="role.id"
              class="role-item"
            >
              <VaChip
                :color="getRoleColor(role.name)"
                class="mb-2"
              >
                {{ role.display_name }}
              </VaChip>
              
              <div class="permission-list">
                <VaChip
                  v-for="permission in role.permissions"
                  :key="permission.id"
                  size="small"
                  outline
                  class="mr-1 mb-1"
                >
                  {{ permission.display_name }}
                </VaChip>
              </div>
            </div>
          </div>
        </div>
        
        <div class="permission-section">
          <h4>추가 권한</h4>
          <VaSelect
            v-model="additionalPermissions"
            :options="availablePermissions"
            multiple
            text-by="display_name"
            value-by="id"
            placeholder="추가 권한 선택"
          />
        </div>
      </div>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vuestic-ui';
import { authAPI } from '../../api/client';
import type { User, Role, Permission, Organization } from '../../types/auth';

const { init: notify } = useToast();

// 상태 관리
const loading = ref(false);
const users = ref<User[]>([]);
const availableRoles = ref<Role[]>([]);
const availablePermissions = ref<Permission[]>([]);
const organizations = ref<Organization[]>([]);

// 검색 및 필터
const searchQuery = ref('');
const statusFilter = ref<boolean | null>(null);
const roleFilter = ref<string | null>(null);

// 페이지네이션
const currentPage = ref(1);
const perPage = ref(10);
const perPageOptions = [10, 20, 50, 100];

// 모달 상태
const showUserModal = ref(false);
const showPermissionModal = ref(false);
const isEditMode = ref(false);
const selectedUser = ref<User | null>(null);
const additionalPermissions = ref<number[]>([]);

// 폼 데이터
const userForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  password: '',
  confirm_password: '',
  roles: [] as number[],
  organization_id: null as number | null,
  description: '',
  is_active: true,
  email_verified: false,
});

// 테이블 컬럼 정의
const columns = [
  { key: 'avatar', label: '', width: '60px', sortable: false },
  { key: 'username', label: '사용자명', sortable: true },
  { key: 'email', label: '이메일', sortable: true },
  { key: 'first_name', label: '이름', sortable: true },
  { key: 'last_name', label: '성', sortable: true },
  { key: 'roles', label: '역할', sortable: false },
  { key: 'status', label: '상태', sortable: true },
  { key: 'last_login', label: '마지막 로그인', sortable: true },
  { key: 'actions', label: '작업', width: '200px', sortable: false },
];

// 필터 옵션
const statusOptions = [
  { text: '활성', value: true },
  { text: '비활성', value: false },
];

const roleOptions = computed(() => {
  return availableRoles.value.map(role => ({
    text: role.display_name,
    value: role.name,
  }));
});

// 필터링된 사용자 목록
const filteredUsers = computed(() => {
  let result = users.value;
  
  // 검색 필터
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    result = result.filter(user => 
      user.username.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.first_name.toLowerCase().includes(query) ||
      user.last_name.toLowerCase().includes(query)
    );
  }
  
  // 상태 필터
  if (statusFilter.value !== null) {
    result = result.filter(user => user.is_active === statusFilter.value);
  }
  
  // 역할 필터
  if (roleFilter.value) {
    result = result.filter(user => 
      user.roles.some(role => role.name === roleFilter.value)
    );
  }
  
  return result;
});

// 총 페이지 수
const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / perPage.value);
});

// 유효성 검사 규칙
const required = (value: string) => !!value || '필수 입력 항목입니다.';
const minLength = (min: number) => (value: string) => 
  value.length >= min || `최소 ${min}자 이상 입력해주세요.`;
const emailRule = (value: string) => {
  const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return pattern.test(value) || '올바른 이메일 형식이 아닙니다.';
};
const passwordMatch = (value: string) => 
  value === userForm.value.password || '비밀번호가 일치하지 않습니다.';

// 상태 색상 반환
const getStatusColor = (isActive: boolean) => {
  return isActive ? 'success' : 'danger';
};

// 역할 색상 반환
const getRoleColor = (roleName: string) => {
  const colorMap: Record<string, string> = {
    'admin': 'danger',
    'manager': 'warning',
    'user': 'info',
    'guest': 'secondary',
  };
  return colorMap[roleName] || 'primary';
};

// 날짜 포맷팅
const formatDateTime = (dateString: string) => {
  return new Date(dateString).toLocaleString('ko-KR');
};

// 데이터 로드
const loadUsers = async () => {
  try {
    loading.value = true;
    const response = await authAPI.get('/admin/users');
    users.value = response.data;
  } catch (error) {
    notify({
      message: '사용자 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const loadRoles = async () => {
  try {
    const response = await authAPI.get('/admin/roles');
    availableRoles.value = response.data;
  } catch (error) {
    console.error('역할 목록 로드 실패:', error);
  }
};

const loadPermissions = async () => {
  try {
    const response = await authAPI.get('/admin/permissions');
    availablePermissions.value = response.data;
  } catch (error) {
    console.error('권한 목록 로드 실패:', error);
  }
};

const loadOrganizations = async () => {
  try {
    const response = await authAPI.get('/admin/organizations');
    organizations.value = response.data;
  } catch (error) {
    console.error('조직 목록 로드 실패:', error);
  }
};

// 검색 및 필터 핸들러
const handleSearch = () => {
  currentPage.value = 1;
};

const handleFilter = () => {
  currentPage.value = 1;
};

const resetFilters = () => {
  searchQuery.value = '';
  statusFilter.value = null;
  roleFilter.value = null;
  currentPage.value = 1;
};

// 모달 관리
const openCreateModal = () => {
  isEditMode.value = false;
  resetUserForm();
  showUserModal.value = true;
};

const openEditModal = (user: User) => {
  isEditMode.value = true;
  selectedUser.value = user;
  fillUserForm(user);
  showUserModal.value = true;
};

const closeUserModal = () => {
  showUserModal.value = false;
  resetUserForm();
  selectedUser.value = null;
};

const openPermissionModal = (user: User) => {
  selectedUser.value = user;
  additionalPermissions.value = user.additional_permissions?.map(p => p.id) || [];
  showPermissionModal.value = true;
};

const closePermissionModal = () => {
  showPermissionModal.value = false;
  selectedUser.value = null;
  additionalPermissions.value = [];
};

// 폼 관리
const resetUserForm = () => {
  userForm.value = {
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    confirm_password: '',
    roles: [],
    organization_id: null,
    description: '',
    is_active: true,
    email_verified: false,
  };
};

const fillUserForm = (user: User) => {
  userForm.value = {
    username: user.username,
    email: user.email,
    first_name: user.first_name,
    last_name: user.last_name,
    password: '',
    confirm_password: '',
    roles: user.roles.map(role => role.id),
    organization_id: user.organization_id,
    description: user.description || '',
    is_active: user.is_active,
    email_verified: user.email_verified,
  };
};

// CRUD 작업
const saveUser = async () => {
  try {
    const userData = { ...userForm.value };
    delete userData.confirm_password;
    
    if (isEditMode.value && selectedUser.value) {
      if (!userData.password) {
        delete userData.password;
      }
      await authAPI.put(`/admin/users/${selectedUser.value.id}`, userData);
      notify({
        message: '사용자가 성공적으로 수정되었습니다.',
        color: 'success',
      });
    } else {
      await authAPI.post('/admin/users', userData);
      notify({
        message: '사용자가 성공적으로 생성되었습니다.',
        color: 'success',
      });
    }
    
    closeUserModal();
    await loadUsers();
  } catch (error: any) {
    notify({
      message: error.response?.data?.detail || '사용자 저장에 실패했습니다.',
      color: 'danger',
    });
  }
};

const toggleUserStatus = async (user: User) => {
  try {
    await authAPI.patch(`/admin/users/${user.id}/status`, {
      is_active: !user.is_active,
    });
    
    notify({
      message: `사용자가 ${!user.is_active ? '활성화' : '비활성화'}되었습니다.`,
      color: 'success',
    });
    
    await loadUsers();
  } catch (error) {
    notify({
      message: '사용자 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  }
};

const confirmDelete = (user: User) => {
  if (confirm(`정말로 사용자 "${user.username}"을(를) 삭제하시겠습니까?`)) {
    deleteUser(user);
  }
};

const deleteUser = async (user: User) => {
  try {
    await authAPI.delete(`/admin/users/${user.id}`);
    notify({
      message: '사용자가 성공적으로 삭제되었습니다.',
      color: 'success',
    });
    await loadUsers();
  } catch (error) {
    notify({
      message: '사용자 삭제에 실패했습니다.',
      color: 'danger',
    });
  }
};

const savePermissions = async () => {
  try {
    if (!selectedUser.value) return;
    
    await authAPI.patch(`/admin/users/${selectedUser.value.id}/permissions`, {
      additional_permissions: additionalPermissions.value,
    });
    
    notify({
      message: '사용자 권한이 성공적으로 업데이트되었습니다.',
      color: 'success',
    });
    
    closePermissionModal();
    await loadUsers();
  } catch (error) {
    notify({
      message: '권한 업데이트에 실패했습니다.',
      color: 'danger',
    });
  }
};

// 컴포넌트 마운트
onMounted(async () => {
  await Promise.all([
    loadUsers(),
    loadRoles(),
    loadPermissions(),
    loadOrganizations(),
  ]);
});
</script>

<style scoped>
.user-management {
  padding: 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem 0;
  display: flex;
  align-items: center;
}

.page-description {
  color: #666;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.filter-card {
  margin-bottom: 1.5rem;
}

.filter-section {
  padding: 0;
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

.filter-actions {
  display: flex;
  gap: 0.5rem;
}

.table-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.roles-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e0e0e0;
}

.pagination-info {
  display: flex;
  align-items: center;
}

.modal-content {
  padding: 1rem 0;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.form-col {
  flex: 1;
}

.permission-content {
  padding: 1rem 0;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.user-info h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.permission-section {
  margin-bottom: 1.5rem;
}

.permission-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #333;
}

.role-permissions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-item {
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
}

.permission-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.text-muted {
  color: #666;
}

.mr-1 {
  margin-right: 0.25rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mr-3 {
  margin-right: 0.75rem;
}

.mb-1 {
  margin-bottom: 0.25rem;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .user-management {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-row {
    flex-direction: column;
  }
  
  .filter-item {
    min-width: auto;
  }
  
  .form-row {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
  
  .pagination-container {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
}
</style>
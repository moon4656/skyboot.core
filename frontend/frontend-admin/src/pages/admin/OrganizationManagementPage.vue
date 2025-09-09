<template>
  <div class="organization-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="account_tree" class="mr-2" />
            조직 관리
          </h1>
          <p class="page-description">
            조직 구조를 관리하고 부서별 사용자를 배치합니다.
          </p>
        </div>
        
        <div class="header-actions">
          <VaButton
            preset="secondary"
            icon="unfold_more"
            @click="expandAll"
          >
            전체 펼치기
          </VaButton>
          
          <VaButton
            preset="secondary"
            icon="unfold_less"
            @click="collapseAll"
          >
            전체 접기
          </VaButton>
          
          <VaButton
            preset="primary"
            icon="add"
            @click="openCreateModal"
          >
            조직 추가
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
                placeholder="조직명, 설명 검색..."
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
                v-model="filters.type"
                :options="typeOptions"
                placeholder="조직 유형 선택"
                clearable
                class="type-select"
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
    
    <!-- 조직 트리 -->
    <VaCard class="organization-tree-card">
      <VaCardContent>
        <div class="tree-header">
          <div class="tree-info">
            <span class="total-count">총 {{ totalOrganizations }}개 조직</span>
            <span class="active-count">활성 {{ activeOrganizations }}개</span>
          </div>
          
          <div class="tree-actions">
            <VaButton
              preset="secondary"
              icon="download"
              @click="exportOrganizations"
            >
              내보내기
            </VaButton>
          </div>
        </div>
        
        <div class="organization-tree">
          <div v-if="loading" class="loading-container">
            <VaProgressCircular indeterminate />
            <span class="loading-text">조직 구조를 불러오는 중...</span>
          </div>
          
          <div v-else-if="filteredOrganizations.length === 0" class="empty-state">
            <VaIcon name="account_tree" size="4rem" color="secondary" />
            <h3>조직이 없습니다</h3>
            <p>새로운 조직을 추가해보세요.</p>
            <VaButton
              preset="primary"
              icon="add"
              @click="openCreateModal"
            >
              조직 추가
            </VaButton>
          </div>
          
          <OrganizationTreeNode
            v-for="org in rootOrganizations"
            :key="org.id"
            :organization="org"
            :level="0"
            @edit="editOrganization"
            @delete="deleteOrganization"
            @add-child="addChildOrganization"
            @toggle-status="toggleOrganizationStatus"
            @view-users="viewOrganizationUsers"
          />
        </div>
      </VaCardContent>
    </VaCard>
    
    <!-- 조직 생성/수정 모달 -->
    <VaModal
      v-model="modals.organization"
      title="조직 정보"
      size="large"
      @ok="saveOrganization"
      @cancel="closeOrganizationModal"
    >
      <VaForm ref="organizationForm" @submit.prevent="saveOrganization">
        <div class="form-grid">
          <div class="form-row">
            <VaInput
              v-model="organizationForm.name"
              label="조직명"
              placeholder="조직명을 입력하세요"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="organizationForm.code"
              label="조직 코드"
              placeholder="ORG001"
              :rules="[required, organizationCodeRule]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="organizationForm.type"
              label="조직 유형"
              :options="typeOptions"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaSelect
              v-model="organizationForm.parent_id"
              label="상위 조직"
              :options="parentOptions"
              placeholder="상위 조직을 선택하세요 (선택사항)"
              clearable
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="organizationForm.manager_name"
              label="담당자명"
              placeholder="담당자명을 입력하세요"
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="organizationForm.manager_email"
              label="담당자 이메일"
              placeholder="manager@example.com"
              type="email"
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model="organizationForm.manager_phone"
              label="담당자 전화번호"
              placeholder="010-1234-5678"
            />
          </div>
          
          <div class="form-row">
            <VaInput
              v-model.number="organizationForm.sort_order"
              label="정렬 순서"
              type="number"
              :min="0"
              :rules="[required]"
              required
            />
          </div>
          
          <div class="form-row">
            <VaTextarea
              v-model="organizationForm.description"
              label="설명"
              placeholder="조직에 대한 설명을 입력하세요"
              :min-rows="3"
              :max-rows="5"
            />
          </div>
          
          <div class="form-row">
            <VaCheckbox
              v-model="organizationForm.is_active"
              label="활성 상태"
            />
          </div>
        </div>
      </VaForm>
    </VaModal>
    
    <!-- 조직 사용자 목록 모달 -->
    <VaModal
      v-model="modals.users"
      title="조직 구성원"
      size="large"
      hide-default-actions
    >
      <div class="users-modal-content">
        <div class="users-header">
          <h3>{{ selectedOrganization?.name }} 구성원</h3>
          <div class="users-actions">
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
            
            <VaButton
              preset="primary"
              icon="person_add"
              @click="openAddUserModal"
            >
              사용자 추가
            </VaButton>
          </div>
        </div>
        
        <VaDataTable
          :items="filteredOrganizationUsers"
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
          
          <template #cell(position)="{ rowData }">
            <VaChip
              v-if="rowData.position"
              color="info"
              size="small"
              outline
            >
              {{ rowData.position }}
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
          
          <template #cell(actions)="{ rowData }">
            <div class="action-buttons">
              <VaButton
                preset="secondary"
                size="small"
                icon="edit"
                @click="editUserPosition(rowData)"
                title="직책 수정"
              />
              
              <VaButton
                preset="secondary"
                color="danger"
                size="small"
                icon="remove_circle"
                @click="removeUserFromOrganization(rowData)"
                title="조직에서 제거"
              />
            </div>
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
    
    <!-- 사용자 추가 모달 -->
    <VaModal
      v-model="modals.addUser"
      title="조직에 사용자 추가"
      size="medium"
      @ok="addUserToOrganization"
      @cancel="modals.addUser = false"
    >
      <div class="add-user-form">
        <VaSelect
          v-model="addUserForm.user_id"
          label="사용자 선택"
          :options="availableUsers"
          text-by="full_name"
          value-by="id"
          placeholder="사용자를 선택하세요"
          :rules="[required]"
          required
        />
        
        <VaInput
          v-model="addUserForm.position"
          label="직책"
          placeholder="직책을 입력하세요 (선택사항)"
          class="mt-4"
        />
      </div>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useToast } from 'vuestic-ui';
import OrganizationTreeNode from '../../components/admin/OrganizationTreeNode.vue';
import type { Organization, User } from '../../types/auth';

// 인터페이스
interface OrganizationForm {
  id: number | null;
  name: string;
  code: string;
  type: 'company' | 'department' | 'team' | 'group';
  parent_id: number | null;
  manager_name: string;
  manager_email: string;
  manager_phone: string;
  description: string;
  sort_order: number;
  is_active: boolean;
}

// 컴포저블
const { init: initToast } = useToast();

// 상태 관리
const loading = ref(false);
const loadingUsers = ref(false);
const organizations = ref<Organization[]>([]);
const organizationUsers = ref<User[]>([]);
const availableUsers = ref<User[]>([]);
const selectedOrganization = ref<Organization | null>(null);
const userSearch = ref('');

// 필터 상태
const filters = ref({
  search: '',
  type: null as string | null,
  status: null as boolean | null,
});

// 모달 상태
const modals = ref({
  organization: false,
  users: false,
  addUser: false,
});

// 폼 상태
const organizationForm = ref<OrganizationForm>({
  id: null as number | null,
  name: '',
  code: '',
  type: 'company',
  parent_id: null as number | null,
  manager_name: '',
  manager_email: '',
  manager_phone: '',
  description: '',
  sort_order: 0,
  is_active: true,
});

const addUserForm = ref({
  user_id: null as number | null,
  position: '',
});

// 폼 참조
const organizationFormRef = ref();

// 옵션 데이터
const typeOptions = [
  { text: '회사', value: 'company' },
  { text: '부서', value: 'department' },
  { text: '팀', value: 'team' },
  { text: '그룹', value: 'group' },
];

const statusOptions = [
  { text: '활성', value: true },
  { text: '비활성', value: false },
];

// 테이블 컬럼
const userColumns = [
  { key: 'avatar', label: '', width: '50px' },
  { key: 'username', label: '사용자명', sortable: true },
  { key: 'full_name', label: '이름', sortable: true },
  { key: 'email', label: '이메일', sortable: true },
  { key: 'position', label: '직책' },
  { key: 'is_active', label: '상태', sortable: true },
  { key: 'actions', label: '작업', width: '100px' },
];

// 계산된 속성
const filteredOrganizations = computed(() => {
  let result = [...organizations.value];
  
  if (filters.value.search) {
    const search = filters.value.search.toLowerCase();
    result = result.filter(org => 
      org.name.toLowerCase().includes(search) ||
      org.code.toLowerCase().includes(search) ||
      org.description?.toLowerCase().includes(search)
    );
  }
  
  if (filters.value.type) {
    result = result.filter(org => org.type === filters.value.type);
  }
  
  if (filters.value.status !== null) {
    result = result.filter(org => org.is_active === filters.value.status);
  }
  
  return result;
});

const rootOrganizations = computed(() => {
  return buildOrganizationTree(filteredOrganizations.value);
});

const totalOrganizations = computed(() => organizations.value.length);

const activeOrganizations = computed(() => {
  return organizations.value.filter(org => org.is_active).length;
});

const parentOptions = computed(() => {
  const currentId = organizationForm.value.id;
  return organizations.value
    .filter(org => org.id !== currentId && org.is_active)
    .map(org => ({
      text: `${org.name} (${org.code})`,
      value: org.id,
    }));
});

const filteredOrganizationUsers = computed(() => {
  if (!userSearch.value) return organizationUsers.value;
  
  const search = userSearch.value.toLowerCase();
  return organizationUsers.value.filter(user => 
    user.username.toLowerCase().includes(search) ||
    user.email.toLowerCase().includes(search) ||
    user.full_name?.toLowerCase().includes(search)
  );
});

// 유틸리티 함수
const buildOrganizationTree = (orgs: Organization[]): Organization[] => {
  const orgMap = new Map<number, Organization & { children: Organization[] }>();
  const roots: (Organization & { children: Organization[] })[] = [];
  
  // 모든 조직을 맵에 추가하고 children 배열 초기화
  orgs.forEach(org => {
    orgMap.set(org.id, { ...org, children: [] });
  });
  
  // 트리 구조 구성
  orgs.forEach(org => {
    const orgWithChildren = orgMap.get(org.id)!;
    
    if (org.parent_id && orgMap.has(org.parent_id)) {
      const parent = orgMap.get(org.parent_id)!;
      parent.children.push(orgWithChildren);
    } else {
      roots.push(orgWithChildren);
    }
  });
  
  // 정렬
  const sortOrganizations = (orgs: any[]) => {
    orgs.sort((a, b) => a.sort_order - b.sort_order);
    orgs.forEach(org => {
      if (org.children && org.children.length > 0) {
        sortOrganizations(org.children);
      }
    });
  };
  
  sortOrganizations(roots);
  return roots;
};

// 검증 규칙
const required = (value: string | number) => !!value || '필수 입력 항목입니다.';
const organizationCodeRule = (value: string) => {
  if (!value) return true;
  const pattern = /^[A-Z0-9_]+$/;
  return pattern.test(value) || '조직 코드는 대문자, 숫자, 언더스코어만 사용 가능합니다.';
};

// 메서드
const loadOrganizations = async () => {
  try {
    loading.value = true;
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    organizations.value = [
      {
        id: 1,
        name: '본사',
        code: 'HQ',
        type: 'company',
        parent_id: null,
        manager_name: '김대표',
        manager_email: 'ceo@company.com',
        manager_phone: '02-1234-5678',
        description: '회사 본사',
        sort_order: 1,
        is_active: true,
        user_count: 25,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        name: '개발부',
        code: 'DEV',
        type: 'department',
        parent_id: 1,
        manager_name: '이부장',
        manager_email: 'dev.manager@company.com',
        manager_phone: '02-1234-5679',
        description: '소프트웨어 개발 부서',
        sort_order: 1,
        is_active: true,
        user_count: 12,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 3,
        name: '프론트엔드팀',
        code: 'FE_TEAM',
        type: 'team',
        parent_id: 2,
        manager_name: '박팀장',
        manager_email: 'fe.lead@company.com',
        manager_phone: '02-1234-5680',
        description: '프론트엔드 개발팀',
        sort_order: 1,
        is_active: true,
        user_count: 6,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
  } catch (error) {
    console.error('조직 목록 로드 실패:', error);
    initToast({
      message: '조직 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const expandAll = () => {
  document.dispatchEvent(new CustomEvent('expand-all-organizations'));
};

const collapseAll = () => {
  document.dispatchEvent(new CustomEvent('collapse-all-organizations'));
};

const openCreateModal = () => {
  resetOrganizationForm();
  modals.value.organization = true;
};

const editOrganization = (organization: Organization) => {
  organizationForm.value = {
    id: organization.id,
    name: organization.name,
    code: organization.code,
    type: organization.type,
    parent_id: organization.parent_id,
    manager_name: organization.manager_name || '',
    manager_email: organization.manager_email || '',
    manager_phone: organization.manager_phone || '',
    description: organization.description || '',
    sort_order: organization.sort_order,
    is_active: organization.is_active,
  };
  modals.value.organization = true;
};

const addChildOrganization = (parentOrganization: Organization) => {
  resetOrganizationForm();
  organizationForm.value.parent_id = parentOrganization.id;
  modals.value.organization = true;
};

const saveOrganization = async () => {
  try {
    // 폼 검증
    if (!organizationFormRef.value?.validate()) {
      return;
    }
    
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const isEdit = !!organizationForm.value.id;
    
    if (isEdit) {
      // 수정
      const index = organizations.value.findIndex(org => org.id === organizationForm.value.id);
      if (index !== -1) {
        organizations.value[index] = {
          ...organizations.value[index],
          ...organizationForm.value,
          updated_at: new Date().toISOString(),
        };
      }
    } else {
      // 생성
      const newOrganization: Organization = {
        ...organizationForm.value,
        id: Date.now(),
        user_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      organizations.value.push(newOrganization);
    }
    
    initToast({
      message: `조직이 성공적으로 ${isEdit ? '수정' : '생성'}되었습니다.`,
      color: 'success',
    });
    
    closeOrganizationModal();
  } catch (error) {
    console.error('조직 저장 실패:', error);
    initToast({
      message: '조직 저장에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const toggleOrganizationStatus = async (organization: Organization) => {
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = organizations.value.findIndex(org => org.id === organization.id);
    if (index !== -1) {
      organizations.value[index].is_active = !organizations.value[index].is_active;
      organizations.value[index].updated_at = new Date().toISOString();
    }
    
    initToast({
      message: `조직이 ${organization.is_active ? '비활성화' : '활성화'}되었습니다.`,
      color: 'success',
    });
  } catch (error) {
    console.error('조직 상태 변경 실패:', error);
    initToast({
      message: '조직 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const deleteOrganization = async (organization: Organization) => {
  if (organization.user_count > 0) {
    initToast({
      message: '구성원이 있는 조직은 삭제할 수 없습니다.',
      color: 'warning',
    });
    return;
  }
  
  // 하위 조직 확인
  const hasChildren = organizations.value.some(org => org.parent_id === organization.id);
  if (hasChildren) {
    initToast({
      message: '하위 조직이 있는 조직은 삭제할 수 없습니다.',
      color: 'warning',
    });
    return;
  }
  
  if (!confirm(`'${organization.name}' 조직을 삭제하시겠습니까?`)) {
    return;
  }
  
  try {
    loading.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = organizations.value.findIndex(org => org.id === organization.id);
    if (index !== -1) {
      organizations.value.splice(index, 1);
    }
    
    initToast({
      message: '조직이 삭제되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('조직 삭제 실패:', error);
    initToast({
      message: '조직 삭제에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
  }
};

const viewOrganizationUsers = async (organization: Organization) => {
  selectedOrganization.value = organization;
  modals.value.users = true;
  
  try {
    loadingUsers.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 목 데이터
    organizationUsers.value = [
      {
        id: 1,
        username: 'admin',
        email: 'admin@company.com',
        full_name: '관리자',
        position: '시스템 관리자',
        is_active: true,
        avatar: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 2,
        username: 'developer1',
        email: 'dev1@company.com',
        full_name: '개발자1',
        position: '선임 개발자',
        is_active: true,
        avatar: null,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
  } catch (error) {
    console.error('조직 사용자 목록 로드 실패:', error);
    initToast({
      message: '조직 사용자 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loadingUsers.value = false;
  }
};

const openAddUserModal = async () => {
  modals.value.addUser = true;
  
  try {
    // 사용 가능한 사용자 목록 로드
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 목 데이터 (조직에 속하지 않은 사용자들)
    availableUsers.value = [
      {
        id: 3,
        username: 'user1',
        email: 'user1@company.com',
        full_name: '사용자1',
        avatar: null,
        position: '',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
      {
        id: 4,
        username: 'user2',
        email: 'user2@company.com',
        full_name: '사용자2',
        avatar: null,
        position: '',
        is_active: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      },
    ];
  } catch (error) {
    console.error('사용 가능한 사용자 목록 로드 실패:', error);
  }
};

const addUserToOrganization = async () => {
  if (!addUserForm.value.user_id) {
    initToast({
      message: '사용자를 선택해주세요.',
      color: 'warning',
    });
    return;
  }
  
  try {
    loadingUsers.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const selectedUser = availableUsers.value.find(user => user.id === addUserForm.value.user_id);
    if (selectedUser) {
      const newUser = {
        ...selectedUser,
        position: addUserForm.value.position,
      };
      organizationUsers.value.push(newUser);
      
      // 조직의 사용자 수 업데이트
      if (selectedOrganization.value) {
        const orgIndex = organizations.value.findIndex(org => org.id === selectedOrganization.value!.id);
        if (orgIndex !== -1) {
          organizations.value[orgIndex].user_count++;
        }
      }
    }
    
    initToast({
      message: '사용자가 조직에 추가되었습니다.',
      color: 'success',
    });
    
    modals.value.addUser = false;
    addUserForm.value = { user_id: null, position: '' };
  } catch (error) {
    console.error('사용자 추가 실패:', error);
    initToast({
      message: '사용자 추가에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loadingUsers.value = false;
  }
};

const editUserPosition = (user: User) => {
  const newPosition = prompt('새로운 직책을 입력하세요:', user.position || '');
  if (newPosition !== null) {
    const index = organizationUsers.value.findIndex(u => u.id === user.id);
    if (index !== -1) {
      organizationUsers.value[index].position = newPosition;
      initToast({
        message: '직책이 수정되었습니다.',
        color: 'success',
      });
    }
  }
};

const removeUserFromOrganization = async (user: User) => {
  if (!confirm(`${user.full_name || user.username}님을 조직에서 제거하시겠습니까?`)) {
    return;
  }
  
  try {
    loadingUsers.value = true;
    
    // API 호출 시뮬레이션
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = organizationUsers.value.findIndex(u => u.id === user.id);
    if (index !== -1) {
      organizationUsers.value.splice(index, 1);
    }
    
    // 조직의 사용자 수 업데이트
    if (selectedOrganization.value) {
      const orgIndex = organizations.value.findIndex(org => org.id === selectedOrganization.value!.id);
      if (orgIndex !== -1) {
        organizations.value[orgIndex].user_count--;
      }
    }
    
    initToast({
      message: '사용자가 조직에서 제거되었습니다.',
      color: 'success',
    });
  } catch (error) {
    console.error('사용자 제거 실패:', error);
    initToast({
      message: '사용자 제거에 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loadingUsers.value = false;
  }
};

const resetOrganizationForm = () => {
  organizationForm.value = {
    id: null,
    name: '',
    code: '',
    type: 'company',
    parent_id: null,
    manager_name: '',
    manager_email: '',
    manager_phone: '',
    description: '',
    sort_order: 0,
    is_active: true,
  };
};

const closeOrganizationModal = () => {
  modals.value.organization = false;
  resetOrganizationForm();
};

const resetFilters = () => {
  filters.value = {
    search: '',
    type: null,
    status: null,
  };
};

const exportOrganizations = () => {
  // 조직 목록 내보내기 구현
  initToast({
    message: '조직 목록을 내보내는 기능은 준비 중입니다.',
    color: 'info',
  });
};

// 감시자
watch(() => filters.value, () => {
  // 필터 변경 시 추가 로직
}, { deep: true });

// 라이프사이클
onMounted(() => {
  loadOrganizations();
});
</script>

<style scoped>
.organization-management {
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

.organization-tree-card {
  margin-bottom: 1.5rem;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.tree-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.total-count,
.active-count {
  font-weight: 500;
  color: #666;
}

.tree-actions {
  display: flex;
  gap: 0.5rem;
}

.organization-tree {
  min-height: 200px;
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

.users-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.user-search {
  width: 300px;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.add-user-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.mt-4 {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .organization-management {
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
  
  .tree-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .users-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .users-actions {
    flex-direction: column;
  }
  
  .user-search {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .organization-management {
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
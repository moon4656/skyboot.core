<template>
  <div class="menu-management">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <VaIcon name="menu" class="mr-2" />
            메뉴 관리
          </h1>
          <p class="page-description">시스템 메뉴 구조를 관리합니다.</p>
        </div>
        
        <div class="header-actions">
          <VaButton
            color="secondary"
            icon="refresh"
            @click="loadMenus"
          >
            새로고침
          </VaButton>
          
          <VaButton
            color="primary"
            icon="add"
            @click="openCreateModal"
          >
            메뉴 추가
          </VaButton>
        </div>
      </div>
    </div>

    <!-- 메뉴 트리 카드 -->
    <VaCard class="menu-tree-card">
      <VaCardContent>
        <div class="tree-header">
          <h3>메뉴 구조</h3>
          <div class="tree-actions">
            <VaButton
              preset="secondary"
              size="small"
              @click="expandAll"
            >
              모두 펼치기
            </VaButton>
            <VaButton
              preset="secondary"
              size="small"
              @click="collapseAll"
            >
              모두 접기
            </VaButton>
          </div>
        </div>
        
        <div class="menu-tree" v-if="menuTree.length > 0">
          <MenuTreeNode
            v-for="menu in menuTree"
            :key="menu.id"
            :menu="menu"
            :level="0"
            @edit="openEditModal"
            @delete="confirmDelete"
            @add-child="openCreateChildModal"
            @toggle-status="toggleMenuStatus"
          />
        </div>
        
        <div v-else class="empty-state">
          <VaIcon name="menu" size="4rem" color="secondary" />
          <h4>메뉴가 없습니다</h4>
          <p>새 메뉴를 추가하여 시작하세요.</p>
          <VaButton color="primary" @click="openCreateModal">
            첫 번째 메뉴 추가
          </VaButton>
        </div>
      </VaCardContent>
    </VaCard>

    <!-- 메뉴 생성/수정 모달 -->
    <VaModal
      v-model="showMenuModal"
      :title="isEditMode ? '메뉴 수정' : '메뉴 생성'"
      size="large"
      @ok="saveMenu"
      @cancel="closeMenuModal"
    >
      <VaForm ref="menuForm" @submit.prevent="saveMenu">
        <div class="modal-content">
          <div class="form-row">
            <div class="form-col">
              <VaInput
                v-model="menuForm.name"
                label="메뉴명"
                :rules="[required]"
                required
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="menuForm.display_name"
                label="표시명"
                :rules="[required]"
                required
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaInput
                v-model="menuForm.path"
                label="경로"
                placeholder="/example/path"
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="menuForm.icon"
                label="아이콘"
                placeholder="dashboard"
              >
                <template #append>
                  <VaIcon
                    v-if="menuForm.icon"
                    :name="menuForm.icon"
                    color="primary"
                  />
                </template>
              </VaInput>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaSelect
                v-model="menuForm.parent_id"
                :options="parentMenuOptions"
                label="상위 메뉴"
                text-by="display_name"
                value-by="id"
                clearable
                placeholder="최상위 메뉴"
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="menuForm.sort_order"
                label="정렬 순서"
                type="number"
                :rules="[required]"
                required
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaSelect
                v-model="menuForm.menu_type"
                :options="menuTypeOptions"
                label="메뉴 타입"
                :rules="[required]"
                required
              />
            </div>
            
            <div class="form-col">
              <VaInput
                v-model="menuForm.component"
                label="컴포넌트"
                placeholder="PageComponent"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaTextarea
                v-model="menuForm.description"
                label="설명"
                rows="3"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaCheckbox
                v-model="menuForm.is_active"
                label="활성 상태"
              />
            </div>
            
            <div class="form-col">
              <VaCheckbox
                v-model="menuForm.is_visible"
                label="메뉴에 표시"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-col">
              <VaCheckbox
                v-model="menuForm.requires_auth"
                label="인증 필요"
              />
            </div>
            
            <div class="form-col">
              <VaCheckbox
                v-model="menuForm.is_external"
                label="외부 링크"
              />
            </div>
          </div>
          
          <div class="form-row" v-if="menuForm.requires_auth">
            <div class="form-col">
              <VaSelect
                v-model="menuForm.required_permissions"
                :options="availablePermissions"
                label="필요 권한"
                multiple
                text-by="display_name"
                value-by="id"
                placeholder="권한 선택"
              />
            </div>
          </div>
        </div>
      </VaForm>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'vuestic-ui';
import { authAPI } from '../../api/client';
import MenuTreeNode from '../../components/admin/MenuTreeNode.vue';
import type { Menu, Permission } from '../../types/auth';

const { init: notify } = useToast();

// 상태 관리
const loading = ref(false);
const menus = ref<Menu[]>([]);
const availablePermissions = ref<Permission[]>([]);

// 모달 상태
const showMenuModal = ref(false);
const isEditMode = ref(false);
const selectedMenu = ref<Menu | null>(null);
const parentMenuId = ref<number | null>(null);

// 폼 데이터
const menuForm = ref({
  name: '',
  display_name: '',
  path: '',
  icon: '',
  parent_id: null as number | null,
  sort_order: 1,
  menu_type: 'menu',
  component: '',
  description: '',
  is_active: true,
  is_visible: true,
  requires_auth: true,
  is_external: false,
  required_permissions: [] as number[],
});

// 메뉴 타입 옵션
const menuTypeOptions = [
  { text: '메뉴', value: 'menu' },
  { text: '페이지', value: 'page' },
  { text: '버튼', value: 'button' },
  { text: '구분선', value: 'divider' },
];

// 메뉴 트리 구조
const menuTree = computed(() => {
  const buildTree = (parentId: number | null = null): Menu[] => {
    return menus.value
      .filter(menu => menu.parent_id === parentId)
      .sort((a, b) => a.sort_order - b.sort_order)
      .map(menu => ({
        ...menu,
        children: buildTree(menu.id),
      }));
  };
  
  return buildTree();
});

// 상위 메뉴 옵션 (현재 편집 중인 메뉴와 그 하위 메뉴 제외)
const parentMenuOptions = computed(() => {
  const excludeIds = new Set<number>();
  
  if (isEditMode.value && selectedMenu.value) {
    // 현재 메뉴와 그 하위 메뉴들을 제외
    const addDescendants = (menuId: number) => {
      excludeIds.add(menuId);
      menus.value
        .filter(m => m.parent_id === menuId)
        .forEach(child => addDescendants(child.id));
    };
    addDescendants(selectedMenu.value.id);
  }
  
  return menus.value
    .filter(menu => !excludeIds.has(menu.id))
    .filter(menu => menu.menu_type === 'menu')
    .sort((a, b) => a.display_name.localeCompare(b.display_name));
});

// 유효성 검사 규칙
const required = (value: string | number) => !!value || '필수 입력 항목입니다.';

// 데이터 로드
const loadMenus = async () => {
  try {
    loading.value = true;
    const response = await authAPI.get('/admin/menus');
    menus.value = response.data;
  } catch (error) {
    notify({
      message: '메뉴 목록을 불러오는데 실패했습니다.',
      color: 'danger',
    });
  } finally {
    loading.value = false;
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

// 트리 확장/축소
const expandAll = () => {
  // MenuTreeNode 컴포넌트에서 처리
  document.dispatchEvent(new CustomEvent('expand-all-menus'));
};

const collapseAll = () => {
  // MenuTreeNode 컴포넌트에서 처리
  document.dispatchEvent(new CustomEvent('collapse-all-menus'));
};

// 모달 관리
const openCreateModal = () => {
  isEditMode.value = false;
  parentMenuId.value = null;
  resetMenuForm();
  showMenuModal.value = true;
};

const openCreateChildModal = (parentMenu: Menu) => {
  isEditMode.value = false;
  parentMenuId.value = parentMenu.id;
  resetMenuForm();
  menuForm.value.parent_id = parentMenu.id;
  menuForm.value.sort_order = getNextSortOrder(parentMenu.id);
  showMenuModal.value = true;
};

const openEditModal = (menu: Menu) => {
  isEditMode.value = true;
  selectedMenu.value = menu;
  fillMenuForm(menu);
  showMenuModal.value = true;
};

const closeMenuModal = () => {
  showMenuModal.value = false;
  resetMenuForm();
  selectedMenu.value = null;
  parentMenuId.value = null;
};

// 폼 관리
const resetMenuForm = () => {
  menuForm.value = {
    name: '',
    display_name: '',
    path: '',
    icon: '',
    parent_id: null,
    sort_order: 1,
    menu_type: 'menu',
    component: '',
    description: '',
    is_active: true,
    is_visible: true,
    requires_auth: true,
    is_external: false,
    required_permissions: [],
  };
};

const fillMenuForm = (menu: Menu) => {
  menuForm.value = {
    name: menu.name,
    display_name: menu.display_name,
    path: menu.path || '',
    icon: menu.icon || '',
    parent_id: menu.parent_id,
    sort_order: menu.sort_order,
    menu_type: menu.menu_type,
    component: menu.component || '',
    description: menu.description || '',
    is_active: menu.is_active,
    is_visible: menu.is_visible,
    requires_auth: menu.requires_auth,
    is_external: menu.is_external,
    required_permissions: menu.required_permissions?.map(p => p.id) || [],
  };
};

// 다음 정렬 순서 계산
const getNextSortOrder = (parentId: number | null): number => {
  const siblings = menus.value.filter(menu => menu.parent_id === parentId);
  if (siblings.length === 0) return 1;
  return Math.max(...siblings.map(menu => menu.sort_order)) + 1;
};

// CRUD 작업
const saveMenu = async () => {
  try {
    const menuData = { ...menuForm.value };
    
    if (isEditMode.value && selectedMenu.value) {
      await authAPI.put(`/admin/menus/${selectedMenu.value.id}`, menuData);
      notify({
        message: '메뉴가 성공적으로 수정되었습니다.',
        color: 'success',
      });
    } else {
      await authAPI.post('/admin/menus', menuData);
      notify({
        message: '메뉴가 성공적으로 생성되었습니다.',
        color: 'success',
      });
    }
    
    closeMenuModal();
    await loadMenus();
  } catch (error: any) {
    notify({
      message: error.response?.data?.detail || '메뉴 저장에 실패했습니다.',
      color: 'danger',
    });
  }
};

const toggleMenuStatus = async (menu: Menu) => {
  try {
    await authAPI.patch(`/admin/menus/${menu.id}/status`, {
      is_active: !menu.is_active,
    });
    
    notify({
      message: `메뉴가 ${!menu.is_active ? '활성화' : '비활성화'}되었습니다.`,
      color: 'success',
    });
    
    await loadMenus();
  } catch (error) {
    notify({
      message: '메뉴 상태 변경에 실패했습니다.',
      color: 'danger',
    });
  }
};

const confirmDelete = (menu: Menu) => {
  if (menu.children && menu.children.length > 0) {
    notify({
      message: '하위 메뉴가 있는 메뉴는 삭제할 수 없습니다.',
      color: 'warning',
    });
    return;
  }
  
  if (confirm(`정말로 메뉴 "${menu.display_name}"을(를) 삭제하시겠습니까?`)) {
    deleteMenu(menu);
  }
};

const deleteMenu = async (menu: Menu) => {
  try {
    await authAPI.delete(`/admin/menus/${menu.id}`);
    notify({
      message: '메뉴가 성공적으로 삭제되었습니다.',
      color: 'success',
    });
    await loadMenus();
  } catch (error) {
    notify({
      message: '메뉴 삭제에 실패했습니다.',
      color: 'danger',
    });
  }
};

// 컴포넌트 마운트
onMounted(async () => {
  await Promise.all([
    loadMenus(),
    loadPermissions(),
  ]);
});
</script>

<style scoped>
.menu-management {
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

.menu-tree-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.tree-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #333;
}

.tree-actions {
  display: flex;
  gap: 0.5rem;
}

.menu-tree {
  min-height: 200px;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
}

.empty-state h4 {
  margin: 1rem 0 0.5rem 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.empty-state p {
  margin: 0 0 1.5rem 0;
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

.mr-2 {
  margin-right: 0.5rem;
}

@media (max-width: 768px) {
  .menu-management {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tree-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .tree-actions {
    justify-content: center;
  }
  
  .form-row {
    flex-direction: column;
  }
}
</style>
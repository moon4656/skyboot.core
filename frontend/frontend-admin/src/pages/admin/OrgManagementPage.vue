<template>
  <div class="org-management-page">
    <!-- 페이지 헤더 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">조직 관리</h1>
        <p class="page-description">조직 구조를 관리하고 부서/팀을 추가, 수정, 삭제할 수 있습니다.</p>
      </div>
      <div class="header-actions">
        <va-button
          color="primary"
          icon="add"
          @click="showCreateModal = true"
        >
          조직 추가
        </va-button>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <va-row :gutter="24">
        <!-- 조직 트리 -->
        <va-col :span="8">
          <va-card>
            <va-card-title>조직 구조</va-card-title>
            <va-card-content>
              <div class="org-tree">
                <org-tree-node
                  v-for="org in rootOrganizations"
                  :key="org.id"
                  :org="org"
                  :selected-org="selectedOrg"
                  :expanded-nodes="expandedNodes"
                  @select="selectOrganization"
                  @toggle="toggleNode"
                  @edit="editOrganization"
                  @delete="deleteOrganization"
                  @add-child="addChildOrganization"
                />
              </div>
            </va-card-content>
          </va-card>
        </va-col>

        <!-- 조직 상세 정보 -->
        <va-col :span="16">
          <va-card v-if="selectedOrg">
            <va-card-title>조직 정보</va-card-title>
            <va-card-content>
              <va-row :gutter="16">
                <va-col :span="12">
                  <va-input
                    v-model="selectedOrg.name"
                    label="조직명"
                    readonly
                  />
                </va-col>
                <va-col :span="12">
                  <va-input
                    v-model="selectedOrg.code"
                    label="조직 코드"
                    readonly
                  />
                </va-col>
              </va-row>

              <va-row :gutter="16">
                <va-col :span="12">
                  <va-select
                    v-model="selectedOrg.type"
                    label="조직 유형"
                    :options="orgTypeOptions"
                    readonly
                  />
                </va-col>
                <va-col :span="12">
                  <va-switch
                    v-model="selectedOrg.isActive"
                    label="활성 상태"
                    readonly
                  />
                </va-col>
              </va-row>

              <va-textarea
                v-model="selectedOrg.description"
                label="설명"
                readonly
              />

              <div class="org-actions">
                <va-button
                  color="primary"
                  icon="edit"
                  @click="editOrganization(selectedOrg)"
                >
                  수정
                </va-button>
                <va-button
                  color="success"
                  icon="add"
                  @click="addChildOrganization(selectedOrg)"
                >
                  하위 조직 추가
                </va-button>
                <va-button
                  color="danger"
                  icon="delete"
                  @click="deleteOrganization(selectedOrg)"
                >
                  삭제
                </va-button>
              </div>
            </va-card-content>
          </va-card>

          <va-card v-else>
            <va-card-content>
              <div class="empty-state">
                <va-icon name="domain" size="4rem" color="secondary" />
                <h3>조직을 선택하세요</h3>
                <p>왼쪽 조직 트리에서 조직을 선택하면 상세 정보를 확인할 수 있습니다.</p>
              </div>
            </va-card-content>
          </va-card>
        </va-col>
      </va-row>
    </div>

    <!-- 조직 생성/수정 모달 -->
    <va-modal
      v-model="showCreateModal"
      title="조직 추가"
      size="medium"
      @ok="createOrganization"
      @cancel="resetForm"
    >
      <va-form ref="formRef">
        <va-row :gutter="16">
          <va-col :span="12">
            <va-input
              v-model="form.name"
              label="조직명"
              :rules="[required]"
              required
            />
          </va-col>
          <va-col :span="12">
            <va-input
              v-model="form.code"
              label="조직 코드"
              :rules="[required]"
              required
            />
          </va-col>
        </va-row>

        <va-row :gutter="16">
          <va-col :span="12">
            <va-select
              v-model="form.type"
              label="조직 유형"
              :options="orgTypeOptions"
              :rules="[required]"
              required
            />
          </va-col>
          <va-col :span="12">
            <va-select
              v-model="form.parentId"
              label="상위 조직"
              :options="parentOrgOptions"
              clearable
            />
          </va-col>
        </va-row>

        <va-textarea
          v-model="form.description"
          label="설명"
        />

        <va-switch
          v-model="form.isActive"
          label="활성 상태"
        />
      </va-form>
    </va-modal>

    <!-- 조직 수정 모달 -->
    <va-modal
      v-model="showEditModal"
      title="조직 수정"
      size="medium"
      @ok="updateOrganization"
      @cancel="resetForm"
    >
      <va-form ref="editFormRef">
        <va-row :gutter="16">
          <va-col :span="12">
            <va-input
              v-model="editForm.name"
              label="조직명"
              :rules="[required]"
              required
            />
          </va-col>
          <va-col :span="12">
            <va-input
              v-model="editForm.code"
              label="조직 코드"
              :rules="[required]"
              required
            />
          </va-col>
        </va-row>

        <va-row :gutter="16">
          <va-col :span="12">
            <va-select
              v-model="editForm.type"
              label="조직 유형"
              :options="orgTypeOptions"
              :rules="[required]"
              required
            />
          </va-col>
          <va-col :span="12">
            <va-select
              v-model="editForm.parentId"
              label="상위 조직"
              :options="parentOrgOptions"
              clearable
            />
          </va-col>
        </va-row>

        <va-textarea
          v-model="editForm.description"
          label="설명"
        />

        <va-switch
          v-model="editForm.isActive"
          label="활성 상태"
        />
      </va-form>
    </va-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useToast } from 'vuestic-ui'
import OrgTreeNode from '../../components/admin/OrgTreeNode.vue'
import { apiUtils } from '../../utils/api'

interface Organization {
  id: number
  name: string
  code: string
  description?: string
  type: 'company' | 'department' | 'team' | 'group'
  parentId?: number
  sortOrder: number
  isActive: boolean
  createdAt: string
  updatedAt: string
  children?: Organization[]
}

interface OrganizationForm {
  id?: number
  name: string
  code: string
  description: string
  type: 'company' | 'department' | 'team' | 'group'
  parentId?: number
  isActive: boolean
}

const { init: notify } = useToast()

// 상태 관리
const organizations = ref<Organization[]>([])
const selectedOrg = ref<Organization | null>(null)
const expandedNodes = ref<Set<number>>(new Set())
const loading = ref(false)

// 모달 상태
const showCreateModal = ref(false)
const showEditModal = ref(false)
const formRef = ref()
const editFormRef = ref()

// 폼 데이터
const form = ref<OrganizationForm>({
  name: '',
  code: '',
  description: '',
  type: 'department',
  isActive: true
})

const editForm = ref<OrganizationForm>({
  id: undefined,
  name: '',
  code: '',
  description: '',
  type: 'department',
  isActive: true
})

// 옵션 데이터
const orgTypeOptions = [
  { text: '회사', value: 'company' },
  { text: '부서', value: 'department' },
  { text: '팀', value: 'team' },
  { text: '그룹', value: 'group' }
]

// 계산된 속성
const rootOrganizations = computed(() => {
  return buildOrgTree(organizations.value)
})

const parentOrgOptions = computed(() => {
  return organizations.value
    .filter(org => org.id !== editForm.value.id)
    .map(org => ({
      text: `${org.name} (${org.code})`,
      value: org.id
    }))
})

// 유틸리티 함수
const buildOrgTree = (orgs: Organization[]): Organization[] => {
  const orgMap = new Map<number, Organization>()
  const roots: Organization[] = []
  
  // 모든 조직을 맵에 저장
  orgs.forEach(org => {
    orgMap.set(org.id, { ...org, children: [] })
  })
  
  // 트리 구조 구성
  orgs.forEach(org => {
    const orgNode = orgMap.get(org.id)!
    if (org.parentId && orgMap.has(org.parentId)) {
      const parent = orgMap.get(org.parentId)!
      parent.children!.push(orgNode)
    } else {
      roots.push(orgNode)
    }
  })
  
  return roots.sort((a, b) => a.sortOrder - b.sortOrder)
}

const required = (value: string) => {
  return !!value || '필수 입력 항목입니다.'
}

// 메서드
const loadOrganizations = async () => {
  try {
    loading.value = true
    const response = await apiUtils.get<Organization[]>('/admin/organizations')
    organizations.value = response.data
  } catch (error) {
    notify({
      message: '조직 목록을 불러오는데 실패했습니다.',
      color: 'danger'
    })
  } finally {
    loading.value = false
  }
}

const selectOrganization = (org: Organization) => {
  selectedOrg.value = org
}

const toggleNode = (orgId: number) => {
  if (expandedNodes.value.has(orgId)) {
    expandedNodes.value.delete(orgId)
  } else {
    expandedNodes.value.add(orgId)
  }
}

const editOrganization = (org: Organization) => {
  editForm.value = {
    id: org.id,
    name: org.name,
    code: org.code,
    description: org.description || '',
    type: org.type,
    parentId: org.parentId,
    isActive: org.isActive
  }
  showEditModal.value = true
}

const addChildOrganization = (parentOrg: Organization) => {
  form.value.parentId = parentOrg.id
  showCreateModal.value = true
}

const createOrganization = async () => {
  if (!formRef.value?.validate()) return
  
  try {
    await apiUtils.post('/admin/organizations', form.value)
    notify({
      message: '조직이 성공적으로 생성되었습니다.',
      color: 'success'
    })
    showCreateModal.value = false
    resetForm()
    await loadOrganizations()
  } catch (error) {
    notify({
      message: '조직 생성에 실패했습니다.',
      color: 'danger'
    })
  }
}

const updateOrganization = async () => {
  if (!editFormRef.value?.validate() || !selectedOrg.value) return
  
  try {
    await apiUtils.put(`/admin/organizations/${selectedOrg.value.id}`, editForm.value)
    notify({
      message: '조직이 성공적으로 수정되었습니다.',
      color: 'success'
    })
    showEditModal.value = false
    resetForm()
    await loadOrganizations()
  } catch (error) {
    notify({
      message: '조직 수정에 실패했습니다.',
      color: 'danger'
    })
  }
}

const deleteOrganization = async (org: Organization) => {
  if (!confirm(`'${org.name}' 조직을 삭제하시겠습니까?`)) return
  
  try {
    await apiUtils.delete(`/admin/organizations/${org.id}`)
    notify({
      message: '조직이 성공적으로 삭제되었습니다.',
      color: 'success'
    })
    if (selectedOrg.value?.id === org.id) {
      selectedOrg.value = null
    }
    await loadOrganizations()
  } catch (error) {
    notify({
      message: '조직 삭제에 실패했습니다.',
      color: 'danger'
    })
  }
}

const resetForm = () => {
  form.value = {
    name: '',
    code: '',
    description: '',
    type: 'department',
    isActive: true
  }
  editForm.value = {
    name: '',
    code: '',
    description: '',
    type: 'department',
    isActive: true
  }
}

// 컴포넌트 마운트
onMounted(() => {
  loadOrganizations()
})
</script>

<style scoped>
.org-management-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--va-background-border);
}

.header-content h1 {
  margin: 0 0 0.5rem 0;
  color: var(--va-text-primary);
}

.header-content p {
  margin: 0;
  color: var(--va-text-secondary);
}

.main-content {
  min-height: 600px;
}

.org-tree {
  max-height: 500px;
  overflow-y: auto;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-state h3 {
  margin: 1rem 0 0.5rem 0;
  color: var(--va-text-primary);
}

.empty-state p {
  margin: 0;
  color: var(--va-text-secondary);
}

.org-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--va-background-border);
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .org-actions {
    flex-direction: column;
  }
}
</style>
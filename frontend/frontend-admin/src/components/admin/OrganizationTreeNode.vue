<template>
  <div class="organization-tree-node">
    <div 
      class="organization-item"
      :class="{
        'is-expanded': isExpanded,
        'is-active': organization.is_active,
        'has-children': hasChildren,
        [`level-${level}`]: true
      }"
    >
      <!-- 들여쓰기 및 확장/축소 버튼 -->
      <div class="node-indent" :style="{ paddingLeft: `${level * 1.5}rem` }">
        <VaButton
          v-if="hasChildren"
          preset="plain"
          size="small"
          :icon="isExpanded ? 'expand_less' : 'expand_more'"
          @click="toggleExpanded"
          class="expand-button"
        />
        <div v-else class="expand-placeholder" />
      </div>
      
      <!-- 조직 정보 -->
      <div class="organization-info">
        <!-- 조직 아이콘 -->
        <div class="organization-icon">
          <VaIcon 
            :name="getOrganizationIcon(organization.type)"
            :color="organization.is_active ? 'primary' : 'secondary'"
            size="1.25rem"
          />
        </div>
        
        <!-- 조직 상세 정보 -->
        <div class="organization-details">
          <div class="organization-header">
            <h4 class="organization-name">{{ organization.name }}</h4>
            <VaChip
              :color="getTypeColor(organization.type)"
              size="small"
              outline
              class="type-chip"
            >
              {{ getTypeLabel(organization.type) }}
            </VaChip>
          </div>
          
          <div class="organization-meta">
            <span class="organization-code">{{ organization.code }}</span>
            <span v-if="organization.manager_name" class="organization-manager">
              <VaIcon name="person" size="0.875rem" />
              {{ organization.manager_name }}
            </span>
            <span class="organization-users">
              <VaIcon name="group" size="0.875rem" />
              {{ organization.user_count || 0 }}명
            </span>
          </div>
          
          <div v-if="organization.description" class="organization-description">
            {{ organization.description }}
          </div>
        </div>
      </div>
      
      <!-- 상태 및 액션 -->
      <div class="organization-actions">
        <!-- 상태 표시 -->
        <VaChip
          :color="organization.is_active ? 'success' : 'danger'"
          size="small"
          outline
          class="status-chip"
        >
          {{ organization.is_active ? '활성' : '비활성' }}
        </VaChip>
        
        <!-- 액션 버튼들 -->
        <div class="action-buttons">
          <VaButton
            preset="plain"
            size="small"
            icon="group"
            @click="$emit('view-users', organization)"
            title="구성원 보기"
            class="action-button"
          />
          
          <VaButton
            preset="plain"
            size="small"
            icon="add_circle"
            @click="$emit('add-child', organization)"
            title="하위 조직 추가"
            class="action-button"
          />
          
          <VaButton
            preset="plain"
            size="small"
            icon="edit"
            @click="$emit('edit', organization)"
            title="수정"
            class="action-button"
          />
          
          <VaButton
            preset="plain"
            size="small"
            :icon="organization.is_active ? 'visibility_off' : 'visibility'"
            @click="$emit('toggle-status', organization)"
            :title="organization.is_active ? '비활성화' : '활성화'"
            class="action-button"
          />
          
          <VaButton
            preset="plain"
            size="small"
            icon="delete"
            color="danger"
            @click="$emit('delete', organization)"
            title="삭제"
            class="action-button delete-button"
            :disabled="organization.user_count > 0 || hasChildren"
          />
        </div>
      </div>
    </div>
    
    <!-- 하위 조직들 -->
    <div 
      v-if="hasChildren && isExpanded"
      class="children-container"
    >
      <OrganizationTreeNode
        v-for="child in organization.children"
        :key="child.id"
        :organization="child"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
        @toggle-status="$emit('toggle-status', $event)"
        @view-users="$emit('view-users', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import type { Organization } from '../../types/auth';

// Props 정의
interface Props {
  organization: Organization & { children?: Organization[] };
  level: number;
}

const props = defineProps<Props>();

// Emits 정의
defineEmits<{
  edit: [organization: Organization];
  delete: [organization: Organization];
  'add-child': [organization: Organization];
  'toggle-status': [organization: Organization];
  'view-users': [organization: Organization];
}>();

// 상태 관리
const isExpanded = ref(props.level < 2); // 기본적으로 2레벨까지만 펼침

// 계산된 속성
const hasChildren = computed(() => {
  return props.organization.children && props.organization.children.length > 0;
});

// 메서드
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value;
};

const getOrganizationIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    headquarters: 'business',
    branch: 'location_city',
    department: 'domain',
    team: 'group',
    project: 'work',
  };
  return iconMap[type] || 'account_tree';
};

const getTypeColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    headquarters: 'primary',
    branch: 'info',
    department: 'success',
    team: 'warning',
    project: 'secondary',
  };
  return colorMap[type] || 'secondary';
};

const getTypeLabel = (type: string): string => {
  const labelMap: Record<string, string> = {
    headquarters: '본사',
    branch: '지사',
    department: '부서',
    team: '팀',
    project: '프로젝트',
  };
  return labelMap[type] || type;
};

// 전역 이벤트 리스너
const handleExpandAll = () => {
  isExpanded.value = true;
};

const handleCollapseAll = () => {
  isExpanded.value = false;
};

// 라이프사이클
onMounted(() => {
  document.addEventListener('expand-all-organizations', handleExpandAll);
  document.addEventListener('collapse-all-organizations', handleCollapseAll);
});

onUnmounted(() => {
  document.removeEventListener('expand-all-organizations', handleExpandAll);
  document.removeEventListener('collapse-all-organizations', handleCollapseAll);
});
</script>

<style scoped>
.organization-tree-node {
  margin-bottom: 0.25rem;
}

.organization-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s ease;
  position: relative;
}

.organization-item:hover {
  border-color: #ccc;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.organization-item.is-expanded {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}

.organization-item.is-active {
  background: #fff;
}

.organization-item:not(.is-active) {
  background: #f8f9fa;
  opacity: 0.8;
}

.organization-item.level-0 {
  border-left: 4px solid var(--va-primary);
}

.organization-item.level-1 {
  border-left: 4px solid var(--va-info);
}

.organization-item.level-2 {
  border-left: 4px solid var(--va-success);
}

.organization-item.level-3 {
  border-left: 4px solid var(--va-warning);
}

.node-indent {
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.expand-button {
  width: 24px;
  height: 24px;
  min-width: 24px;
  border-radius: 50%;
}

.expand-placeholder {
  width: 24px;
  height: 24px;
}

.organization-info {
  display: flex;
  align-items: flex-start;
  flex: 1;
  gap: 0.75rem;
  min-width: 0;
}

.organization-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.organization-details {
  flex: 1;
  min-width: 0;
}

.organization-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.organization-name {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.type-chip {
  flex-shrink: 0;
}

.organization-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
  color: #666;
  flex-wrap: wrap;
}

.organization-code {
  font-family: 'Courier New', monospace;
  background: #f0f0f0;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-weight: 500;
}

.organization-manager,
.organization-users {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.organization-description {
  font-size: 0.875rem;
  color: #777;
  line-height: 1.4;
  margin-top: 0.25rem;
}

.organization-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.status-chip {
  flex-shrink: 0;
}

.action-buttons {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.organization-item:hover .action-buttons {
  opacity: 1;
}

.action-button {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  transition: all 0.2s ease;
}

.action-button:hover {
  background: rgba(0, 0, 0, 0.05);
}

.delete-button:hover {
  background: rgba(220, 53, 69, 0.1);
}

.delete-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.children-container {
  border-left: 1px solid #e0e0e0;
  border-right: 1px solid #e0e0e0;
  border-bottom: 1px solid #e0e0e0;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  padding: 0.5rem;
  background: #fafafa;
}

.children-container .organization-tree-node:last-child {
  margin-bottom: 0;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .organization-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .node-indent {
    display: none;
  }
  
  .organization-info {
    align-items: center;
  }
  
  .organization-header {
    flex-wrap: wrap;
  }
  
  .organization-meta {
    justify-content: flex-start;
  }
  
  .organization-actions {
    justify-content: space-between;
    padding-top: 0.5rem;
    border-top: 1px solid #e0e0e0;
  }
  
  .action-buttons {
    opacity: 1;
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .organization-item {
    padding: 0.5rem;
  }
  
  .organization-name {
    font-size: 0.875rem;
  }
  
  .organization-meta {
    font-size: 0.75rem;
    gap: 0.5rem;
  }
  
  .action-buttons {
    gap: 0.125rem;
  }
  
  .action-button {
    width: 28px;
    height: 28px;
    min-width: 28px;
  }
}

/* 애니메이션 */
.children-container {
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 드래그 앤 드롭 지원 (향후 확장용) */
.organization-item.dragging {
  opacity: 0.5;
  transform: rotate(5deg);
}

.organization-item.drop-target {
  border-color: var(--va-primary);
  background: rgba(var(--va-primary-rgb), 0.05);
}

/* 포커스 스타일 */
.organization-item:focus-within {
  outline: 2px solid var(--va-primary);
  outline-offset: 2px;
}

/* 다크 모드 지원 */
@media (prefers-color-scheme: dark) {
  .organization-item {
    background: #2d3748;
    border-color: #4a5568;
    color: #e2e8f0;
  }
  
  .organization-item:hover {
    border-color: #718096;
  }
  
  .organization-item:not(.is-active) {
    background: #1a202c;
  }
  
  .organization-name {
    color: #e2e8f0;
  }
  
  .organization-meta {
    color: #a0aec0;
  }
  
  .organization-code {
    background: #4a5568;
    color: #e2e8f0;
  }
  
  .organization-description {
    color: #cbd5e0;
  }
  
  .children-container {
    background: #1a202c;
    border-color: #4a5568;
  }
  
  .action-button:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}
</style>
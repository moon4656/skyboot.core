<template>
  <div class="org-tree-node">
    <div 
      class="node-content"
      :class="{ 'selected': selectedOrg?.id === org.id }"
      @click="$emit('select', org)"
    >
      <div class="node-info">
        <va-button
          v-if="hasChildren"
          preset="plain"
          size="small"
          :icon="isExpanded ? 'expand_less' : 'expand_more'"
          @click.stop="$emit('toggle', org.id)"
        />
        <va-icon
          v-else
          name="radio_button_unchecked"
          size="small"
          color="secondary"
        />
        
        <va-icon
          :name="getOrgIcon(org.type)"
          :color="getOrgIconColor(org.type)"
          size="small"
        />
        
        <span class="node-name">{{ org.name }}</span>
        <span class="node-code">({{ org.code }})</span>
        
        <va-badge
          v-if="!org.isActive"
          color="danger"
          text="비활성"
          size="small"
        />
      </div>
      
      <div class="node-actions">
        <va-button
          preset="plain"
          size="small"
          icon="add"
          @click.stop="$emit('add-child', org)"
        />
        <va-button
          preset="plain"
          size="small"
          icon="edit"
          @click.stop="$emit('edit', org)"
        />
        <va-button
          preset="plain"
          size="small"
          icon="delete"
          @click.stop="$emit('delete', org)"
        />
      </div>
    </div>
    
    <div v-if="hasChildren && isExpanded" class="children">
      <org-tree-node
        v-for="child in org.children"
        :key="child.id"
        :org="child"
        :selected-org="selectedOrg"
        :expanded-nodes="expandedNodes"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

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

interface Props {
  org: Organization
  selectedOrg: Organization | null
  expandedNodes: Set<number>
}

const props = defineProps<Props>()

defineEmits<{
  select: [org: Organization]
  toggle: [orgId: number]
  edit: [org: Organization]
  delete: [org: Organization]
  'add-child': [org: Organization]
}>()

// 계산된 속성
const hasChildren = computed(() => {
  return props.org.children && props.org.children.length > 0
})

const isExpanded = computed(() => {
  return props.expandedNodes.has(props.org.id)
})

// 유틸리티 함수
const getOrgIcon = (type: string): string => {
  switch (type) {
    case 'company': return 'business'
    case 'department': return 'domain'
    case 'team': return 'group'
    case 'group': return 'workspaces'
    default: return 'folder'
  }
}

const getOrgIconColor = (type: string): string => {
  switch (type) {
    case 'company': return 'primary'
    case 'department': return 'success'
    case 'team': return 'info'
    case 'group': return 'warning'
    default: return 'secondary'
  }
}
</script>

<style scoped>
.org-tree-node {
  margin-bottom: 0.25rem;
}

.node-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.node-content:hover {
  background-color: var(--va-background-element);
  border-color: var(--va-background-border);
}

.node-content.selected {
  background-color: var(--va-primary-lighten);
  border-color: var(--va-primary);
  color: var(--va-primary-darken);
}

.node-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.node-name {
  font-weight: 500;
  color: var(--va-text-primary);
}

.node-code {
  font-size: 0.875rem;
  color: var(--va-text-secondary);
}

.node-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.node-content:hover .node-actions {
  opacity: 1;
}

.children {
  margin-left: 1.5rem;
  padding-left: 1rem;
  border-left: 2px solid var(--va-background-border);
  margin-top: 0.25rem;
}

/* 선택된 노드의 자식들 스타일 */
.node-content.selected + .children {
  border-left-color: var(--va-primary-lighten);
}
</style>
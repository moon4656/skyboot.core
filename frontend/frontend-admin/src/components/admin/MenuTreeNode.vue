<template>
  <div class="menu-tree-node">
    <div 
      class="menu-item"
      :class="{
        'menu-item--active': menu.is_active,
        'menu-item--inactive': !menu.is_active,
        [`menu-item--level-${level}`]: true
      }"
    >
      <!-- 들여쓰기 -->
      <div class="menu-indent" :style="{ width: `${level * 24}px` }" />
      
      <!-- 확장/축소 버튼 -->
      <div class="expand-button">
        <VaButton
          v-if="hasChildren"
          preset="secondary"
          size="small"
          :icon="isExpanded ? 'expand_less' : 'expand_more'"
          @click="toggleExpanded"
        />
        <div v-else class="expand-placeholder" />
      </div>
      
      <!-- 메뉴 아이콘 -->
      <div class="menu-icon">
        <VaIcon
          :name="menu.icon || getDefaultIcon(menu.menu_type)"
          :color="menu.is_active ? 'primary' : 'secondary'"
          size="small"
        />
      </div>
      
      <!-- 메뉴 정보 -->
      <div class="menu-info">
        <div class="menu-title">
          <span class="menu-name">{{ menu.display_name }}</span>
          <VaChip
            v-if="menu.menu_type !== 'menu'"
            :color="getTypeColor(menu.menu_type)"
            size="small"
            outline
            class="ml-2"
          >
            {{ getTypeLabel(menu.menu_type) }}
          </VaChip>
        </div>
        
        <div class="menu-details">
          <span v-if="menu.path" class="menu-path">{{ menu.path }}</span>
          <span v-if="menu.component" class="menu-component">{{ menu.component }}</span>
          <span v-if="menu.is_external" class="external-indicator">
            <VaIcon name="open_in_new" size="12px" />
            외부링크
          </span>
        </div>
      </div>
      
      <!-- 메뉴 상태 -->
      <div class="menu-status">
        <VaChip
          :color="menu.is_active ? 'success' : 'danger'"
          size="small"
          outline
        >
          {{ menu.is_active ? '활성' : '비활성' }}
        </VaChip>
        
        <VaChip
          v-if="!menu.is_visible"
          color="warning"
          size="small"
          outline
          class="ml-1"
        >
          숨김
        </VaChip>
        
        <VaChip
          v-if="menu.requires_auth"
          color="info"
          size="small"
          outline
          class="ml-1"
        >
          인증필요
        </VaChip>
      </div>
      
      <!-- 정렬 순서 -->
      <div class="menu-order">
        <VaChip
          color="secondary"
          size="small"
          outline
        >
          {{ menu.sort_order }}
        </VaChip>
      </div>
      
      <!-- 액션 버튼 -->
      <div class="menu-actions">
        <VaButton
          preset="secondary"
          size="small"
          icon="add"
          @click="$emit('add-child', menu)"
          title="하위 메뉴 추가"
        />
        
        <VaButton
          preset="secondary"
          size="small"
          icon="edit"
          @click="$emit('edit', menu)"
          title="수정"
        />
        
        <VaButton
          :preset="menu.is_active ? 'secondary' : 'primary'"
          :color="menu.is_active ? 'warning' : 'success'"
          size="small"
          :icon="menu.is_active ? 'visibility_off' : 'visibility'"
          @click="$emit('toggle-status', menu)"
          :title="menu.is_active ? '비활성화' : '활성화'"
        />
        
        <VaButton
          preset="secondary"
          color="danger"
          size="small"
          icon="delete"
          @click="$emit('delete', menu)"
          title="삭제"
          :disabled="hasChildren"
        />
      </div>
    </div>
    
    <!-- 하위 메뉴 -->
    <div v-if="hasChildren && isExpanded" class="menu-children">
      <MenuTreeNode
        v-for="child in menu.children"
        :key="child.id"
        :menu="child"
        :level="level + 1"
        @edit="$emit('edit', $event)"
        @delete="$emit('delete', $event)"
        @add-child="$emit('add-child', $event)"
        @toggle-status="$emit('toggle-status', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Menu } from '../../types/auth'

interface Props {
  menu: Menu & { children?: Menu[] }
  level: number
}

interface Emits {
  edit: [menu: Menu]
  delete: [menu: Menu]
  'add-child': [menu: Menu]
  'toggle-status': [menu: Menu]
}

const props = defineProps<Props>()
defineEmits<Emits>()

// 상태 관리
const isExpanded = ref(props.level < 2) // 기본적으로 2레벨까지만 펼침

// 계산된 속성
const hasChildren = computed(() => {
  return props.menu.children && props.menu.children.length > 0
})

// 메서드
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const getDefaultIcon = (menuType: string): string => {
  const iconMap: Record<string, string> = {
    menu: 'folder',
    page: 'description',
    button: 'smart_button',
    divider: 'horizontal_rule',
  }
  return iconMap[menuType] || 'circle'
}

const getTypeColor = (menuType: string): string => {
  const colorMap: Record<string, string> = {
    menu: 'primary',
    page: 'info',
    button: 'success',
    divider: 'secondary',
  }
  return colorMap[menuType] || 'primary'
}

const getTypeLabel = (menuType: string): string => {
  const labelMap: Record<string, string> = {
    menu: '메뉴',
    page: '페이지',
    button: '버튼',
    divider: '구분선',
  }
  return labelMap[menuType] || menuType
}

// 전역 이벤트 리스너
const handleExpandAll = () => {
  isExpanded.value = true
}

const handleCollapseAll = () => {
  isExpanded.value = false
}

// 라이프사이클
onMounted(() => {
  document.addEventListener('expand-all-menus', handleExpandAll)
  document.addEventListener('collapse-all-menus', handleCollapseAll)
})

onUnmounted(() => {
  document.removeEventListener('expand-all-menus', handleExpandAll)
  document.removeEventListener('collapse-all-menus', handleCollapseAll)
})
</script>

<style scoped>
.menu-tree-node {
  margin-bottom: 2px;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s ease;
  gap: 0.75rem;
}

.menu-item:hover {
  background: #f8f9fa;
  border-color: #d0d7de;
}

.menu-item--active {
  border-left: 4px solid #4caf50;
}

.menu-item--inactive {
  border-left: 4px solid #f44336;
  background: #fafafa;
}

.menu-item--level-0 {
  font-weight: 600;
}

.menu-item--level-1 {
  font-weight: 500;
}

.menu-indent {
  flex-shrink: 0;
}

.expand-button {
  width: 32px;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.expand-placeholder {
  width: 32px;
  height: 32px;
}

.menu-icon {
  flex-shrink: 0;
  width: 24px;
  display: flex;
  justify-content: center;
}

.menu-info {
  flex: 1;
  min-width: 0;
}

.menu-title {
  display: flex;
  align-items: center;
  margin-bottom: 0.25rem;
}

.menu-name {
  font-weight: 500;
  color: #333;
}

.menu-details {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.875rem;
  color: #666;
}

.menu-path {
  font-family: 'Courier New', monospace;
  background: #f1f3f4;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.menu-component {
  font-family: 'Courier New', monospace;
  background: #e8f5e8;
  padding: 0.125rem 0.375rem;
  border-radius: 4px;
  font-size: 0.8rem;
  color: #2e7d32;
}

.external-indicator {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #1976d2;
  font-size: 0.8rem;
}

.menu-status {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-shrink: 0;
}

.menu-order {
  flex-shrink: 0;
}

.menu-actions {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.menu-children {
  margin-top: 0.5rem;
  margin-left: 1rem;
  border-left: 2px solid #e0e0e0;
  padding-left: 1rem;
}

.ml-1 {
  margin-left: 0.25rem;
}

.ml-2 {
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .menu-item {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .menu-info {
    flex-basis: 100%;
    order: 1;
  }
  
  .menu-status {
    order: 2;
  }
  
  .menu-order {
    order: 3;
  }
  
  .menu-actions {
    order: 4;
    flex-wrap: wrap;
  }
  
  .menu-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .menu-children {
    margin-left: 0.5rem;
    padding-left: 0.5rem;
  }
}

@media (max-width: 480px) {
  .menu-item {
    padding: 0.5rem;
  }
  
  .menu-actions {
    gap: 0.125rem;
  }
  
  .expand-button,
  .expand-placeholder {
    width: 24px;
  }
  
  .menu-indent {
    display: none;
  }
}
</style>
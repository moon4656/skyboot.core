<template>
  <!-- 자식 메뉴가 있는 경우 - 아코디언 스타일 -->
  <div v-if="hasChildren" class="menu-group">
    <VaSidebarItem
      :active="isActive"
      @click="toggleExpanded"
      class="menu-parent"
    >
      <VaSidebarItemContent>
        <VaIcon
          v-if="menuItem.icon"
          :name="menuItem.icon"
          class="mr-2"
        />
        <VaSidebarItemTitle>
          {{ menuItem.displayName }}
        </VaSidebarItemTitle>
        <VaIcon
          :name="isExpanded ? 'expand_less' : 'expand_more'"
          class="ml-auto transition-transform"
          :class="{ 'rotate-180': isExpanded }"
        />
      </VaSidebarItemContent>
    </VaSidebarItem>
    
    <!-- 자식 메뉴들 -->
    <VaCollapse v-model="isExpanded">
      <div class="children-container">
        <DynamicMenuItem
          v-for="child in menuItem.children"
          :key="child.id"
          :menu-item="child"
          :current-route="currentRoute"
          :depth="depth + 1"
          @navigate="$emit('navigate', $event)"
        />
      </div>
    </VaCollapse>
  </div>
  
  <!-- 단일 메뉴 아이템 -->
  <VaSidebarItem
    v-else
    :to="menuItem.path ? menuItem.path : undefined"
    :active="isActive"
    :class="`menu-item depth-${depth}`"
    @click="handleClick"
  >
    <VaSidebarItemContent>
      <VaIcon
        v-if="menuItem.icon"
        :name="menuItem.icon"
        class="mr-2"
      />
      <VaSidebarItemTitle>
        {{ menuItem.displayName }}
      </VaSidebarItemTitle>
    </VaSidebarItemContent>
  </VaSidebarItem>
</template>

<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import type { MenuItem } from '../../stores/menu-store'

interface Props {
  menuItem: MenuItem
  currentRoute: string
  depth?: number
}

const props = withDefaults(defineProps<Props>(), {
  depth: 0
})

const emit = defineEmits<{
  navigate: [menuItem: MenuItem]
}>()

// 확장 상태 관리
const isExpanded = ref(false)

// 자식 메뉴가 있는지 확인
const hasChildren = computed(() => {
  return props.menuItem.children && props.menuItem.children.length > 0
})

// 확장/축소 토글
const toggleExpanded = () => {
  if (hasChildren.value) {
    isExpanded.value = !isExpanded.value
  }
}

// 자식 메뉴 중 활성화된 것이 있는지 확인하는 계산 속성
const hasChildrenActive = computed(() => {
  if (!hasChildren.value) return false
  return hasActiveChild(props.menuItem)
})

// 현재 경로와 자식 메뉴 활성 상태를 감시하여 자동 확장
watch([() => props.currentRoute, hasChildrenActive], ([newRoute, hasActiveChild]) => {
  if (hasChildren.value && (isActive.value || hasActiveChild)) {
    isExpanded.value = true
  }
}, { immediate: true })

// 현재 활성화된 메뉴인지 확인
const isActive = computed(() => {
  if (hasChildren.value) {
    // 부모 메뉴의 경우 자식 중 하나가 활성화되어 있으면 활성화
    return hasActiveChild(props.menuItem)
  }
  // 단일 메뉴의 경우 현재 라우트와 일치하면 활성화
  return props.menuItem.path === props.currentRoute || props.menuItem.name === props.currentRoute
})

// 자식 메뉴 중 활성화된 것이 있는지 재귀적으로 확인
const hasActiveChild = (menuItem: MenuItem): boolean => {
  if (menuItem.path === props.currentRoute || menuItem.name === props.currentRoute) {
    return true
  }
  
  if (menuItem.children) {
    return menuItem.children.some(child => hasActiveChild(child))
  }
  
  return false
}

// 텍스트 색상 결정
const getTextColor = () => {
  return isActive.value ? 'primary' : 'textPrimary'
}

// 클릭 처리
const handleClick = () => {
  if (!hasChildren.value && props.menuItem.path) {
    emit('navigate', props.menuItem)
  }
}
</script>

<style scoped>
.menu-group {
  margin-bottom: 2px;
}

.menu-parent {
  cursor: pointer;
}

.menu-parent:hover {
  background-color: var(--va-background-secondary);
}

.children-container {
  padding-left: 16px;
  border-left: 2px solid var(--va-background-border);
  margin-left: 12px;
}

.menu-item {
  transition: all 0.2s ease;
}

.menu-item:hover {
  background-color: var(--va-background-secondary);
  transform: translateX(2px);
}

.depth-1 {
  padding-left: 24px;
}

.depth-2 {
  padding-left: 48px;
}

.depth-3 {
  padding-left: 72px;
}

.transition-transform {
  transition: transform 0.2s ease;
}

.rotate-180 {
  transform: rotate(180deg);
}
</style>
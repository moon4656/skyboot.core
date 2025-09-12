<template>
  <div class="menu-test">
    <h2>메뉴 테스트 컴포넌트</h2>
    
    <!-- 로딩 상태 -->
    <div v-if="isLoading" class="loading">
      <va-progress-circle indeterminate />
      <p>메뉴 로딩 중...</p>
    </div>
    
    <!-- 에러 상태 -->
    <div v-else-if="error" class="error">
      <va-alert color="danger" :model-value="true">
        <h4>메뉴 로딩 실패</h4>
        <p>{{ error }}</p>
      </va-alert>
      <va-button @click="refreshMenu" color="primary" class="mt-3">
        다시 시도
      </va-button>
    </div>
    
    <!-- 메뉴 데이터 표시 -->
    <div v-else-if="hasMenuItems" class="menu-data">
      <va-alert color="success" :model-value="true" class="mb-4">
        <h4>메뉴 로딩 성공!</h4>
        <p>총 {{ menuStats.total }}개의 메뉴가 로드되었습니다.</p>
      </va-alert>
      
      <!-- 메뉴 통계 -->
      <div class="menu-stats mb-4">
        <h3>메뉴 통계</h3>
        <div class="stats-grid">
          <va-card class="stat-card">
            <va-card-content>
              <h4>전체 메뉴</h4>
              <p class="stat-number">{{ menuStats.total }}</p>
            </va-card-content>
          </va-card>
          
          <va-card class="stat-card">
            <va-card-content>
              <h4>활성 메뉴</h4>
              <p class="stat-number">{{ menuStats.active }}</p>
            </va-card-content>
          </va-card>
          
          <va-card class="stat-card">
            <va-card-content>
              <h4>1단계 메뉴</h4>
              <p class="stat-number">{{ menuStats.byLevel.level1 }}</p>
            </va-card-content>
          </va-card>
          
          <va-card class="stat-card">
            <va-card-content>
              <h4>2단계 메뉴</h4>
              <p class="stat-number">{{ menuStats.byLevel.level2 }}</p>
            </va-card-content>
          </va-card>
        </div>
      </div>
      
      <!-- 메뉴 트리 표시 -->
      <div class="menu-tree">
        <h3>메뉴 트리</h3>
        <va-tree-view :nodes="treeNodes" />
      </div>
      
      <!-- 메뉴 검색 테스트 -->
      <div class="menu-search mt-4">
        <h3>메뉴 검색 테스트</h3>
        <va-input
          v-model="searchKeyword"
          placeholder="메뉴 검색..."
          class="mb-3"
        />
        <div v-if="searchResults.length > 0">
          <h4>검색 결과 ({{ searchResults.length }}개)</h4>
          <va-list>
            <va-list-item
              v-for="menu in searchResults"
              :key="menu.id"
            >
              <va-list-item-section>
                <va-list-item-label>{{ menu.name }}</va-list-item-label>
                <va-list-item-label caption>
                  {{ menu.description || '설명 없음' }}
                </va-list-item-label>
              </va-list-item-section>
            </va-list-item>
          </va-list>
        </div>
        <div v-else-if="searchKeyword">
          <p>검색 결과가 없습니다.</p>
        </div>
      </div>
    </div>
    
    <!-- 메뉴 없음 -->
    <div v-else class="no-menu">
      <va-alert color="warning" :model-value="true">
        <h4>메뉴 데이터 없음</h4>
        <p>로드된 메뉴가 없습니다.</p>
      </va-alert>
      <va-button @click="refreshMenu" color="primary" class="mt-3">
        메뉴 새로고침
      </va-button>
    </div>
    
    <!-- 컨트롤 버튼 -->
    <div class="controls mt-4">
      <va-button @click="refreshMenu" color="primary" :loading="isLoading">
        메뉴 새로고침
      </va-button>
      <va-button @click="clearCache" color="secondary" class="ml-2">
        캐시 클리어
      </va-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useMenu } from '@/composables/useMenu'
import { useMenuStore } from '@/stores/menu'
import type { MenuTreeNode } from '@/services/api'

const {
  menuItems,
  isLoading,
  error,
  hasMenuItems,
  refreshMenu,
  searchMenus,
  menuStats
} = useMenu()

const menuStore = useMenuStore()
const { clearCache } = menuStore

// 검색 기능
const searchKeyword = ref('')
const searchResults = ref<MenuTreeNode[]>([])

// 검색어 변경 시 검색 실행
watch(searchKeyword, (newKeyword) => {
  if (newKeyword.trim()) {
    searchResults.value = searchMenus(newKeyword)
  } else {
    searchResults.value = []
  }
})

// 트리뷰용 노드 변환
const treeNodes = computed(() => {
  const convertToTreeNode = (menu: MenuTreeNode): any => {
    return {
      id: menu.id,
      label: menu.name,
      children: menu.children?.map(convertToTreeNode) || []
    }
  }
  
  return menuItems.value.map(convertToTreeNode)
})
</script>

<style scoped>
.menu-test {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.stat-card {
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: var(--va-primary);
  margin: 8px 0;
}

.menu-tree {
  margin-top: 24px;
}

.controls {
  display: flex;
  gap: 12px;
  padding: 20px 0;
  border-top: 1px solid var(--va-background-border);
}

.error, .no-menu {
  text-align: center;
  padding: 40px;
}
</style>
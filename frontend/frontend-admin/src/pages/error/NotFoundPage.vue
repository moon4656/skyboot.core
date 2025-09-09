<template>
  <div class="error-container">
    <div class="error-content">
      <!-- 에러 일러스트레이션 -->
      <div class="error-illustration">
        <VaIcon
          name="search_off"
          size="8rem"
          color="warning"
        />
      </div>

      <!-- 에러 정보 -->
      <div class="error-info">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">페이지를 찾을 수 없습니다</h2>
        <p class="error-description">
          요청하신 페이지가 존재하지 않거나 이동되었습니다.<br>
          URL을 다시 확인하거나 다른 페이지를 이용해 주세요.
        </p>
        
        <!-- 현재 경로 표시 -->
        <div class="current-path">
          <VaChip
            color="warning"
            outline
            size="small"
          >
            <VaIcon name="link" size="small" class="mr-1" />
            {{ currentPath }}
          </VaChip>
        </div>
      </div>

      <!-- 액션 버튼 -->
      <div class="error-actions">
        <VaButton
          color="primary"
          size="large"
          @click="goBack"
        >
          <VaIcon name="arrow_back" class="mr-2" />
          이전 페이지로
        </VaButton>
        
        <VaButton
          color="secondary"
          preset="secondary"
          size="large"
          @click="goHome"
        >
          <VaIcon name="home" class="mr-2" />
          홈으로 가기
        </VaButton>
      </div>

      <!-- 추천 페이지 -->
      <div class="error-suggestions">
        <VaCard class="suggestions-card">
          <VaCardContent>
            <h3 class="suggestions-title">
              <VaIcon name="explore" class="mr-2" />
              추천 페이지
            </h3>
            
            <div class="suggestions-grid">
              <div
                v-for="suggestion in suggestions"
                :key="suggestion.path"
                class="suggestion-item"
                @click="goToPage(suggestion.path)"
              >
                <VaIcon
                  :name="suggestion.icon"
                  :color="suggestion.color"
                  size="1.5rem"
                />
                <div class="suggestion-info">
                  <div class="suggestion-name">{{ suggestion.name }}</div>
                  <div class="suggestion-description">{{ suggestion.description }}</div>
                </div>
                <VaIcon name="chevron_right" size="small" color="secondary" />
              </div>
            </div>
          </VaCardContent>
        </VaCard>
      </div>

      <!-- 검색 기능 -->
      <div class="error-search">
        <VaCard class="search-card">
          <VaCardContent>
            <h3 class="search-title">
              <VaIcon name="search" class="mr-2" />
              페이지 검색
            </h3>
            
            <div class="search-input">
              <VaInput
                v-model="searchQuery"
                placeholder="찾고 있는 페이지를 검색해보세요..."
                @keyup.enter="performSearch"
              >
                <template #appendInner>
                  <VaButton
                    preset="secondary"
                    size="small"
                    icon="search"
                    @click="performSearch"
                  />
                </template>
              </VaInput>
            </div>
            
            <div v-if="searchResults.length > 0" class="search-results">
              <div class="search-results-title">검색 결과:</div>
              <div
                v-for="result in searchResults"
                :key="result.path"
                class="search-result-item"
                @click="goToPage(result.path)"
              >
                <VaIcon :name="result.icon" size="small" class="mr-2" />
                {{ result.name }}
              </div>
            </div>
            
            <div v-else-if="searchQuery && hasSearched" class="no-results">
              <VaIcon name="search_off" class="mr-2" />
              검색 결과가 없습니다.
            </div>
          </VaCardContent>
        </VaCard>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/auth';
import { useMenuStore } from '../../stores/menu';
import { useToast } from 'vuestic-ui';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const menuStore = useMenuStore();
const { init: notify } = useToast();

// 검색 관련 상태
const searchQuery = ref('');
const searchResults = ref<any[]>([]);
const hasSearched = ref(false);

// 현재 경로
const currentPath = computed(() => route.fullPath);

// 추천 페이지
const suggestions = ref([
  {
    name: '대시보드',
    description: '시스템 현황 및 통계',
    path: '/dashboard',
    icon: 'dashboard',
    color: 'primary',
  },
  {
    name: '사용자 관리',
    description: '사용자 계정 관리',
    path: '/admin/users',
    icon: 'people',
    color: 'success',
  },
  {
    name: '메뉴 관리',
    description: '시스템 메뉴 설정',
    path: '/admin/menus',
    icon: 'menu',
    color: 'info',
  },
  {
    name: '권한 관리',
    description: '사용자 권한 설정',
    path: '/admin/permissions',
    icon: 'security',
    color: 'warning',
  },
]);

// 이전 페이지로 이동
const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1);
  } else {
    goHome();
  }
};

// 홈으로 이동
const goHome = () => {
  if (authStore.isAuthenticated) {
    router.push('/dashboard');
  } else {
    router.push('/login');
  }
};

// 특정 페이지로 이동
const goToPage = (path: string) => {
  router.push(path);
};

// 검색 수행
const performSearch = () => {
  hasSearched.value = true;
  
  if (!searchQuery.value.trim()) {
    searchResults.value = [];
    return;
  }
  
  // 메뉴에서 검색
  const query = searchQuery.value.toLowerCase();
  const allMenus = getAllMenus(menuStore.menuTree);
  
  searchResults.value = allMenus.filter(menu => 
    menu.name.toLowerCase().includes(query) ||
    (menu.description && menu.description.toLowerCase().includes(query))
  ).slice(0, 5); // 최대 5개 결과만 표시
  
  if (searchResults.value.length === 0) {
    notify({
      message: `"${searchQuery.value}"에 대한 검색 결과가 없습니다.`,
      color: 'warning',
      duration: 3000,
    });
  }
};

// 모든 메뉴 가져오기 (재귀적으로)
const getAllMenus = (menus: any[]): any[] => {
  const result: any[] = [];
  
  const traverse = (menuList: any[]) => {
    menuList.forEach(menu => {
      if (menu.path && menu.path !== '#') {
        result.push({
          name: menu.name,
          path: menu.path,
          icon: menu.icon || 'folder',
          description: menu.description,
        });
      }
      
      if (menu.children && menu.children.length > 0) {
        traverse(menu.children);
      }
    });
  };
  
  traverse(menus);
  return result;
};
</script>

<style scoped>
.error-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  padding: 2rem;
}

.error-content {
  text-align: center;
  max-width: 800px;
  width: 100%;
}

.error-illustration {
  margin-bottom: 2rem;
  animation: float 3s ease-in-out infinite;
}

.error-info {
  margin-bottom: 3rem;
}

.error-code {
  font-size: 6rem;
  font-weight: 900;
  color: #ff9800;
  margin: 0;
  line-height: 1;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.error-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin: 1rem 0;
}

.error-description {
  font-size: 1.125rem;
  color: #666;
  line-height: 1.6;
  margin: 0 0 1rem 0;
}

.current-path {
  margin-top: 1rem;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.error-suggestions,
.error-search {
  margin-bottom: 2rem;
}

.suggestions-card,
.search-card {
  text-align: left;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.suggestions-title,
.search-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
}

.suggestions-grid {
  display: grid;
  gap: 0.75rem;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  background: #fafafa;
}

.suggestion-item:hover {
  background: #f0f0f0;
  border-color: #1976d2;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.suggestion-info {
  flex: 1;
}

.suggestion-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.suggestion-description {
  font-size: 0.875rem;
  color: #666;
}

.search-input {
  margin-bottom: 1rem;
}

.search-results {
  margin-top: 1rem;
}

.search-results-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.875rem;
}

.search-result-item:hover {
  background-color: #f0f0f0;
}

.no-results {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  color: #666;
  font-size: 0.875rem;
}

.mr-1 {
  margin-right: 0.25rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

@media (max-width: 768px) {
  .error-container {
    padding: 1rem;
  }
  
  .error-code {
    font-size: 4rem;
  }
  
  .error-title {
    font-size: 1.5rem;
  }
  
  .error-description {
    font-size: 1rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .error-actions .va-button {
    width: 100%;
    max-width: 200px;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .error-container {
    padding: 0.5rem;
  }
  
  .error-illustration {
    margin-bottom: 1rem;
  }
  
  .error-illustration .va-icon {
    font-size: 4rem !important;
  }
  
  .error-code {
    font-size: 3rem;
  }
  
  .error-info {
    margin-bottom: 2rem;
  }
  
  .error-actions {
    margin-bottom: 2rem;
  }
  
  .suggestion-item {
    padding: 0.75rem;
  }
}
</style>
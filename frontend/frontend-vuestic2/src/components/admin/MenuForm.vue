<template>
  <div class="menu-form">
    <va-form ref="formRef" @submit.prevent="handleSubmit">
      <div class="row">
        <!-- 메뉴명 -->
        <div class="flex md6">
          <va-input
            v-model="formData.name"
            label="메뉴명"
            placeholder="메뉴명을 입력하세요"
            :rules="nameRules"
            required
            class="mb-3"
          />
        </div>

        <!-- 경로 -->
        <div class="flex md6">
          <va-input
            v-model="formData.path"
            label="경로"
            placeholder="/admin/example"
            :rules="pathRules"
            required
            class="mb-3"
          />
        </div>
      </div>

      <div class="row">
        <!-- 아이콘 -->
        <div class="flex md6">
          <va-input
            v-model="formData.icon"
            label="아이콘"
            placeholder="Material Icons 이름"
            class="mb-3"
          >
            <template #appendInner>
              <va-icon
                v-if="formData.icon"
                :name="formData.icon"
                color="primary"
              />
            </template>
          </va-input>
        </div>

        <!-- 상위 메뉴 -->
        <div class="flex md6">
          <va-select
            v-model="formData.parent_id"
            label="상위 메뉴"
            placeholder="상위 메뉴를 선택하세요"
            :options="parentOptions"
            clearable
            class="mb-3"
          />
        </div>
      </div>

      <div class="row">
        <!-- 메뉴 타입 -->
        <div class="flex md4">
          <va-select
            v-model="formData.type"
            label="메뉴 타입"
            :options="typeOptions"
            required
            class="mb-3"
          />
        </div>

        <!-- 상태 -->
        <div class="flex md4">
          <va-select
            v-model="formData.status"
            label="상태"
            :options="statusOptions"
            required
            class="mb-3"
          />
        </div>

        <!-- 순서 -->
        <div class="flex md4">
          <va-input
            v-model.number="formData.sort_order"
            label="순서"
            type="number"
            min="0"
            class="mb-3"
          />
        </div>
      </div>

      <!-- 권한 -->
      <div class="row">
        <div class="flex md12">
          <va-input
            v-model="formData.permission"
            label="권한"
            placeholder="admin.menus.read"
            :rules="permissionRules"
            class="mb-3"
          />
        </div>
      </div>

      <!-- 설명 -->
      <div class="row">
        <div class="flex md12">
          <va-textarea
            v-model="formData.description"
            label="설명"
            placeholder="메뉴에 대한 설명을 입력하세요"
            rows="3"
            class="mb-3"
          />
        </div>
      </div>

      <!-- 아이콘 선택 도우미 -->
      <div class="row" v-if="showIconHelper">
        <div class="flex md12">
          <va-card class="icon-helper">
            <va-card-title>자주 사용되는 아이콘</va-card-title>
            <va-card-content>
              <div class="icon-grid">
                <div
                  v-for="icon in commonIcons"
                  :key="icon.name"
                  class="icon-item"
                  @click="selectIcon(icon.name)"
                  :class="{ active: formData.icon === icon.name }"
                >
                  <va-icon :name="icon.name" size="24px" />
                  <span class="icon-name">{{ icon.label }}</span>
                </div>
              </div>
            </va-card-content>
          </va-card>
        </div>
      </div>

      <!-- 아이콘 도우미 토글 -->
      <div class="row">
        <div class="flex md12">
          <va-button
            preset="plain"
            icon="palette"
            @click="showIconHelper = !showIconHelper"
            class="mb-3"
          >
            {{ showIconHelper ? '아이콘 도우미 숨기기' : '아이콘 도우미 보기' }}
          </va-button>
        </div>
      </div>
    </va-form>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

// Props 정의
interface Props {
  modelValue: {
    name: string
    path: string
    icon: string
    parent_id: number | null
    type: string
    status: string
    sort_order: number
    description: string
    permission: string
  }
  parentOptions: Array<{ text: string; value: number }>
  isEditing: boolean
}

const props = withDefaults(defineProps<Props>(), {
  isEditing: false
})

// Emits 정의
const emit = defineEmits<{
  'update:modelValue': [value: Props['modelValue']]
}>()

// 반응형 데이터
const formRef = ref()
const showIconHelper = ref(false)

// 폼 데이터
const formData = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 검증 규칙
const nameRules = [
  (value: string) => !!value || '메뉴명은 필수입니다.',
  (value: string) => value.length >= 2 || '메뉴명은 2자 이상이어야 합니다.',
  (value: string) => value.length <= 50 || '메뉴명은 50자 이하여야 합니다.'
]

const pathRules = [
  (value: string) => !!value || '경로는 필수입니다.',
  (value: string) => value.startsWith('/') || '경로는 /로 시작해야 합니다.',
  (value: string) => !/\s/.test(value) || '경로에는 공백이 포함될 수 없습니다.',
  (value: string) => /^[a-zA-Z0-9/_-]+$/.test(value) || '경로는 영문, 숫자, /, _, -만 사용 가능합니다.'
]

const permissionRules = [
  (value: string) => !!value || '권한은 필수입니다.',
  (value: string) => /^[a-zA-Z0-9._-]+$/.test(value) || '권한은 영문, 숫자, ., _, -만 사용 가능합니다.'
]

// 선택 옵션
const typeOptions = [
  { text: '메뉴', value: 'menu' },
  { text: '액션', value: 'action' }
]

const statusOptions = [
  { text: '활성', value: 'active' },
  { text: '비활성', value: 'inactive' },
  { text: '곧 출시', value: 'coming_soon' }
]

// 자주 사용되는 아이콘
const commonIcons = [
  { name: 'dashboard', label: '대시보드' },
  { name: 'people', label: '사용자' },
  { name: 'menu', label: '메뉴' },
  { name: 'settings', label: '설정' },
  { name: 'security', label: '보안' },
  { name: 'admin_panel_settings', label: '관리자' },
  { name: 'apps', label: '앱' },
  { name: 'code', label: '코드' },
  { name: 'forum', label: '게시판' },
  { name: 'folder', label: '폴더' },
  { name: 'description', label: '문서' },
  { name: 'analytics', label: '분석' },
  { name: 'notifications', label: '알림' },
  { name: 'help', label: '도움말' },
  { name: 'info', label: '정보' },
  { name: 'home', label: '홈' },
  { name: 'business', label: '비즈니스' },
  { name: 'work', label: '작업' },
  { name: 'group', label: '그룹' },
  { name: 'lock', label: '잠금' },
  { name: 'key', label: '키' },
  { name: 'visibility', label: '보기' },
  { name: 'edit', label: '편집' },
  { name: 'delete', label: '삭제' },
  { name: 'add', label: '추가' },
  { name: 'save', label: '저장' },
  { name: 'cancel', label: '취소' },
  { name: 'check', label: '확인' },
  { name: 'close', label: '닫기' },
  { name: 'search', label: '검색' },
  { name: 'filter_list', label: '필터' },
  { name: 'sort', label: '정렬' },
  { name: 'refresh', label: '새로고침' },
  { name: 'download', label: '다운로드' },
  { name: 'upload', label: '업로드' },
  { name: 'print', label: '인쇄' },
  { name: 'share', label: '공유' },
  { name: 'star', label: '즐겨찾기' },
  { name: 'bookmark', label: '북마크' },
  { name: 'favorite', label: '좋아요' },
  { name: 'thumb_up', label: '추천' },
  { name: 'comment', label: '댓글' },
  { name: 'chat', label: '채팅' },
  { name: 'mail', label: '메일' },
  { name: 'phone', label: '전화' },
  { name: 'location_on', label: '위치' },
  { name: 'calendar_today', label: '달력' },
  { name: 'schedule', label: '일정' },
  { name: 'timer', label: '타이머' },
  { name: 'history', label: '히스토리' },
  { name: 'trending_up', label: '상승' },
  { name: 'trending_down', label: '하락' },
  { name: 'bar_chart', label: '차트' },
  { name: 'pie_chart', label: '파이차트' },
  { name: 'table_chart', label: '테이블' },
  { name: 'list', label: '목록' },
  { name: 'grid_view', label: '그리드' },
  { name: 'view_list', label: '리스트뷰' },
  { name: 'view_module', label: '모듈뷰' }
]

// 메서드
const selectIcon = (iconName: string) => {
  formData.value = {
    ...formData.value,
    icon: iconName
  }
}

const handleSubmit = () => {
  // 폼 검증은 부모 컴포넌트에서 처리
}

// 메뉴 타입에 따른 경로 자동 생성
watch(() => formData.value.name, (newName) => {
  if (newName && !props.isEditing) {
    // 새 메뉴 생성 시에만 자동 경로 생성
    const pathName = newName
      .toLowerCase()
      .replace(/[^a-zA-Z0-9가-힣\s]/g, '') // 특수문자 제거
      .replace(/\s+/g, '-') // 공백을 하이픈으로
      .replace(/[가-힣]/g, '') // 한글 제거 (영문만 유지)
    
    if (pathName) {
      const parentPath = props.parentOptions.find(p => p.value === formData.value.parent_id)?.text || ''
      const basePath = parentPath ? `/admin/${parentPath.toLowerCase()}` : '/admin'
      
      formData.value = {
        ...formData.value,
        path: `${basePath}/${pathName}`
      }
    }
  }
})

// 메뉴 타입에 따른 권한 자동 생성
watch(() => [formData.value.name, formData.value.type], ([newName, newType]) => {
  if (newName && newType && !props.isEditing) {
    const permissionName = newName
      .toLowerCase()
      .replace(/[^a-zA-Z0-9\s]/g, '')
      .replace(/\s+/g, '_')
      .replace(/[가-힣]/g, '') // 한글 제거
    
    if (permissionName) {
      const action = newType === 'menu' ? 'read' : 'access'
      formData.value = {
        ...formData.value,
        permission: `admin.${permissionName}.${action}`
      }
    }
  }
})

// 폼 검증 메서드 노출
defineExpose({
  validate: () => formRef.value?.validate(),
  reset: () => formRef.value?.reset()
})
</script>

<style scoped>
.menu-form {
  padding: 1rem;
}

.icon-helper {
  margin-top: 1rem;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 0.75rem;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}

.icon-item:hover {
  border-color: #1976d2;
  background: #f5f5f5;
  transform: translateY(-1px);
}

.icon-item.active {
  border-color: #1976d2;
  background: #e3f2fd;
  color: #1976d2;
}

.icon-name {
  font-size: 0.75rem;
  margin-top: 0.25rem;
  text-align: center;
  color: #666;
}

.icon-item.active .icon-name {
  color: #1976d2;
  font-weight: 500;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .icon-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }
  
  .icon-item {
    padding: 0.5rem;
  }
  
  .icon-name {
    font-size: 0.7rem;
  }
}

/* 스크롤바 스타일링 */
.icon-grid::-webkit-scrollbar {
  width: 6px;
}

.icon-grid::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.icon-grid::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.icon-grid::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>
import { createVuesticEssential } from 'vuestic-ui'

/**
 * SkyBoot Core 커스텀 테마 설정
 * 부드러운 베이지/네이비 색상 팔레트를 사용한 전문적인 관리자 테마
 */
export const skybootTheme = {
  colors: {
    // 주요 색상 (네이비 계열)
    primary: '#2C3E50',      // 진한 네이비
    secondary: '#34495E',    // 중간 네이비
    success: '#27AE60',      // 성공 (그린)
    info: '#3498DB',         // 정보 (블루)
    warning: '#F39C12',      // 경고 (오렌지)
    danger: '#E74C3C',       // 위험 (레드)
    
    // 배경 색상 (베이지 계열)
    backgroundPrimary: '#FDFCF8',    // 메인 배경 (아이보리)
    backgroundSecondary: '#F8F6F0',  // 보조 배경 (연한 베이지)
    backgroundElement: '#FFFFFF',     // 엘리먼트 배경 (화이트)
    backgroundBorder: '#E8E6E0',     // 테두리 (연한 베이지)
    
    // 텍스트 색상
    textPrimary: '#2C3E50',      // 주요 텍스트 (진한 네이비)
    textInverted: '#FFFFFF',     // 반전 텍스트 (화이트)
    
    // 그라데이션 색상
    backgroundLanding: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    
    // 추가 색상 팔레트
    // 네이비 계열
    navy: {
      50: '#F7F9FC',
      100: '#E3EAF2',
      200: '#C5D2E0',
      300: '#A3B9CC',
      400: '#7A9BB8',
      500: '#5A7FA3',
      600: '#4A6B8A',
      700: '#3A5670',
      800: '#2C4257',
      900: '#1E2D3E'
    },
    
    // 베이지 계열
    beige: {
      50: '#FDFCF8',
      100: '#FAF7F0',
      200: '#F5F0E8',
      300: '#F0E9DF',
      400: '#EBE2D7',
      500: '#E6DBCE',
      600: '#D4C4B0',
      700: '#C2AD92',
      800: '#B09674',
      900: '#9E7F56'
    },
    
    // 상태별 색상 (부드러운 톤)
    states: {
      active: '#27AE60',
      inactive: '#95A5A6',
      pending: '#F39C12',
      error: '#E74C3C',
      warning: '#E67E22',
      info: '#3498DB'
    }
  },
  
  // 그림자 설정
  shadow: {
    sm: '0 1px 3px 0 rgba(44, 62, 80, 0.1), 0 1px 2px 0 rgba(44, 62, 80, 0.06)',
    md: '0 4px 6px -1px rgba(44, 62, 80, 0.1), 0 2px 4px -1px rgba(44, 62, 80, 0.06)',
    lg: '0 10px 15px -3px rgba(44, 62, 80, 0.1), 0 4px 6px -2px rgba(44, 62, 80, 0.05)',
    xl: '0 20px 25px -5px rgba(44, 62, 80, 0.1), 0 10px 10px -5px rgba(44, 62, 80, 0.04)'
  },
  
  // 타이포그래피
  typography: {
    fontFamily: {
      sans: ['Inter', 'Noto Sans KR', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'Consolas', 'Monaco', 'monospace']
    },
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem'
    },
    fontWeight: {
      light: '300',
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700'
    }
  },
  
  // 간격 설정
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '1rem',
    lg: '1.5rem',
    xl: '2rem',
    '2xl': '3rem',
    '3xl': '4rem'
  },
  
  // 테두리 반경
  borderRadius: {
    none: '0',
    sm: '0.125rem',
    md: '0.375rem',
    lg: '0.5rem',
    xl: '0.75rem',
    '2xl': '1rem',
    full: '9999px'
  },
  
  // 컴포넌트별 테마
  components: {
    // 버튼 테마
    VaButton: {
      borderRadius: '0.5rem',
      fontWeight: '500',
      transition: 'all 0.2s ease-in-out'
    },
    
    // 카드 테마
    VaCard: {
      borderRadius: '0.75rem',
      boxShadow: '0 4px 6px -1px rgba(44, 62, 80, 0.1)',
      backgroundColor: '#FFFFFF'
    },
    
    // 입력 필드 테마
    VaInput: {
      borderRadius: '0.5rem',
      backgroundColor: '#FFFFFF',
      borderColor: '#E8E6E0'
    },
    
    // 사이드바 테마
    VaSidebar: {
      backgroundColor: '#2C3E50',
      color: '#FFFFFF',
      width: '280px'
    },
    
    // 네비게이션 바 테마
    VaNavbar: {
      backgroundColor: '#FFFFFF',
      borderBottom: '1px solid #E8E6E0',
      boxShadow: '0 1px 3px 0 rgba(44, 62, 80, 0.1)'
    },
    
    // 테이블 테마
    VaDataTable: {
      backgroundColor: '#FFFFFF',
      borderRadius: '0.75rem',
      headerBackgroundColor: '#F8F6F0',
      stripedColor: '#FDFCF8'
    },
    
    // 모달 테마
    VaModal: {
      borderRadius: '0.75rem',
      backgroundColor: '#FFFFFF',
      backdropColor: 'rgba(44, 62, 80, 0.5)'
    },
    
    // 알림 테마
    VaAlert: {
      borderRadius: '0.5rem',
      fontWeight: '500'
    },
    
    // 배지 테마
    VaBadge: {
      borderRadius: '0.375rem',
      fontWeight: '500',
      fontSize: '0.75rem'
    },
    
    // 칩 테마
    VaChip: {
      borderRadius: '0.5rem',
      fontWeight: '500'
    },
    
    // 프로그레스 바 테마
    VaProgressBar: {
      borderRadius: '0.25rem',
      backgroundColor: '#F8F6F0'
    },
    
    // 스위치 테마
    VaSwitch: {
      borderRadius: '1rem'
    },
    
    // 체크박스 테마
    VaCheckbox: {
      borderRadius: '0.25rem'
    },
    
    // 라디오 테마
    VaRadio: {
      borderRadius: '50%'
    },
    
    // 슬라이더 테마
    VaSlider: {
      trackColor: '#F8F6F0',
      thumbColor: '#2C3E50'
    },
    
    // 탭 테마
    VaTabs: {
      borderRadius: '0.5rem',
      backgroundColor: '#F8F6F0'
    },
    
    // 아코디언 테마
    VaAccordion: {
      borderRadius: '0.5rem',
      backgroundColor: '#FFFFFF'
    },
    
    // 드롭다운 테마
    VaDropdown: {
      borderRadius: '0.5rem',
      backgroundColor: '#FFFFFF',
      boxShadow: '0 10px 15px -3px rgba(44, 62, 80, 0.1)'
    },
    
    // 툴팁 테마
    VaTooltip: {
      borderRadius: '0.375rem',
      backgroundColor: '#2C3E50',
      color: '#FFFFFF'
    },
    
    // 페이지네이션 테마
    VaPagination: {
      borderRadius: '0.5rem'
    },
    
    // 브레드크럼 테마
    VaBreadcrumbs: {
      color: '#7A9BB8',
      activeColor: '#2C3E50'
    },
    
    // 스피너 테마
    VaInnerLoading: {
      color: '#2C3E50'
    },
    
    // 아바타 테마
    VaAvatar: {
      backgroundColor: '#F8F6F0',
      color: '#2C3E50'
    },
    
    // 아이콘 테마
    VaIcon: {
      color: '#2C3E50'
    },
    
    // 디바이더 테마
    VaDivider: {
      color: '#E8E6E0'
    },
    
    // 스켈레톤 테마
    VaSkeleton: {
      backgroundColor: '#F8F6F0',
      animationColor: '#FDFCF8'
    }
  },
  
  // 애니메이션 설정
  animations: {
    duration: {
      fast: '150ms',
      normal: '250ms',
      slow: '350ms'
    },
    easing: {
      ease: 'ease',
      easeIn: 'ease-in',
      easeOut: 'ease-out',
      easeInOut: 'ease-in-out'
    }
  },
  
  // 반응형 브레이크포인트
  breakpoints: {
    xs: '0px',
    sm: '576px',
    md: '768px',
    lg: '992px',
    xl: '1200px',
    xxl: '1400px'
  }
}

/**
 * 다크 모드 테마 (향후 확장용)
 */
export const skybootDarkTheme = {
  ...skybootTheme,
  colors: {
    ...skybootTheme.colors,
    // 다크 모드 색상 오버라이드
    backgroundPrimary: '#1A1A1A',
    backgroundSecondary: '#2D2D2D',
    backgroundElement: '#3A3A3A',
    backgroundBorder: '#4A4A4A',
    textPrimary: '#FFFFFF',
    textInverted: '#1A1A1A'
  }
}

/**
 * Vuestic UI 설정
 */
export const vuesticConfig = createVuesticEssential({
  config: {
    colors: skybootTheme.colors,
    components: skybootTheme.components,
    icons: [
      {
        name: 'material-icons',
        resolve: ({ icon }) => ({ class: 'material-icons', content: icon })
      }
    ]
  }
})

export default skybootTheme
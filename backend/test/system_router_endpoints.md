# System Router API 엔드포인트 목록

## 개요
`system_router.py` 파일에서 추출한 모든 API 엔드포인트 목록입니다.

## 기본 정보
- **라우터 프리픽스**: `/system`
- **태그**: 시스템 관리
- **총 엔드포인트 수**: 22개
- **인증**: Bearer Token 필요 (모든 엔드포인트)

## 엔드포인트 목록

### 1. 시스템 로그(SysLog) API (8개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| POST | `/system/logs/` | `create_system_log` | 시스템 로그 생성 |
| GET | `/system/logs/` | `get_system_logs` | 시스템 로그 목록 조회 (페이징) |
| GET | `/system/logs/search` | `search_system_logs` | 시스템 로그 검색 |
| GET | `/system/logs/statistics` | `get_system_log_statistics` | 시스템 로그 통계 |
| GET | `/system/logs/{log_id}` | `get_system_log` | 시스템 로그 상세 조회 |
| PUT | `/system/logs/{log_id}` | `update_system_log` | 시스템 로그 수정 |
| DELETE | `/system/logs/{log_id}` | `delete_system_log` | 시스템 로그 삭제 |

### 2. 웹 로그(WebLog) API (9개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| POST | `/system/web-logs/` | `create_web_log` | 웹 로그 생성 |
| GET | `/system/web-logs/` | `get_web_logs` | 웹 로그 목록 조회 (페이징) |
| GET | `/system/web-logs/search` | `search_web_logs` | 웹 로그 검색 |
| GET | `/system/web-logs/popular-pages` | `get_popular_pages` | 인기 페이지 조회 |
| GET | `/system/web-logs/hourly-traffic` | `get_hourly_traffic` | 시간대별 트래픽 조회 |
| GET | `/system/web-logs/{conect_id}` | `get_web_log` | 웹 로그 상세 조회 |
| PUT | `/system/web-logs/{conect_id}` | `update_web_log` | 웹 로그 수정 |
| DELETE | `/system/web-logs/{conect_id}` | `delete_web_log` | 웹 로그 삭제 |

### 3. 시스템 모니터링 API (5개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| GET | `/system/health` | `get_system_health` | 시스템 상태 확인 |
| GET | `/system/dashboard` | `get_dashboard_summary` | 대시보드 요약 정보 |
| GET | `/system/logs/export` | `export_logs` | 로그 데이터 내보내기 |
| DELETE | `/system/logs/cleanup` | `cleanup_old_logs` | 오래된 로그 정리 |

## 스키마 정보

### 요청 스키마
- `SysLogCreate`: 시스템 로그 생성
- `SysLogUpdate`: 시스템 로그 수정
- `WebLogCreate`: 웹 로그 생성
- `WebLogUpdate`: 웹 로그 수정
- `LogSearchParams`: 로그 검색 파라미터

### 응답 스키마
- `SysLogResponse`: 시스템 로그 응답
- `SysLogPagination`: 페이징된 시스템 로그 목록
- `WebLogResponse`: 웹 로그 응답
- `WebLogPagination`: 페이징된 웹 로그 목록
- `LogStatistics`: 로그 통계 정보
- `SystemHealthCheck`: 시스템 상태 정보
- `DashboardSummary`: 대시보드 요약 정보

### 공통 파라미터
- `skip`, `limit`: 페이징 (기본값: skip=0, limit=100)
- `start_date`, `end_date`: 날짜 범위 필터
- `log_id`: 시스템 로그 ID
- `conect_id`: 웹 로그 접속 ID

## 주요 기능별 분류

### High Priority (핵심 CRUD 기능)
1. **시스템 로그 기본 CRUD**
   - POST `/system/logs/` - 로그 생성
   - GET `/system/logs/` - 로그 목록 조회
   - GET `/system/logs/{log_id}` - 로그 상세 조회
   - PUT `/system/logs/{log_id}` - 로그 수정
   - DELETE `/system/logs/{log_id}` - 로그 삭제

2. **웹 로그 기본 CRUD**
   - POST `/system/web-logs/` - 웹 로그 생성
   - GET `/system/web-logs/` - 웹 로그 목록 조회
   - GET `/system/web-logs/{conect_id}` - 웹 로그 상세 조회
   - PUT `/system/web-logs/{conect_id}` - 웹 로그 수정
   - DELETE `/system/web-logs/{conect_id}` - 웹 로그 삭제

### Medium Priority (검색 및 통계 기능)
1. **검색 기능**
   - GET `/system/logs/search` - 시스템 로그 검색
   - GET `/system/web-logs/search` - 웹 로그 검색

2. **통계 및 분석**
   - GET `/system/logs/statistics` - 시스템 로그 통계
   - GET `/system/web-logs/popular-pages` - 인기 페이지 조회
   - GET `/system/web-logs/hourly-traffic` - 시간대별 트래픽

### Low Priority (관리 및 모니터링 기능)
1. **시스템 모니터링**
   - GET `/system/health` - 시스템 상태 확인
   - GET `/system/dashboard` - 대시보드 요약

2. **데이터 관리**
   - GET `/system/logs/export` - 로그 내보내기
   - DELETE `/system/logs/cleanup` - 로그 정리

## 에러 처리
- 모든 엔드포인트에서 일관된 예외 처리
- HTTP 404 에러 시 한국어 에러 메시지 반환
- HTTP 500 에러 시 내부 서버 오류 처리
- Bearer Token 인증 실패 시 401 에러

## 테스트 전략
1. **단위 테스트**: 각 기능별로 독립적인 테스트
2. **통합 테스트**: 전체 워크플로우 테스트
3. **오류 처리 테스트**: 예외 상황 및 에러 케이스
4. **성능 테스트**: 대용량 데이터 처리 성능

---

**생성일**: 2025년 1월 7일
**파일**: system_router.py
**총 엔드포인트**: 22개
**분석 완료**: ✅
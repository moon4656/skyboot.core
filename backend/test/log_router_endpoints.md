# Log Router API 엔드포인트 목록

## 개요
`log_router.py` 파일에서 추출한 모든 API 엔드포인트 목록입니다.

## 기본 정보
- **라우터 프리픽스**: `/logs`
- **태그**: 로그인 로그 관리
- **총 엔드포인트 수**: 20개

## 엔드포인트 목록

### 1. 로그인 로그 기본 API (8개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| GET | `/logs/` | `get_login_logs` | 로그인 로그 목록 조회 (페이징, 필터링) |
| GET | `/logs/recent` | `get_recent_logs` | 최근 로그인 로그 조회 |
| GET | `/logs/user/{user_id}` | `get_user_logs` | 사용자별 로그인 로그 조회 |
| GET | `/logs/failed` | `get_failed_attempts` | 실패한 로그인 시도 조회 |
| GET | `/logs/{log_id}` | `get_login_log` | 로그인 로그 상세 조회 |
| POST | `/logs/` | `create_login_log` | 로그인 로그 생성 |
| PUT | `/logs/{log_id}` | `update_login_log` | 로그인 로그 수정 |
| DELETE | `/logs/{log_id}` | `delete_login_log` | 로그인 로그 삭제 |

### 2. 로그 통계 및 분석 API (4개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| GET | `/logs/statistics/overview` | `get_login_statistics` | 로그인 통계 조회 |
| GET | `/logs/statistics/daily` | `get_daily_statistics` | 일별 로그인 통계 조회 |
| GET | `/logs/statistics/hourly` | `get_hourly_statistics` | 시간별 로그인 통계 조회 |
| GET | `/logs/statistics/top-ips` | `get_top_ip_statistics` | 상위 IP 주소 통계 조회 |

### 3. 보안 및 모니터링 API (5개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| GET | `/logs/security/alerts` | `get_security_alerts` | 보안 알림 조회 |
| GET | `/logs/security/suspicious` | `get_suspicious_activities` | 의심스러운 활동 조회 |
| GET | `/logs/security/repeated-failures` | `get_repeated_failures` | 반복 실패 시도 조회 |
| GET | `/logs/security/unusual-times` | `get_unusual_login_times` | 비정상 시간대 로그인 조회 |
| GET | `/logs/security/new-ip-logins` | `get_new_ip_logins` | 새로운 IP 로그인 조회 |

### 4. 세션 관리 API (2개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| GET | `/logs/sessions/active` | `get_active_sessions` | 활성 세션 조회 |
| GET | `/logs/sessions/user/{user_id}` | `get_user_sessions` | 사용자 세션 조회 |

### 5. 로그 관리 API (3개)

| 메서드 | 경로 | 함수명 | 설명 |
|--------|------|--------|------|
| POST | `/logs/cleanup` | `cleanup_old_logs` | 오래된 로그 정리 |
| GET | `/logs/export` | `export_logs` | 로그 데이터 내보내기 |
| GET | `/logs/analysis` | `analyze_logs` | 로그 분석 |

## 주요 특징

### 인증
- 대부분의 엔드포인트에서 `get_current_user_from_bearer` 의존성 사용
- JWT 토큰 기반 인증 필요

### 응답 모델
- `LoginLogResponse`: 기본 로그 응답
- `LoginLogPagination`: 페이징된 로그 목록
- `LoginLogStatistics`: 통계 정보
- `SecurityAlertResponse`: 보안 알림
- `SuspiciousActivityResponse`: 의심스러운 활동
- `SessionManagementResponse`: 세션 관리
- `LogExportResponse`: 로그 내보내기
- `LogAnalysisResponse`: 로그 분석

### 공통 파라미터
- `skip`, `limit`: 페이징
- `days`, `hours`: 시간 범위
- `user_id`: 사용자 필터링
- `start_date`, `end_date`: 날짜 범위

### 에러 처리
- 모든 엔드포인트에서 일관된 예외 처리
- HTTP 500 에러 시 한국어 에러 메시지 반환
- HTTP 404 에러 시 리소스 없음 메시지

## 테스트 우선순위

### High Priority (핵심 기능)
1. `GET /logs/` - 기본 로그 목록 조회
2. `POST /logs/` - 로그 생성
3. `GET /logs/{log_id}` - 로그 상세 조회
4. `GET /logs/recent` - 최근 로그 조회

### Medium Priority (통계 및 분석)
1. `GET /logs/statistics/overview` - 통계 조회
2. `GET /logs/failed` - 실패 로그 조회
3. `GET /logs/user/{user_id}` - 사용자별 로그

### Low Priority (고급 기능)
1. 보안 관련 엔드포인트들
2. 세션 관리 엔드포인트들
3. 로그 관리 엔드포인트들

---

**생성일**: 2025년 1월
**파일**: log_router.py
**총 엔드포인트**: 20개
# SkyBoot Core API 엔드포인트 목록

이 문서는 SkyBoot Core API 프로젝트의 모든 엔드포인트를 정리한 목록입니다.

## 📋 목차

1. [인증 관리 (Authentication)](#인증-관리-authentication)
2. [사용자 관리 (User Management)](#사용자-관리-user-management)
3. [조직 관리 (Organization Management)](#조직-관리-organization-management)
4. [우편번호 관리 (Zip Code Management)](#우편번호-관리-zip-code-management)
5. [프로그램 관리 (Program Management)](#프로그램-관리-program-management)
6. [메뉴 관리 (Menu Management)](#메뉴-관리-menu-management)
7. [게시판 관리 (Board Management)](#게시판-관리-board-management)
8. [파일 관리 (File Management)](#파일-관리-file-management)
9. [공통 코드 관리 (Common Code Management)](#공통-코드-관리-common-code-management)
10. [시스템 관리 (System Management)](#시스템-관리-system-management)
11. [로그 관리 (Log Management)](#로그-관리-log-management)
12. [권한 메뉴 관리 (Authorization Menu Management)](#권한-메뉴-관리-authorization-menu-management)

---

## 인증 관리 (Authentication)

**Base URL**: `/auth`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/auth/login` | 사용자 로그인 | 사용자 ID와 비밀번호로 로그인하여 JWT 토큰 발급 |
| POST | `/auth/refresh` | 토큰 갱신 | 리프레시 토큰을 사용하여 새로운 액세스 토큰 발급 |

---

## 사용자 관리 (User Management)

**Base URL**: `/users`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/users/` | 사용자 생성 | 새로운 사용자 생성 (JWT 토큰 필요) |
| POST | `/users/basic` | 사용자 기본 자료 생성 | 기본 사용자 정보로 사용자 생성 (JWT 토큰 필요) |
| GET | `/users/` | 사용자 목록 조회 | 페이지네이션으로 사용자 목록 조회 (JWT 토큰 필요) |
| GET | `/users/search` | 사용자 검색 | 다양한 조건으로 사용자 검색 (JWT 토큰 필요) |
| GET | `/users/{user_id}` | 사용자 상세 조회 | 특정 사용자의 상세 정보 조회 |
| PUT | `/users/{user_id}` | 사용자 정보 수정 | 사용자 정보 업데이트 |
| DELETE | `/users/{user_id}` | 사용자 삭제 | 사용자 삭제 |
| GET | `/users/statistics` | 사용자 통계 | 사용자 관련 통계 정보 조회 |

---

## 조직 관리 (Organization Management)

**Base URL**: `/organizations`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/organizations/` | 조직 생성 | 새로운 조직 생성 |
| GET | `/organizations/` | 조직 목록 조회 | 페이지네이션으로 조직 목록 조회 |
| GET | `/organizations/tree` | 조직 트리 구조 조회 | 조직의 계층 구조를 트리 형태로 조회 |
| GET | `/organizations/{org_no}` | 조직 상세 조회 | 특정 조직의 상세 정보 조회 |
| PUT | `/organizations/{org_no}` | 조직 정보 수정 | 조직 정보 업데이트 |
| DELETE | `/organizations/{org_no}` | 조직 삭제 | 조직 삭제 |
| GET | `/organizations/search` | 조직 검색 | 조직명으로 조직 검색 |

---

## 우편번호 관리 (Zip Code Management)

**Base URL**: `/zip-codes`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/zip-codes/` | 우편번호 생성 | 새로운 우편번호 정보 생성 |
| GET | `/zip-codes/` | 우편번호 목록 조회 | 페이지네이션으로 우편번호 목록 조회 |
| GET | `/zip-codes/search` | 주소로 우편번호 검색 | 주소 정보로 우편번호 검색 |
| GET | `/zip-codes/{sn}` | 우편번호 상세 조회 | 특정 우편번호의 상세 정보 조회 |
| PUT | `/zip-codes/{sn}` | 우편번호 정보 수정 | 우편번호 정보 업데이트 |
| DELETE | `/zip-codes/{sn}` | 우편번호 삭제 | 우편번호 삭제 |

---

## 프로그램 관리 (Program Management)

**Base URL**: `/programs`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/programs/` | 프로그램 생성 | 새로운 프로그램 생성 |
| GET | `/programs/` | 프로그램 목록 조회 | 페이지네이션으로 프로그램 목록 조회 |
| GET | `/programs/search` | 프로그램 검색 | 다양한 조건으로 프로그램 검색 |
| GET | `/programs/{progrm_file_nm}` | 프로그램 상세 조회 | 특정 프로그램의 상세 정보 조회 |
| PUT | `/programs/{progrm_file_nm}` | 프로그램 정보 수정 | 프로그램 정보 업데이트 |
| DELETE | `/programs/{progrm_file_nm}` | 프로그램 삭제 | 프로그램 삭제 |
| GET | `/programs/statistics` | 프로그램 통계 | 프로그램 관련 통계 정보 조회 |

---

## 메뉴 관리 (Menu Management)

**Base URL**: `/menus`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/menus/` | 메뉴 목록 조회 | 페이지네이션으로 메뉴 목록 조회 |
| GET | `/menus/tree` | 메뉴 트리 조회 | 메뉴의 계층 구조를 트리 형태로 조회 |
| POST | `/menus/` | 메뉴 생성 | 새로운 메뉴 생성 |
| GET | `/menus/{menu_id}` | 메뉴 상세 조회 | 특정 메뉴의 상세 정보 조회 |
| PUT | `/menus/{menu_id}` | 메뉴 정보 수정 | 메뉴 정보 업데이트 |
| DELETE | `/menus/{menu_id}` | 메뉴 삭제 | 메뉴 삭제 |
| GET | `/menus/search` | 메뉴 검색 | 메뉴명으로 메뉴 검색 |
| POST | `/menus/move` | 메뉴 이동 | 메뉴의 위치 변경 |
| PUT | `/menus/order` | 메뉴 순서 변경 | 메뉴의 표시 순서 변경 |
| POST | `/menus/copy` | 메뉴 복사 | 메뉴 복사 생성 |
| GET | `/menus/statistics` | 메뉴 통계 | 메뉴 관련 통계 정보 조회 |
| GET | `/menus/{menu_id}/path` | 메뉴 경로 조회 | 메뉴의 전체 경로 조회 |
| POST | `/menus/validate` | 메뉴 검증 | 메뉴 데이터 유효성 검증 |
| GET | `/menus/export` | 메뉴 내보내기 | 메뉴 데이터 내보내기 |
| POST | `/menus/import` | 메뉴 가져오기 | 메뉴 데이터 가져오기 |

---

## 게시판 관리 (Board Management)

### 게시판 마스터 관리
**Base URL**: `/bbs-master`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/bbs-master/` | 게시판 마스터 목록 조회 | 페이지네이션으로 게시판 마스터 목록 조회 |
| POST | `/bbs-master/` | 게시판 마스터 생성 | 새로운 게시판 마스터 생성 |
| GET | `/bbs-master/{bbs_id}` | 게시판 마스터 상세 조회 | 특정 게시판 마스터의 상세 정보 조회 |
| PUT | `/bbs-master/{bbs_id}` | 게시판 마스터 수정 | 게시판 마스터 정보 업데이트 |
| DELETE | `/bbs-master/{bbs_id}` | 게시판 마스터 삭제 | 게시판 마스터 삭제 |
| GET | `/bbs-master/search` | 게시판 마스터 검색 | 게시판명으로 게시판 마스터 검색 |
| GET | `/bbs-master/statistics` | 게시판 통계 | 게시판 관련 통계 정보 조회 |

### 게시글 관리
**Base URL**: `/bbs`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/bbs/` | 게시글 목록 조회 | 페이지네이션으로 게시글 목록 조회 |
| POST | `/bbs/` | 게시글 생성 | 새로운 게시글 생성 |
| GET | `/bbs/{ntt_id}` | 게시글 상세 조회 | 특정 게시글의 상세 정보 조회 |
| PUT | `/bbs/{ntt_id}` | 게시글 수정 | 게시글 정보 업데이트 |
| DELETE | `/bbs/{ntt_id}` | 게시글 삭제 | 게시글 삭제 |
| GET | `/bbs/search` | 게시글 검색 | 다양한 조건으로 게시글 검색 |
| GET | `/bbs/popular` | 인기 게시글 조회 | 조회수가 높은 인기 게시글 목록 |
| POST | `/bbs/{ntt_id}/like` | 게시글 좋아요 | 게시글에 좋아요 추가 |
| DELETE | `/bbs/{ntt_id}/like` | 게시글 좋아요 취소 | 게시글 좋아요 취소 |
| GET | `/bbs/statistics` | 게시글 통계 | 게시글 관련 통계 정보 조회 |

### 댓글 관리
**Base URL**: `/comments`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/comments/` | 댓글 목록 조회 | 페이지네이션으로 댓글 목록 조회 |
| POST | `/comments/` | 댓글 생성 | 새로운 댓글 생성 |
| GET | `/comments/{comment_id}` | 댓글 상세 조회 | 특정 댓글의 상세 정보 조회 |
| PUT | `/comments/{comment_id}` | 댓글 수정 | 댓글 정보 업데이트 |
| DELETE | `/comments/{comment_id}` | 댓글 삭제 | 댓글 삭제 |
| GET | `/comments/post/{ntt_id}` | 게시글별 댓글 조회 | 특정 게시글의 댓글 목록 조회 |
| GET | `/comments/statistics` | 댓글 통계 | 댓글 관련 통계 정보 조회 |

---

## 파일 관리 (File Management)

### 파일 그룹 관리
**Base URL**: `/files`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/files/` | 파일 그룹 목록 조회 | 페이지네이션으로 파일 그룹 목록 조회 |
| POST | `/files/` | 파일 그룹 생성 | 새로운 파일 그룹 생성 |
| GET | `/files/{file_sn}` | 파일 그룹 상세 조회 | 특정 파일 그룹의 상세 정보 조회 |
| PUT | `/files/{file_sn}` | 파일 그룹 수정 | 파일 그룹 정보 업데이트 |
| DELETE | `/files/{file_sn}` | 파일 그룹 삭제 | 파일 그룹 삭제 |
| GET | `/files/search` | 파일 그룹 검색 | 파일 그룹 검색 |
| POST | `/files/upload` | 파일 업로드 | 파일 업로드 및 그룹 생성 |
| GET | `/files/statistics` | 파일 통계 | 파일 관련 통계 정보 조회 |
| POST | `/files/validate` | 파일 검증 | 파일 유효성 검증 |

### 파일 상세 관리
**Base URL**: `/file-details`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/file-details/` | 파일 상세 목록 조회 | 페이지네이션으로 파일 상세 목록 조회 |
| POST | `/file-details/` | 파일 상세 생성 | 새로운 파일 상세 정보 생성 |
| GET | `/file-details/{file_detail_sn}` | 파일 상세 조회 | 특정 파일 상세 정보 조회 |
| PUT | `/file-details/{file_detail_sn}` | 파일 상세 수정 | 파일 상세 정보 업데이트 |
| DELETE | `/file-details/{file_detail_sn}` | 파일 상세 삭제 | 파일 상세 정보 삭제 |
| GET | `/file-details/group/{file_sn}` | 그룹별 파일 상세 조회 | 특정 파일 그룹의 파일 상세 목록 조회 |
| GET | `/file-details/{file_detail_sn}/download` | 파일 다운로드 | 파일 다운로드 |
| GET | `/file-details/search` | 파일 상세 검색 | 파일 상세 정보 검색 |
| GET | `/file-details/statistics` | 파일 상세 통계 | 파일 상세 관련 통계 정보 조회 |

---

## 공통 코드 관리 (Common Code Management)

### 공통 그룹 코드 관리
**Base URL**: `/group-codes`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/group-codes/` | 공통 그룹 코드 목록 조회 | 페이지네이션으로 공통 그룹 코드 목록 조회 |
| POST | `/group-codes/` | 공통 그룹 코드 생성 | 새로운 공통 그룹 코드 생성 |
| GET | `/group-codes/{group_code_id}` | 공통 그룹 코드 상세 조회 | 특정 공통 그룹 코드의 상세 정보 조회 |
| PUT | `/group-codes/{group_code_id}` | 공통 그룹 코드 수정 | 공통 그룹 코드 정보 업데이트 |
| DELETE | `/group-codes/{group_code_id}` | 공통 그룹 코드 삭제 | 공통 그룹 코드 삭제 |
| GET | `/group-codes/search` | 공통 그룹 코드 검색 | 그룹코드명으로 공통 그룹 코드 검색 |
| GET | `/group-codes/statistics` | 공통 그룹 코드 통계 | 공통 그룹 코드 관련 통계 정보 조회 |
| GET | `/group-codes/{group_code_id}/codes` | 그룹별 공통 코드 조회 | 특정 그룹의 공통 코드 목록 조회 |

### 공통 코드 관리
**Base URL**: `/codes`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/codes/` | 공통 코드 목록 조회 | 페이지네이션으로 공통 코드 목록 조회 |
| POST | `/codes/` | 공통 코드 생성 | 새로운 공통 코드 생성 |
| GET | `/codes/{code_id}` | 공통 코드 상세 조회 | 특정 공통 코드의 상세 정보 조회 |
| PUT | `/codes/{code_id}` | 공통 코드 수정 | 공통 코드 정보 업데이트 |
| DELETE | `/codes/{code_id}` | 공통 코드 삭제 | 공통 코드 삭제 |
| GET | `/codes/search` | 공통 코드 검색 | 다양한 조건으로 공통 코드 검색 |
| GET | `/codes/group/{group_code_id}` | 그룹별 공통 코드 조회 | 특정 그룹의 공통 코드 목록 조회 |
| PUT | `/codes/order` | 공통 코드 순서 변경 | 공통 코드의 표시 순서 변경 |
| GET | `/codes/statistics` | 공통 코드 통계 | 공통 코드 관련 통계 정보 조회 |

---

## 시스템 관리 (System Management)

**Base URL**: `/system`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| POST | `/system/logs/` | 시스템 로그 생성 | 새로운 시스템 로그 생성 |
| GET | `/system/logs/` | 시스템 로그 목록 조회 | 페이지네이션으로 시스템 로그 목록 조회 |
| GET | `/system/logs/search` | 시스템 로그 검색 | 다양한 조건으로 시스템 로그 검색 |
| GET | `/system/logs/{log_id}` | 시스템 로그 상세 조회 | 특정 시스템 로그의 상세 정보 조회 |
| PUT | `/system/logs/{log_id}` | 시스템 로그 수정 | 시스템 로그 정보 업데이트 |
| DELETE | `/system/logs/{log_id}` | 시스템 로그 삭제 | 시스템 로그 삭제 |
| GET | `/system/logs/statistics` | 시스템 로그 통계 | 시스템 로그 관련 통계 정보 조회 |
| POST | `/system/web-logs/` | 웹 로그 생성 | 새로운 웹 로그 생성 |
| GET | `/system/web-logs/` | 웹 로그 목록 조회 | 페이지네이션으로 웹 로그 목록 조회 |
| GET | `/system/web-logs/search` | 웹 로그 검색 | 다양한 조건으로 웹 로그 검색 |
| GET | `/system/web-logs/{log_id}` | 웹 로그 상세 조회 | 특정 웹 로그의 상세 정보 조회 |
| PUT | `/system/web-logs/{log_id}` | 웹 로그 수정 | 웹 로그 정보 업데이트 |
| DELETE | `/system/web-logs/{log_id}` | 웹 로그 삭제 | 웹 로그 삭제 |
| GET | `/system/web-logs/statistics` | 웹 로그 통계 | 웹 로그 관련 통계 정보 조회 |
| GET | `/system/health` | 시스템 상태 확인 | 시스템 헬스 체크 |
| GET | `/system/dashboard` | 대시보드 요약 | 시스템 대시보드 요약 정보 조회 |

---

## 로그 관리 (Log Management)

**Base URL**: `/logs`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/logs/` | 로그인 로그 목록 조회 | 페이지네이션으로 로그인 로그 목록 조회 |
| POST | `/logs/` | 로그인 로그 생성 | 새로운 로그인 로그 생성 |
| GET | `/logs/{log_id}` | 로그인 로그 상세 조회 | 특정 로그인 로그의 상세 정보 조회 |
| PUT | `/logs/{log_id}` | 로그인 로그 수정 | 로그인 로그 정보 업데이트 |
| DELETE | `/logs/{log_id}` | 로그인 로그 삭제 | 로그인 로그 삭제 |
| GET | `/logs/search` | 로그인 로그 검색 | 다양한 조건으로 로그인 로그 검색 |
| GET | `/logs/statistics` | 로그인 로그 통계 | 로그인 로그 관련 통계 정보 조회 |
| GET | `/logs/security-alerts` | 보안 알림 조회 | 보안 관련 알림 정보 조회 |
| GET | `/logs/suspicious-activity` | 의심스러운 활동 조회 | 의심스러운 로그인 활동 조회 |
| GET | `/logs/session-management` | 세션 관리 조회 | 사용자 세션 관리 정보 조회 |
| GET | `/logs/export` | 로그 내보내기 | 로그 데이터 내보내기 |
| GET | `/logs/analysis` | 로그 분석 | 로그 데이터 분석 결과 조회 |

---

## 권한 메뉴 관리 (Authorization Menu Management)

**Base URL**: `/author-menu`

| Method | Endpoint | Summary | Description |
|--------|----------|---------|-------------|
| GET | `/author-menu/` | 권한 메뉴 목록 조회 | 페이지네이션으로 권한 메뉴 목록 조회 |
| GET | `/author-menu/author/{author_code}` | 권한별 메뉴 조회 | 특정 권한의 메뉴 목록 조회 |
| GET | `/author-menu/menu/{menu_id}` | 메뉴별 권한 조회 | 특정 메뉴의 권한 목록 조회 |
| POST | `/author-menu/` | 권한 메뉴 생성 | 새로운 권한 메뉴 매핑 생성 |
| PUT | `/author-menu/{author_code}/{menu_id}` | 권한 메뉴 수정 | 권한 메뉴 매핑 정보 업데이트 |
| DELETE | `/author-menu/{author_code}/{menu_id}` | 권한 메뉴 삭제 | 권한 메뉴 매핑 삭제 |
| POST | `/author-menu/bulk` | 권한 메뉴 일괄 생성 | 여러 권한 메뉴 매핑을 일괄 생성 |
| DELETE | `/author-menu/bulk` | 권한 메뉴 일괄 삭제 | 여러 권한 메뉴 매핑을 일괄 삭제 |
| GET | `/author-menu/statistics` | 권한 메뉴 통계 | 권한 메뉴 관련 통계 정보 조회 |

---

## 📊 엔드포인트 요약

### 총 엔드포인트 수: **약 150개**

| 카테고리 | 엔드포인트 수 | 주요 기능 |
|----------|---------------|----------|
| 인증 관리 | 2 | 로그인, 토큰 갱신 |
| 사용자 관리 | 8 | CRUD, 검색, 통계 |
| 조직 관리 | 7 | CRUD, 트리 구조, 검색 |
| 우편번호 관리 | 6 | CRUD, 주소 검색 |
| 프로그램 관리 | 7 | CRUD, 검색, 통계 |
| 메뉴 관리 | 15 | CRUD, 트리 구조, 이동/복사, 내보내기/가져오기 |
| 게시판 관리 | 25 | 게시판 마스터, 게시글, 댓글 관리 |
| 파일 관리 | 18 | 파일 그룹, 파일 상세, 업로드/다운로드 |
| 공통 코드 관리 | 17 | 그룹 코드, 공통 코드 관리 |
| 시스템 관리 | 16 | 시스템 로그, 웹 로그, 헬스 체크 |
| 로그 관리 | 12 | 로그인 로그, 보안 알림, 세션 관리 |
| 권한 메뉴 관리 | 9 | 권한-메뉴 매핑, 일괄 처리 |

---

## 🔐 인증 요구사항

### JWT 토큰이 필요한 엔드포인트
- 사용자 생성 및 관리 엔드포인트
- 대부분의 CRUD 작업
- 민감한 정보 조회 엔드포인트

### 공개 엔드포인트 (인증 불필요)
- 로그인 엔드포인트
- 일부 조회 엔드포인트 (설정에 따라)
- 헬스 체크 엔드포인트

---

## 📝 참고사항

1. **페이지네이션**: 대부분의 목록 조회 엔드포인트는 `skip`과 `limit` 파라미터를 지원합니다.
2. **검색 기능**: 각 엔드포인트는 관련 필드를 기반으로 한 검색 기능을 제공합니다.
3. **통계 정보**: 주요 엔드포인트들은 통계 정보 조회 기능을 제공합니다.
4. **파일 처리**: 파일 업로드/다운로드 기능이 포함되어 있습니다.
5. **트리 구조**: 조직과 메뉴는 계층적 트리 구조를 지원합니다.

---

**마지막 업데이트**: 2025년 1월  
**작성자**: SkyBoot Core API 개발팀  
**버전**: 1.0
# 파일 라우터 통합 테스트 시나리오

## 개요
이 문서는 `file_router.py`의 모든 엔드포인트에 대한 통합 테스트 시나리오를 정의합니다.
각 시나리오는 실제 사용자 워크플로우를 기반으로 작성되었으며, 엔드포인트 간의 상호작용을 검증합니다.

## 테스트 환경 설정
- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api/v1/files`
- **인증**: Bearer Token 또는 세션 기반 인증
- **데이터베이스**: 테스트용 격리된 데이터베이스

---

## 시나리오 1: 기본 파일 관리 워크플로우

### 목적
파일의 전체 생명주기(생성 → 조회 → 수정 → 삭제)를 테스트합니다.

### 테스트 단계

| 단계 | 엔드포인트 | HTTP 메서드 | 입력 값 | 예상 출력 | 실제 결과 |
|------|------------|-------------|---------|-----------|----------|
| 1.1 | `/api/v1/files` | POST | `{"atch_file_id": "TEST001", "file_stre_cours": "/uploads/test", "stre_file_nm": "test.txt", "orignl_file_nm": "original.txt", "file_extsn": "txt", "file_cn": "테스트 내용", "file_size": 1024, "frst_register_id": "testuser"}` | 201 Created, 파일 ID 반환 | |
| 1.2 | `/api/v1/files` | GET | 쿼리 파라미터: `page=1&size=10` | 200 OK, 파일 목록 반환 | |
| 1.3 | `/api/v1/files/{file_id}` | GET | 1.1에서 생성된 파일 ID | 200 OK, 파일 상세 정보 | |
| 1.4 | `/api/v1/files/{file_id}` | PUT | `{"orignl_file_nm": "updated.txt", "file_cn": "수정된 내용"}` | 200 OK, 수정된 파일 정보 | |
| 1.5 | `/api/v1/files/{file_id}` | DELETE | 파일 ID | 204 No Content | |
| 1.6 | `/api/v1/files/{file_id}` | GET | 삭제된 파일 ID | 404 Not Found | |

### 성공 기준
- 모든 단계가 예상 HTTP 상태 코드를 반환
- 생성된 파일이 올바른 정보로 저장됨
- 수정 작업이 정확히 반영됨
- 삭제 후 파일에 접근할 수 없음

---

## 시나리오 2: 파일 업로드 및 다운로드 워크플로우

### 목적
파일 업로드, 검증, 다운로드 프로세스를 테스트합니다.

### 테스트 단계

| 단계 | 엔드포인트 | HTTP 메서드 | 입력 값 | 예상 출력 | 실제 결과 |
|------|------------|-------------|---------|-----------|----------|
| 2.1 | `/api/v1/files/upload` | POST | 파일: `test.txt` (1KB), 메타데이터 | 201 Created, 업로드 성공 | |
| 2.2 | `/api/v1/files/validate` | POST | `{"file_path": "/uploads/test.txt", "expected_size": 1024}` | 200 OK, 검증 성공 | |
| 2.3 | `/api/v1/files/{file_id}/download` | GET | 업로드된 파일 ID | 200 OK, 파일 다운로드 | |
| 2.4 | `/api/v1/files/upload` | POST | 파일: `malicious.exe` (실행 파일) | 400 Bad Request, 업로드 거부 | |
| 2.5 | `/api/v1/files/upload` | POST | 파일: `large.txt` (50MB) | 413 Request Entity Too Large | |

### 성공 기준
- 허용된 파일 타입만 업로드 성공
- 파일 크기 제한이 올바르게 적용됨
- 업로드된 파일이 정확히 다운로드됨
- 보안 위험이 있는 파일은 차단됨

---

## 시나리오 3: 파일 통계 및 관리 기능

### 목적
파일 통계 조회 및 관리 기능을 테스트합니다.

### 테스트 단계

| 단계 | 엔드포인트 | HTTP 메서드 | 입력 값 | 예상 출력 | 실제 결과 |
|------|------------|-------------|---------|-----------|----------|
| 3.1 | `/api/v1/files/stats` | GET | 없음 | 200 OK, 전체 파일 통계 | |
| 3.2 | `/api/v1/files/type-stats` | GET | 없음 | 200 OK, 파일 타입별 통계 | |
| 3.3 | `/api/v1/files/{file_id}/details` | GET | 파일 ID | 200 OK, 파일 상세 정보 목록 | |
| 3.4 | `/api/v1/files/cleanup-orphaned` | POST | 없음 | 200 OK, 정리된 파일 수 | |

### 성공 기준
- 통계 정보가 정확히 계산됨
- 파일 타입별 분류가 올바름
- 고아 파일 정리가 안전하게 수행됨

---

## 시나리오 4: 오류 처리 및 보안 테스트

### 목적
다양한 오류 상황과 보안 공격에 대한 방어를 테스트합니다.

### 테스트 단계

| 단계 | 엔드포인트 | HTTP 메서드 | 입력 값 | 예상 출력 | 실제 결과 |
|------|------------|-------------|---------|-----------|----------|
| 4.1 | `/api/v1/files` | POST | `{"atch_file_id": "'; DROP TABLE files; --"}` | 400 Bad Request, SQL 인젝션 차단 | |
| 4.2 | `/api/v1/files` | POST | `{"orignl_file_nm": "<script>alert('xss')</script>"}` | 400/201, XSS 차단 또는 이스케이프 | |
| 4.3 | `/api/v1/files` | POST | `{invalid json}` | 422 Unprocessable Entity | |
| 4.4 | `/api/v1/files` | POST | `{"file_size": -1}` | 422 Unprocessable Entity | |
| 4.5 | `/api/v1/files/99999` | GET | 존재하지 않는 ID | 404 Not Found | |
| 4.6 | `/api/v1/files` | GET | 인증 토큰 없음 | 401 Unauthorized | |

### 성공 기준
- SQL 인젝션 공격이 차단됨
- XSS 공격이 차단되거나 안전하게 처리됨
- 잘못된 입력에 대해 적절한 오류 응답
- 인증이 필요한 엔드포인트에서 권한 검사

---

## 시나리오 5: 성능 및 동시성 테스트

### 목적
높은 부하와 동시 접근 상황에서의 API 성능을 테스트합니다.

### 테스트 단계

| 단계 | 엔드포인트 | HTTP 메서드 | 입력 값 | 예상 출력 | 실제 결과 |
|------|------------|-------------|---------|-----------|----------|
| 5.1 | `/api/v1/files` | GET | 100개 동시 요청 | 200 OK, 응답 시간 < 2초 | |
| 5.2 | `/api/v1/files` | POST | 50개 파일 동시 생성 | 201 Created, 데이터 일관성 유지 | |
| 5.3 | `/api/v1/files/upload` | POST | 10개 파일 동시 업로드 | 201 Created, 파일 무결성 유지 | |
| 5.4 | `/api/v1/files/stats` | GET | 연속 1000회 요청 | 200 OK, 메모리 누수 없음 | |

### 성공 기준
- 동시 요청 처리 시 데이터 일관성 유지
- 응답 시간이 허용 범위 내
- 메모리 누수나 리소스 고갈 없음

---

## 시나리오 6: 엔드투엔드 사용자 시나리오

### 목적
실제 사용자의 전형적인 사용 패턴을 시뮬레이션합니다.

### 테스트 단계

| 단계 | 설명 | 엔드포인트 | 예상 결과 | 실제 결과 |
|------|------|------------|-----------|----------|
| 6.1 | 사용자 로그인 및 파일 목록 조회 | `GET /api/v1/files` | 빈 목록 또는 기존 파일 목록 | |
| 6.2 | 새 문서 파일 업로드 | `POST /api/v1/files/upload` | 업로드 성공, 파일 ID 반환 | |
| 6.3 | 업로드된 파일 정보 확인 | `GET /api/v1/files/{file_id}` | 파일 메타데이터 조회 성공 | |
| 6.4 | 파일 이름 수정 | `PUT /api/v1/files/{file_id}` | 수정 성공 | |
| 6.5 | 파일 다운로드 | `GET /api/v1/files/{file_id}/download` | 원본 파일 다운로드 성공 | |
| 6.6 | 전체 파일 통계 확인 | `GET /api/v1/files/stats` | 통계 정보 조회 성공 | |
| 6.7 | 불필요한 파일 삭제 | `DELETE /api/v1/files/{file_id}` | 삭제 성공 | |
| 6.8 | 삭제 확인 | `GET /api/v1/files/{file_id}` | 404 Not Found | |

### 성공 기준
- 전체 워크플로우가 끊김 없이 진행됨
- 각 단계에서 예상된 결과 획득
- 사용자 경험이 직관적이고 일관됨

---

## 테스트 실행 방법

### 자동화된 테스트 실행
```bash
# 전체 통합 테스트 실행
python -m pytest integration_tests/ -v --tb=short

# 특정 시나리오만 실행
python -m pytest integration_tests/test_scenario_1.py -v

# 성능 테스트 실행
python -m pytest integration_tests/test_performance.py -v --durations=10
```

### 수동 테스트 실행
1. 테스트 환경 설정
2. API 서버 시작
3. 각 시나리오별로 순차 실행
4. 결과 기록 및 분석

---

## 테스트 결과 보고서 템플릿

### 실행 정보
- **테스트 일시**: 
- **테스트 환경**: 
- **API 버전**: 
- **테스터**: 

### 시나리오별 결과

| 시나리오 | 총 단계 수 | 성공 | 실패 | 성공률 | 비고 |
|----------|------------|------|------|--------|------|
| 시나리오 1 | 6 | | | | |
| 시나리오 2 | 5 | | | | |
| 시나리오 3 | 4 | | | | |
| 시나리오 4 | 6 | | | | |
| 시나리오 5 | 4 | | | | |
| 시나리오 6 | 8 | | | | |
| **전체** | **33** | | | | |

### 발견된 이슈

| 이슈 번호 | 시나리오 | 단계 | 설명 | 심각도 | 상태 |
|-----------|----------|------|------|--------|------|
| | | | | | |

### 권장사항

1. **성능 개선**:
   - 

2. **보안 강화**:
   - 

3. **사용성 개선**:
   - 

### 결론

전체적인 API 품질 평가:
- **기능성**: 
- **안정성**: 
- **성능**: 
- **보안**: 
- **사용성**: 

---

## 부록

### A. 테스트 데이터 세트
```json
{
  "valid_file": {
    "atch_file_id": "TEST001",
    "file_stre_cours": "/uploads/test",
    "stre_file_nm": "test_file.txt",
    "orignl_file_nm": "original_test.txt",
    "file_extsn": "txt",
    "file_cn": "테스트 파일 내용",
    "file_size": 1024,
    "frst_register_id": "testuser"
  },
  "invalid_file": {
    "atch_file_id": "",
    "file_size": -1
  },
  "malicious_data": {
    "sql_injection": "'; DROP TABLE files; --",
    "xss_payload": "<script>alert('xss')</script>"
  }
}
```

### B. 환경 설정 체크리스트
- [ ] 테스트 데이터베이스 준비
- [ ] API 서버 실행
- [ ] 인증 토큰 준비
- [ ] 테스트 파일 준비
- [ ] 로그 수집 설정
- [ ] 모니터링 도구 설정

### C. 문제 해결 가이드

**일반적인 오류와 해결방법**:

1. **401 Unauthorized**
   - 인증 토큰 확인
   - 토큰 만료 여부 확인

2. **404 Not Found**
   - 엔드포인트 URL 확인
   - 리소스 존재 여부 확인

3. **500 Internal Server Error**
   - 서버 로그 확인
   - 데이터베이스 연결 상태 확인

4. **테스트 타임아웃**
   - 네트워크 연결 확인
   - 서버 성능 상태 확인
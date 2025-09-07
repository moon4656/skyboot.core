# SkyBoot Core API

> **현대적인 FastAPI 기반 백엔드 프레임워크:** PostgreSQL + SQLAlchemy 2.0 + Pydantic v2 + JWT 인증 + 구조화된 로깅 시스템을 갖춘 확장 가능한 API 서버

---

## 📋 프로젝트 개요

* **목표:** 사용자 관리, 인증/인가, 게시판, 파일 관리 등을 포함한 종합적인 백엔드 API 서버
* **인증 시스템:** JWT 기반 Access Token + 사용자 권한 관리
* **데이터베이스:** PostgreSQL with SQLAlchemy 2.0 ORM
* **API 설계:** RESTful API with OpenAPI/Swagger 문서화
* **로깅 시스템:** 구조화된 로깅 with 자동 로테이션 (10MB 단위, 매일)
* **코드 품질:** Type hints, Pydantic v2 validation, 모듈화된 구조

---

## 🛠️ 기술 스택

### 백엔드 프레임워크
* **Python 3.11+** - 최신 Python 기능 활용
* **FastAPI** - 고성능 비동기 웹 프레임워크
* **Uvicorn** - ASGI 서버

### 데이터베이스 & ORM
* **PostgreSQL 14+** - 메인 데이터베이스
* **SQLAlchemy 2.0** - 현대적인 ORM
* **Alembic** - 데이터베이스 마이그레이션

### 인증 & 보안
* **PyJWT** - JWT 토큰 처리
* **passlib + bcrypt** - 비밀번호 해싱
* **python-multipart** - 파일 업로드 지원

### 검증 & 직렬화
* **Pydantic v2** - 데이터 검증 및 직렬화

### 로깅 & 모니터링
* **Python logging** - 구조화된 로깅
* **RotatingFileHandler** - 로그 파일 로테이션

### 개발 도구
* **pytest** - 테스트 프레임워크
* **httpx** - HTTP 클라이언트 (테스트용)

---

## 🏗️ 시스템 아키텍처

```
[Client] ──HTTP──> [FastAPI Server]
                     │
                     ├─ SQLAlchemy ORM → PostgreSQL (메인 데이터)
                     ├─ File System (업로드 파일 저장)
                     ├─ Logging System (구조화된 로그)
                     └─ JWT Authentication (토큰 기반 인증)
```

### 주요 컴포넌트
- **API Layer**: FastAPI 라우터 기반 RESTful API
- **Service Layer**: 비즈니스 로직 처리
- **Repository Layer**: 데이터 접근 계층
- **Model Layer**: SQLAlchemy 모델 정의
- **Schema Layer**: Pydantic 모델 (요청/응답 검증)
- **Middleware**: 로깅, CORS, 인증 처리

---

## ⚡ 주요 기능

### 🔐 인증 & 사용자 관리
- **JWT 기반 인증**: 로그인/로그아웃, 토큰 검증
- **사용자 관리**: CRUD 작업, 프로필 관리
- **권한 시스템**: 역할 기반 접근 제어

### 📋 게시판 시스템
- **게시판 관리**: 다중 게시판 지원
- **게시글 관리**: 작성, 수정, 삭제, 조회
- **댓글 시스템**: 게시글별 댓글 관리
- **첨부파일**: 파일 업로드 및 다운로드

### 🗂️ 메뉴 & 시스템 관리
- **메뉴 관리**: 계층형 메뉴 구조
- **코드 관리**: 시스템 공통 코드
- **로그 관리**: API 요청/응답 로깅

### 📁 파일 관리
- **파일 업로드**: 다중 파일 업로드 지원
- **파일 다운로드**: 안전한 파일 다운로드
- **파일 정보**: 메타데이터 관리

### 🔧 시스템 기능
- **헬스 체크**: 서버 상태 모니터링
- **API 문서**: Swagger/OpenAPI 자동 생성
- **로깅 시스템**: 구조화된 로그 with 자동 로테이션

---

## 📁 프로젝트 구조

```
skyboot.core/
├── backend/                    # 백엔드 애플리케이션
│   ├── app/
│   │   ├── api/               # API 라우터
│   │   │   └── routes/        # 개별 라우터 파일들
│   │   │       ├── auth_router.py
│   │   │       ├── user_router.py
│   │   │       ├── board_router.py
│   │   │       ├── file_router.py
│   │   │       ├── menu_router.py
│   │   │       ├── log_router.py
│   │   │       └── system_router.py
│   │   ├── database/          # 데이터베이스 관련
│   │   │   ├── connection.py
│   │   │   └── session.py
│   │   ├── middleware/        # 미들웨어
│   │   │   ├── cors.py
│   │   │   └── logging.py
│   │   ├── models/           # SQLAlchemy 모델
│   │   │   ├── user.py
│   │   │   ├── board.py
│   │   │   ├── menu.py
│   │   │   └── ...
│   │   ├── routers/          # 통합 라우터
│   │   │   └── __init__.py
│   │   ├── schemas/          # Pydantic 스키마
│   │   │   ├── user.py
│   │   │   ├── board.py
│   │   │   └── ...
│   │   ├── services/         # 비즈니스 로직
│   │   │   ├── auth_service.py
│   │   │   ├── user_service.py
│   │   │   └── ...
│   │   └── utils/           # 유틸리티 함수
│   │       ├── auth.py
│   │       ├── logging.py
│   │       └── ...
│   ├── logs/                # 로그 파일
│   │   └── api_requests.log
│   ├── uploads/             # 업로드된 파일
│   ├── migrations/          # Alembic 마이그레이션
│   ├── main.py             # 애플리케이션 진입점
│   ├── requirements.txt    # Python 의존성
│   └── .env               # 환경 변수
├── frontend/              # 프론트엔드 (향후 확장)
└── README.md             # 프로젝트 문서
```

---

## ⚙️ 환경 설정

### 환경 변수 (.env)

| 변수명 | 예시 값 | 설명 |
|--------|---------|------|
| `DATABASE_URL` | `postgresql://user:password@localhost:5432/skyboot` | PostgreSQL 데이터베이스 연결 URL |
| `SECRET_KEY` | `your-secret-key-here` | JWT 토큰 서명용 비밀키 (32자 이상 권장) |
| `ALGORITHM` | `HS256` | JWT 토큰 알고리즘 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access Token 만료 시간 (분) |
| `UPLOAD_DIR` | `./uploads` | 파일 업로드 디렉토리 |
| `LOG_LEVEL` | `INFO` | 로깅 레벨 (DEBUG, INFO, WARNING, ERROR) |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | CORS 허용 오리진 (쉼표로 구분) |

### .env 파일 예시

```env
# 데이터베이스 설정
DATABASE_URL=postgresql://skyboot:password@localhost:5432/skyboot_db

# JWT 설정
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 파일 업로드 설정
UPLOAD_DIR=./uploads

# 로깅 설정
LOG_LEVEL=INFO

# CORS 설정
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 🚀 설치 및 실행

### 사전 요구사항
- Python 3.11 이상
- PostgreSQL 14 이상
- Git

### 로컬 개발 환경 설정

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd skyboot.core/backend  

# 2. 가상환경 생성 및 활성화
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
python.exe -m pip install --upgrade pip
cd backend
pip install -r requirements.txt

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 데이터베이스 URL 및 기타 설정 입력

# 5. 데이터베이스 설정
# PostgreSQL에서 데이터베이스 생성
createdb skyboot_db

# 데이터베이스 마이그레이션 실행
alembic upgrade head

# 6. 서버 실행
python main.py
```

### 서버 접속
- **API 서버**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **헬스 체크**: http://localhost:8000/health

---

## 7) 데이터 모델 (핵심)

### 사용자/권한

* **User(id, username, email, password\_hash, is\_active, last\_login\_at)**
* **Role(id, name, description)**
* **Permission(id, code, description)**  → 예: `users.read`, `users.write`, `boards.post.create`
* **UserRole(user\_id, role\_id)** (N\:M)
* **RolePermission(role\_id, permission\_id)** (N\:M)

### 메뉴/프로그램

* **Program(id, code, name, path, method, is\_protected)**
* **Menu(id, parent\_id, name, path, sort, is\_visible, required\_permission\_code?)**

### 게시판

* **Board(id, key, name, description, is\_public)**
* **Post(id, board\_id, author\_id, title, content, pinned, created\_at, updated\_at)**
* **Comment(id, post\_id, author\_id, content, created\_at, updated\_at)**
* **Attachment(id, post\_id, filename, url, size, mime)**

### 보안/로깅

* **TokenBlacklist(jti, exp)**  ← 로그아웃 처리용
* **AuditLog(id, user\_id, action, resource, resource\_id, ip, ua, created\_at)**

> **의견:** Permission은 문자열 코드(`module.action`)가 유지보수상 가장 실용적입니다. DB 조인 비용보다 운영 효율이 훨씬 큽니다.

---

## 8) RBAC 적용 방식

* **엔드포인트 단위**로 `@router.get(..., dependencies=[Depends(require("users.read"))])`
* `require(permission_code)`는 내부에서:

  1. JWT 검증 → user\_id 추출
  2. 캐시된 권한 세트 조회 (없으면 DB → Redis 300초 캐시)
  3. 포함 여부 검사 → 미포함시 403

---

## 9) 인증/로그아웃 (JWT + 블랙리스트)

### 로그인

* **POST** `/auth/login`

```json
{ "username": "admin", "password": "pass" }
```

* 성공 시:

```json
{ "access_token": "<JWT>", "token_type": "bearer", "expires_in": 900 }
```

* JWT 클레임: `sub=user_id`, `jti`, `exp`, `iat`, `roles=[...]`

### 인증 미들웨어

* `Authorization: Bearer <token>`
* 처리: **서명 검증** → **exp 확인** → **Redis 블랙리스트(jti) 조회** → OK

### 로그아웃

* **POST** `/auth/logout` (헤더로 현재 토큰 전달)

  * 서버가 **해당 토큰의 `jti`를 Redis에 저장** (TTL=남은 만료시간)
  * 이후 같은 토큰은 즉시 거부

> **강한 의견:** “Access만 쓰고 클라이언트가 토큰 버린다”로는 **진짜 로그아웃이 아닙니다**. 블랙리스트 필수.

---

## 📡 API 엔드포인트

> **Base URL:** `/api/v1`

### 🔐 인증 (Authentication)
- `POST /api/v1/auth/login` - 사용자 로그인
- `POST /api/v1/auth/logout` - 사용자 로그아웃
- `GET /api/v1/auth/me` - 현재 사용자 정보 조회
- `POST /api/v1/auth/refresh` - 토큰 갱신

### 👥 사용자 관리 (Users)
- `GET /api/v1/auth/users` - 사용자 목록 조회
- `POST /api/v1/auth/users` - 새 사용자 생성
- `GET /api/v1/auth/users/{user_id}` - 특정 사용자 조회
- `PUT /api/v1/auth/users/{user_id}` - 사용자 정보 수정
- `DELETE /api/v1/auth/users/{user_id}` - 사용자 삭제

### 📋 게시판 (Boards)
- `GET /api/v1/boards` - 게시판 목록 조회
- `POST /api/v1/boards` - 새 게시판 생성
- `GET /api/v1/boards/{board_id}` - 특정 게시판 조회
- `PUT /api/v1/boards/{board_id}` - 게시판 정보 수정
- `DELETE /api/v1/boards/{board_id}` - 게시판 삭제

### 📝 게시글 (Posts)
- `GET /api/v1/boards/{board_id}/posts` - 게시글 목록 조회
- `POST /api/v1/boards/{board_id}/posts` - 새 게시글 작성
- `GET /api/v1/posts/{post_id}` - 특정 게시글 조회
- `PUT /api/v1/posts/{post_id}` - 게시글 수정
- `DELETE /api/v1/posts/{post_id}` - 게시글 삭제

### 💬 댓글 (Comments)
- `GET /api/v1/posts/{post_id}/comments` - 댓글 목록 조회
- `POST /api/v1/posts/{post_id}/comments` - 새 댓글 작성
- `PUT /api/v1/comments/{comment_id}` - 댓글 수정
- `DELETE /api/v1/comments/{comment_id}` - 댓글 삭제

### 📁 파일 관리 (Files)
- `POST /api/v1/files/upload` - 파일 업로드
- `GET /api/v1/files/{file_id}` - 파일 다운로드
- `GET /api/v1/files` - 파일 목록 조회
- `DELETE /api/v1/files/{file_id}` - 파일 삭제

### 🗂️ 메뉴 관리 (Menus)
- `GET /api/v1/menus` - 메뉴 목록 조회
- `POST /api/v1/menus` - 새 메뉴 생성
- `PUT /api/v1/menus/{menu_id}` - 메뉴 수정
- `DELETE /api/v1/menus/{menu_id}` - 메뉴 삭제

### 🔧 시스템 (System)
- `GET /health` - 헬스 체크
- `GET /api/v1/system/info` - 시스템 정보
- `GET /api/v1/logs` - 로그 조회

---

## 💡 API 사용 예시

### 로그인 및 인증

```bash
# 1. 사용자 로그인
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "password123"
  }'

# 응답 예시
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}

# 2. 인증이 필요한 API 호출
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
curl -X GET http://localhost:8000/api/v1/auth/users \
  -H "Authorization: Bearer $TOKEN"

# 3. 로그아웃
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔧 개발 가이드

### 데이터베이스 마이그레이션

```bash
# 새 마이그레이션 생성
alembic revision --autogenerate -m "migration description"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1

# 마이그레이션 히스토리 확인
alembic history
```

### 로깅 시스템

- **로그 파일 위치**: `backend/logs/api_requests.log`
- **로그 로테이션**: 10MB 단위, 매일 자동 로테이션
- **로그 레벨**: DEBUG, INFO, WARNING, ERROR
- **구조화된 로깅**: JSON 형태로 요청/응답 정보 기록

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_auth.py

# 커버리지 포함 테스트
pytest --cov=app

# 상세 출력
pytest -v
```

---

## 🔒 보안 고려사항

### 인증 및 권한
- **JWT 토큰**: 안전한 비밀키 사용 및 적절한 만료 시간 설정
- **비밀번호 해싱**: bcrypt를 사용한 안전한 비밀번호 저장
- **권한 기반 접근 제어**: 사용자 역할에 따른 API 접근 제한

### 데이터 보호
- **CORS 설정**: 허용된 오리진만 접근 가능
- **입력 검증**: Pydantic을 통한 엄격한 데이터 검증
- **SQL 인젝션 방지**: SQLAlchemy ORM 사용
- **파일 업로드**: 안전한 파일 타입 및 크기 제한

### 로깅 및 모니터링
- **API 요청 로깅**: 모든 API 요청/응답 기록
- **에러 추적**: 상세한 에러 로그 및 스택 트레이스
- **보안 이벤트**: 로그인 실패, 권한 없는 접근 시도 기록

---

## 📈 성능 최적화

### 데이터베이스 최적화
- **인덱싱**: 자주 조회되는 컬럼에 인덱스 적용
- **쿼리 최적화**: N+1 문제 방지, 적절한 JOIN 사용
- **페이지네이션**: 대용량 데이터 조회 시 페이징 처리

### API 성능
- **비동기 처리**: FastAPI의 async/await 활용
- **캐싱**: 자주 조회되는 데이터 캐싱
- **압축**: gzip 압축을 통한 응답 크기 최적화

### 리소스 관리
- **로그 관리**: 자동 로테이션으로 디스크 공간 관리
- **파일 정리**: 임시 파일 및 오래된 업로드 파일 정리
- **메모리 최적화**: 적절한 연결 풀 크기 설정

---

## 🤝 기여 가이드

### 개발 워크플로우
1. **이슈 생성**: 새 기능이나 버그 리포트
2. **브랜치 생성**: `feature/기능명` 또는 `bugfix/버그명`
3. **코드 작성**: 기능 구현 및 테스트 코드 작성
4. **테스트**: 모든 테스트 통과 확인
5. **커밋**: 명확하고 간결한 커밋 메시지
6. **Pull Request**: 코드 리뷰 요청

### 코딩 스타일
- **PEP 8**: Python 코딩 스타일 가이드 준수
- **Type Hints**: 모든 함수에 타입 힌트 추가
- **Docstring**: 클래스와 함수에 명확한 문서화
- **테스트**: 새 기능에 대한 테스트 코드 필수

---

## 📞 지원 및 문의

### 문제 해결
- **API 문서**: http://localhost:8000/docs 에서 상세 API 문서 확인
- **로그 확인**: `backend/logs/` 디렉토리에서 로그 파일 확인
- **헬스 체크**: http://localhost:8000/health 에서 서버 상태 확인

### 개발 지원
- **이슈 트래킹**: GitHub Issues를 통한 버그 리포트 및 기능 요청
- **문서화**: 코드 내 주석 및 README 문서 참조
- **커뮤니티**: 개발자 커뮤니티를 통한 질문 및 답변

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.

---

## 🎯 로드맵

### 단기 목표 (1-3개월)
- [ ] 사용자 권한 시스템 고도화
- [ ] 파일 업로드 최적화
- [ ] API 성능 모니터링 도구 추가

### 중기 목표 (3-6개월)
- [ ] 실시간 알림 시스템
- [ ] 고급 검색 기능
- [ ] 모바일 API 최적화

### 장기 목표 (6개월+)
- [ ] 마이크로서비스 아키텍처 전환
- [ ] AI 기반 콘텐츠 추천
- [ ] 다국어 지원

## GITHUB   

- git init
- git status
- git remote -v
- git config --list

# git 사용자정보 설정
# 전역 설정 (모든 저장소에 적용)
- git config --global user.name "사용자명"
- git config --global user.email "이메일@example.com"

# 로컬 설정 (현재 저장소에만 적용)
- git config user.name "사용자명"
- git config user.email "이메일@example.com"

# 프로젝트 루트 디렉토리에서
- git init
- git add .
- git commit -m "Initial commit: STT project with FastAPI, Vue3, PostgreSQL"
- git branch -M main
- git remote add origin https://github.com/moon4656/stt_service.git
- git push -u origin main

- git remote add origin 
- git push -u origin main

- git init
- git add README.md
- git commit -m "first commit"
- git branch -M main
- git remote add origin https://github.com/moon4656/skyboot.core.git
- git push -u origin main

# 향후 변경사항 푸시:
- git add .
- git commit -m "커밋 메시지"
- git push

# 브랜치 확인:
- git branch
- git branch -a

# 브랜치 생성:
- git branch <브랜치명>

# 브랜치 변경:
- git checkout <브랜치명>

# 브랜치 병합:
- git checkout <병합할 브랜치>
- git merge <병합할 브랜치>
- git branch -d <병합된 브랜치>

# 원격 브랜치 삭제:
- git branch -r -d origin/<브랜치명>
- git push origin --delete <브랜치명>

# 서버 8001 포트 확인
- netstat -an | findstr :8001

# 서버 8001 포트 종료
- taskkill /f /pid <PID>

# uvicorn 서버 실행
- uvicorn app:app --host 0.0.0.0 --port 8001 --reload

# 1단계: Git 상태 확인
- git status

# 2단계: 변경 사항 확인
- git diff

# 3단계: 변경 사항 스테이징
- git add .

# 4단계: 커밋
- git commit -m "Add new feature"

# 5단계: 원격 저장소에 푸시
- git push origin main

# Personal Access Token 사용 
- git remote set-url origin https://[moonsoo-dx]:[TOKEN]@github.com/moonsoo-dx/stt_service.git

# GitHub에서 Personal Access Token 생성
# Settings → Developer settings → Personal access tokens → Generate new token
# repo 권한 체크 후 토큰 생성

# push 시 사용자명: GitHub 사용자명, 비밀번호: 생성한 토큰

# Windows Credential Manager 사용
- git config --global credential.helper manager-core

# 또는 토큰을 URL에 직접 포함
- git remote set-url origin https://[토큰]@github.com/moon4656/skyboot.core.git
---

**SkyBoot Core API** - 현대적이고 확장 가능한 FastAPI 백엔드 프레임워크  
**버전**: 1.0.0 | **최종 업데이트**: 2024년 1월

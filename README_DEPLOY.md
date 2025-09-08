# SkyBoot Core API 배포 가이드

이 문서는 SkyBoot Core API 프로젝트를 프로덕션 환경에 배포하는 방법을 설명합니다.

## 📋 목차

1. [사전 요구사항](#사전-요구사항)
2. [환경 설정](#환경-설정)
3. [Docker를 이용한 배포](#docker를-이용한-배포)
4. [수동 배포](#수동-배포)
5. [배포 후 확인](#배포-후-확인)
6. [모니터링 및 로그](#모니터링-및-로그)
7. [트러블슈팅](#트러블슈팅)
8. [보안 체크리스트](#보안-체크리스트)

---

## 🔧 사전 요구사항

### 시스템 요구사항
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Windows Server 2019+
- **CPU**: 최소 2 Core (권장 4 Core)
- **RAM**: 최소 4GB (권장 8GB)
- **Storage**: 최소 20GB (권장 50GB)
- **Network**: 인터넷 연결 필수

### 필수 소프트웨어
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Python**: 3.12+ (수동 배포 시)
- **PostgreSQL**: 14+ (외부 DB 사용 시)
- **Nginx**: 1.20+ (리버스 프록시 사용 시)

---

## ⚙️ 환경 설정

### 1. 환경 변수 설정

프로덕션 환경 변수 파일을 생성합니다:

```bash
# .env.production 파일 복사
cp .env.production.example .env.production
```

`.env.production` 파일을 편집하여 실제 값으로 설정:

```env
# 환경 설정
ENVIRONMENT=production
DEBUG=false

# 서버 설정
HOST=0.0.0.0
PORT=8000
WORKERS=4

# 데이터베이스 설정 (실제 값으로 변경)
DATABASE_URL=postgresql://username:password@localhost:5432/skyboot_prod
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# JWT 설정 (강력한 시크릿 키로 변경)
JWT_SECRET_KEY=your-super-secret-jwt-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# API 키 (강력한 키로 변경)
API_KEY=your-super-secret-api-key-here

# 보안 설정
SECURE_HEADERS=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
MAX_REQUEST_SIZE=10485760

# 정적 파일 설정
STATIC_FILES_ENABLED=true
UPLOADS_DIR=/app/uploads
STATIC_DIR=/app/static
ALLOWED_EXTENSIONS=jpg,jpeg,png,gif,pdf,txt,docx
MAX_FILE_SIZE=10485760

# 로그 설정
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_ROTATION=true
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
```

### 2. SSL 인증서 준비

HTTPS를 위한 SSL 인증서를 준비합니다:

```bash
# Let's Encrypt 사용 예시
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 인증서 파일 위치 확인
ls /etc/letsencrypt/live/your-domain.com/
```

---

## 🐳 Docker를 이용한 배포

### 1. 프로덕션 이미지 빌드

```bash
# 프로덕션 이미지 빌드
docker build -f Dockerfile.prod -t skyboot-core:latest .

# 이미지 확인
docker images | grep skyboot-core
```

### 2. Docker Compose로 배포

```bash
# 프로덕션 환경으로 서비스 시작
docker-compose -f docker-compose.prod.yml up -d

# 서비스 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f api
```

### 3. 데이터베이스 마이그레이션

```bash
# 컨테이너 내에서 마이그레이션 실행
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# 초기 데이터 생성 (필요한 경우)
docker-compose -f docker-compose.prod.yml exec api python scripts/init_data.py
```

### 4. Nginx 설정 (선택사항)

```bash
# Nginx 설정 파일 복사
sudo cp nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp nginx/conf.d/default.conf /etc/nginx/conf.d/

# SSL 인증서 경로 수정
sudo nano /etc/nginx/conf.d/default.conf

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl enable nginx
```

---

## 🔧 수동 배포

### 1. Python 환경 설정

```bash
# Python 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r backend/requirements-prod.txt
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 설치 (Ubuntu)
sudo apt update
sudo apt install postgresql postgresql-contrib

# 데이터베이스 및 사용자 생성
sudo -u postgres psql
CREATE DATABASE skyboot_prod;
CREATE USER skyboot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE skyboot_prod TO skyboot_user;
\q
```

### 3. 애플리케이션 실행

```bash
# 환경 변수 로드
export $(cat .env.production | xargs)

# 데이터베이스 마이그레이션
cd backend
alembic upgrade head

# 애플리케이션 실행
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 4. 시스템 서비스 등록

```bash
# systemd 서비스 파일 생성
sudo nano /etc/systemd/system/skyboot-core.service
```

서비스 파일 내용:

```ini
[Unit]
Description=SkyBoot Core API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/skyboot.core/backend
Environment=PATH=/path/to/skyboot.core/venv/bin
EnvironmentFile=/path/to/skyboot.core/.env.production
ExecStart=/path/to/skyboot.core/venv/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# 서비스 활성화 및 시작
sudo systemctl daemon-reload
sudo systemctl enable skyboot-core
sudo systemctl start skyboot-core
sudo systemctl status skyboot-core
```

---

## ✅ 배포 후 확인

### 1. 헬스체크

```bash
# API 서버 상태 확인
curl http://localhost:8000/health

# 응답 예시
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### 2. API 문서 확인

브라우저에서 다음 URL에 접속:
- Swagger UI: `https://your-domain.com/docs`
- ReDoc: `https://your-domain.com/redoc`

### 3. 기본 기능 테스트

```bash
# 사용자 등록 테스트
curl -X POST "https://your-domain.com/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
  }'

# 로그인 테스트
curl -X POST "https://your-domain.com/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpassword123"
  }'
```

---

## 📊 모니터링 및 로그

### 1. 로그 확인

```bash
# Docker 환경
docker-compose -f docker-compose.prod.yml logs -f api

# 수동 배포 환경
sudo journalctl -u skyboot-core -f

# 애플리케이션 로그 파일
tail -f backend/logs/app.log
tail -f backend/logs/error.log
tail -f backend/logs/security.log
```

### 2. 시스템 모니터링

```bash
# 시스템 리소스 확인
htop
df -h
free -h

# Docker 컨테이너 리소스 확인
docker stats

# 네트워크 연결 확인
netstat -tulpn | grep :8000
```

### 3. 데이터베이스 모니터링

```bash
# PostgreSQL 연결 확인
psql -h localhost -U skyboot_user -d skyboot_prod -c "SELECT version();"

# 활성 연결 수 확인
psql -h localhost -U skyboot_user -d skyboot_prod -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. 서버가 시작되지 않는 경우

```bash
# 포트 사용 확인
sudo netstat -tulpn | grep :8000

# 프로세스 종료
sudo kill -9 $(sudo lsof -t -i:8000)

# 환경 변수 확인
env | grep -E "DATABASE_URL|JWT_SECRET_KEY|API_KEY"
```

#### 2. 데이터베이스 연결 오류

```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 데이터베이스 연결 테스트
psql -h localhost -U skyboot_user -d skyboot_prod

# 방화벽 확인
sudo ufw status
```

#### 3. 메모리 부족 오류

```bash
# 메모리 사용량 확인
free -h

# 스왑 파일 생성 (필요한 경우)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. SSL 인증서 문제

```bash
# 인증서 유효성 확인
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# 인증서 갱신
sudo certbot renew
```

### 로그 분석

```bash
# 에러 로그 필터링
grep -i error backend/logs/app.log

# 특정 시간대 로그 확인
grep "2024-01-15 10:" backend/logs/app.log

# API 요청 통계
grep "POST\|GET\|PUT\|DELETE" backend/logs/app.log | wc -l
```

---

## 🔒 보안 체크리스트

### 배포 전 확인사항

- [ ] **환경 변수**: 모든 시크릿 키가 강력하게 설정됨
- [ ] **데이터베이스**: 기본 패스워드 변경됨
- [ ] **방화벽**: 필요한 포트만 열림 (80, 443, 22)
- [ ] **SSL**: HTTPS 인증서 설정됨
- [ ] **사용자 권한**: 애플리케이션이 root 권한으로 실행되지 않음
- [ ] **로그**: 민감한 정보가 로그에 기록되지 않음
- [ ] **백업**: 데이터베이스 백업 계획 수립됨
- [ ] **모니터링**: 시스템 모니터링 도구 설정됨

### 정기 보안 점검

```bash
# 시스템 업데이트
sudo apt update && sudo apt upgrade

# 보안 패치 확인
sudo apt list --upgradable

# 불필요한 서비스 확인
sudo systemctl list-unit-files --state=enabled

# 로그인 시도 확인
sudo grep "Failed password" /var/log/auth.log
```

---

## 📚 추가 리소스

### 유용한 명령어

```bash
# 전체 시스템 상태 확인
sudo systemctl status

# 디스크 사용량 확인
du -sh /path/to/skyboot.core/*

# 네트워크 연결 확인
ss -tulpn

# 프로세스 트리 확인
pstree -p
```

### 성능 최적화

```bash
# Gunicorn 워커 수 조정 (CPU 코어 수 * 2 + 1)
gunicorn main:app --workers 9 --worker-class uvicorn.workers.UvicornWorker

# 데이터베이스 연결 풀 최적화
# .env.production에서 DATABASE_POOL_SIZE 조정

# Nginx 캐싱 설정
# nginx/conf.d/default.conf에서 캐시 설정 활성화
```

### 백업 및 복구

```bash
# 데이터베이스 백업
pg_dump -h localhost -U skyboot_user skyboot_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 데이터베이스 복구
psql -h localhost -U skyboot_user skyboot_prod < backup_20240115_103000.sql

# 파일 백업
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz backend/uploads/
```

---

## 📞 지원 및 문의

배포 과정에서 문제가 발생하거나 추가 지원이 필요한 경우:

- **이슈 트래커**: GitHub Issues
- **문서**: 프로젝트 README.md
- **로그 분석**: `backend/logs/` 디렉토리 확인

---

**⚠️ 주의사항**

1. 프로덕션 배포 전에 반드시 스테이징 환경에서 테스트하세요.
2. 데이터베이스 마이그레이션 전에 백업을 생성하세요.
3. 보안 설정을 정기적으로 검토하고 업데이트하세요.
4. 시스템 리소스를 지속적으로 모니터링하세요.

---

*이 문서는 SkyBoot Core API v1.0.0 기준으로 작성되었습니다.*
*최신 정보는 프로젝트 저장소를 확인하세요.*
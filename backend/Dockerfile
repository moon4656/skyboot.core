# SkyBoot Core API - Production Dockerfile
# Python 3.12 기반 프로덕션 환경 컨테이너

# 베이스 이미지: Python 3.12 slim 버전 사용
FROM python:3.12-slim

# 메타데이터 설정
LABEL maintainer="SkyBoot Core Team"
LABEL version="1.0.0"
LABEL description="SkyBoot Core API Production Container"

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 시스템 패키지 업데이트 및 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 사용자 생성 (보안 강화)
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 필요한 디렉토리 생성
RUN mkdir -p /app/logs /app/uploads /app/certs && \
    chown -R appuser:appuser /app

# Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 파일 권한 설정
RUN chown -R appuser:appuser /app

# 비특권 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 실행
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
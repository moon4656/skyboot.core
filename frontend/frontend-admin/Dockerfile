# SkyBoot Core Admin Frontend - Production Dockerfile
# Vue 3 + Vuestic UI 기반 관리자 프론트엔드

# 빌드 스테이지
FROM node:22-alpine AS builder

# 메타데이터 설정
LABEL maintainer="SkyBoot Core Team"
LABEL version="1.0.0"
LABEL description="SkyBoot Core Admin Frontend Production Container"

# 작업 디렉토리 설정
WORKDIR /app

# pnpm 설치 및 패키지 파일 복사
RUN npm install -g pnpm
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --prod=false

# 소스 코드 복사
COPY . .

# 프로덕션 빌드
RUN pnpm run build

# 프로덕션 스테이지
FROM nginx:alpine AS production

# 메타데이터 설정
LABEL maintainer="SkyBoot Core Team"
LABEL version="1.0.0"
LABEL description="SkyBoot Core Admin Frontend Production Server"

# 빌드된 파일 복사
COPY --from=builder /app/dist /usr/share/nginx/html/admin

# Nginx 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 포트 노출
EXPOSE 80

# 헬스체크 설정
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/admin/health || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
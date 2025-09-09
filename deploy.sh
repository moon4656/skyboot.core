#!/bin/bash

# SkyBoot Core - 프로덕션 배포 스크립트
# Vue 3 + Vuestic UI Admin Frontend + FastAPI Backend 배포

set -e

echo "🚀 SkyBoot Core 프로덕션 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
print_step() {
    echo -e "${BLUE}📋 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 환경 변수 확인
check_env() {
    print_step "환경 변수 확인 중..."
    
    if [ ! -f ".env.production" ]; then
        print_error ".env.production 파일이 없습니다."
        print_warning "cp .env.production.example .env.production 명령으로 생성하고 설정을 수정하세요."
        exit 1
    fi
    
    if [ ! -f "frontend/frontend-admin/.env.production" ]; then
        print_error "frontend/frontend-admin/.env.production 파일이 없습니다."
        exit 1
    fi
    
    print_success "환경 변수 파일 확인 완료"
}

# Docker 및 Docker Compose 확인
check_docker() {
    print_step "Docker 환경 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker 데몬이 실행되지 않았습니다."
        exit 1
    fi
    
    print_success "Docker 환경 확인 완료"
}

# 기존 컨테이너 정리
cleanup_containers() {
    print_step "기존 컨테이너 정리 중..."
    
    docker-compose down --remove-orphans || true
    docker system prune -f || true
    
    print_success "컨테이너 정리 완료"
}

# 프론트엔드 빌드
build_frontend() {
    print_step "Frontend Admin 빌드 중..."
    
    cd frontend/frontend-admin
    
    # Node.js 의존성 설치
    if [ -f "package-lock.json" ]; then
        npm ci
    else
        npm install
    fi
    
    # 프로덕션 빌드
    npm run build
    
    cd ../..
    
    print_success "Frontend Admin 빌드 완료"
}

# Docker 이미지 빌드
build_images() {
    print_step "Docker 이미지 빌드 중..."
    
    docker-compose build --no-cache
    
    print_success "Docker 이미지 빌드 완료"
}

# 서비스 시작
start_services() {
    print_step "서비스 시작 중..."
    
    docker-compose up -d
    
    print_success "서비스 시작 완료"
}

# 헬스체크
health_check() {
    print_step "서비스 헬스체크 중..."
    
    # 서비스가 시작될 때까지 대기
    sleep 30
    
    # API 헬스체크
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "API 서버 정상 동작"
    else
        print_error "API 서버 헬스체크 실패"
        docker-compose logs api
        exit 1
    fi
    
    # Frontend Admin 헬스체크
    if curl -f http://localhost:3000/admin/health &> /dev/null; then
        print_success "Frontend Admin 정상 동작"
    else
        print_error "Frontend Admin 헬스체크 실패"
        docker-compose logs frontend-admin
        exit 1
    fi
    
    # Nginx 헬스체크
    if curl -f http://localhost/health &> /dev/null; then
        print_success "Nginx 정상 동작"
    else
        print_error "Nginx 헬스체크 실패"
        docker-compose logs nginx
        exit 1
    fi
}

# 배포 정보 출력
print_deployment_info() {
    print_step "배포 정보"
    
    echo -e "${GREEN}🎉 SkyBoot Core 배포 완료!${NC}"
    echo ""
    echo "📍 서비스 접속 정보:"
    echo "   • API 서버: http://localhost:8000"
    echo "   • API 문서: http://localhost:8000/docs"
    echo "   • Admin 패널: http://localhost/admin"
    echo "   • Frontend Admin (직접): http://localhost:3000"
    echo ""
    echo "🔧 관리 명령어:"
    echo "   • 로그 확인: docker-compose logs -f [service_name]"
    echo "   • 서비스 중지: docker-compose down"
    echo "   • 서비스 재시작: docker-compose restart [service_name]"
    echo "   • 컨테이너 상태: docker-compose ps"
    echo ""
    echo "📊 기본 로그인 정보:"
    echo "   • 사용자명: admin"
    echo "   • 비밀번호: admin123"
    echo ""
}

# 메인 실행 함수
main() {
    echo -e "${BLUE}🚀 SkyBoot Core 프로덕션 배포 스크립트${NC}"
    echo "================================================"
    
    check_env
    check_docker
    cleanup_containers
    build_frontend
    build_images
    start_services
    health_check
    print_deployment_info
    
    echo -e "${GREEN}✨ 배포가 성공적으로 완료되었습니다!${NC}"
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
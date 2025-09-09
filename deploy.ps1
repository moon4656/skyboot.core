# SkyBoot Core - 프로덕션 배포 스크립트 (PowerShell)
# Vue 3 + Vuestic UI Admin Frontend + FastAPI Backend 배포

param(
    [switch]$SkipBuild,
    [switch]$SkipHealthCheck,
    [switch]$Verbose
)

# 에러 발생 시 스크립트 중단
$ErrorActionPreference = "Stop"

# 색상 함수 정의
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    switch ($Color) {
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Blue" { Write-Host $Message -ForegroundColor Blue }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message }
    }
}

function Print-Step {
    param([string]$Message)
    Write-ColorOutput "📋 $Message" "Blue"
}

function Print-Success {
    param([string]$Message)
    Write-ColorOutput "✅ $Message" "Green"
}

function Print-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠️  $Message" "Yellow"
}

function Print-Error {
    param([string]$Message)
    Write-ColorOutput "❌ $Message" "Red"
}

# 환경 변수 확인
function Test-Environment {
    Print-Step "환경 변수 확인 중..."
    
    if (-not (Test-Path ".env.production")) {
        Print-Error ".env.production 파일이 없습니다."
        Print-Warning "Copy-Item .env.production.example .env.production 명령으로 생성하고 설정을 수정하세요."
        exit 1
    }
    
    if (-not (Test-Path "frontend\frontend-admin\.env.production")) {
        Print-Error "frontend\frontend-admin\.env.production 파일이 없습니다."
        exit 1
    }
    
    Print-Success "환경 변수 파일 확인 완료"
}

# Docker 환경 확인
function Test-Docker {
    Print-Step "Docker 환경 확인 중..."
    
    try {
        $null = Get-Command docker -ErrorAction Stop
    }
    catch {
        Print-Error "Docker가 설치되지 않았습니다."
        exit 1
    }
    
    try {
        $null = Get-Command docker-compose -ErrorAction Stop
    }
    catch {
        Print-Error "Docker Compose가 설치되지 않았습니다."
        exit 1
    }
    
    try {
        docker info | Out-Null
    }
    catch {
        Print-Error "Docker 데몬이 실행되지 않았습니다."
        exit 1
    }
    
    Print-Success "Docker 환경 확인 완료"
}

# 기존 컨테이너 정리
function Clear-Containers {
    Print-Step "기존 컨테이너 정리 중..."
    
    try {
        docker-compose down --remove-orphans
        docker system prune -f
    }
    catch {
        Print-Warning "컨테이너 정리 중 일부 오류가 발생했지만 계속 진행합니다."
    }
    
    Print-Success "컨테이너 정리 완료"
}

# 프론트엔드 빌드
function Build-Frontend {
    if ($SkipBuild) {
        Print-Warning "빌드 단계를 건너뜁니다."
        return
    }
    
    Print-Step "Frontend Admin 빌드 중..."
    
    Push-Location "frontend\frontend-admin"
    
    try {
        # Node.js 의존성 설치
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }
        
        # 프로덕션 빌드
        npm run build
        
        Print-Success "Frontend Admin 빌드 완료"
    }
    catch {
        Print-Error "Frontend Admin 빌드 실패: $($_.Exception.Message)"
        exit 1
    }
    finally {
        Pop-Location
    }
}

# Docker 이미지 빌드
function Build-Images {
    if ($SkipBuild) {
        Print-Warning "이미지 빌드 단계를 건너뜁니다."
        return
    }
    
    Print-Step "Docker 이미지 빌드 중..."
    
    try {
        docker-compose build --no-cache
        Print-Success "Docker 이미지 빌드 완료"
    }
    catch {
        Print-Error "Docker 이미지 빌드 실패: $($_.Exception.Message)"
        exit 1
    }
}

# 서비스 시작
function Start-Services {
    Print-Step "서비스 시작 중..."
    
    try {
        docker-compose up -d
        Print-Success "서비스 시작 완료"
    }
    catch {
        Print-Error "서비스 시작 실패: $($_.Exception.Message)"
        exit 1
    }
}

# 헬스체크
function Test-Health {
    if ($SkipHealthCheck) {
        Print-Warning "헬스체크를 건너뜁니다."
        return
    }
    
    Print-Step "서비스 헬스체크 중..."
    
    # 서비스가 시작될 때까지 대기
    Start-Sleep -Seconds 30
    
    # API 헬스체크
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Print-Success "API 서버 정상 동작"
        } else {
            throw "API 서버 응답 코드: $($response.StatusCode)"
        }
    }
    catch {
        Print-Error "API 서버 헬스체크 실패: $($_.Exception.Message)"
        docker-compose logs api
        exit 1
    }
    
    # Frontend Admin 헬스체크
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/admin/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Print-Success "Frontend Admin 정상 동작"
        } else {
            throw "Frontend Admin 응답 코드: $($response.StatusCode)"
        }
    }
    catch {
        Print-Error "Frontend Admin 헬스체크 실패: $($_.Exception.Message)"
        docker-compose logs frontend-admin
        exit 1
    }
    
    # Nginx 헬스체크
    try {
        $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Print-Success "Nginx 정상 동작"
        } else {
            throw "Nginx 응답 코드: $($response.StatusCode)"
        }
    }
    catch {
        Print-Error "Nginx 헬스체크 실패: $($_.Exception.Message)"
        docker-compose logs nginx
        exit 1
    }
}

# 배포 정보 출력
function Show-DeploymentInfo {
    Print-Step "배포 정보"
    
    Write-ColorOutput "🎉 SkyBoot Core 배포 완료!" "Green"
    Write-Host ""
    Write-Host "📍 서비스 접속 정보:"
    Write-Host "   • API 서버: http://localhost:8000"
    Write-Host "   • API 문서: http://localhost:8000/docs"
    Write-Host "   • Admin 패널: http://localhost/admin"
    Write-Host "   • Frontend Admin (직접): http://localhost:3000"
    Write-Host ""
    Write-Host "🔧 관리 명령어:"
    Write-Host "   • 로그 확인: docker-compose logs -f [service_name]"
    Write-Host "   • 서비스 중지: docker-compose down"
    Write-Host "   • 서비스 재시작: docker-compose restart [service_name]"
    Write-Host "   • 컨테이너 상태: docker-compose ps"
    Write-Host ""
    Write-Host "📊 기본 로그인 정보:"
    Write-Host "   • 사용자명: admin"
    Write-Host "   • 비밀번호: admin123"
    Write-Host ""
}

# 메인 실행 함수
function Main {
    Write-ColorOutput "🚀 SkyBoot Core 프로덕션 배포 스크립트" "Blue"
    Write-Host "================================================"
    
    Test-Environment
    Test-Docker
    Clear-Containers
    Build-Frontend
    Build-Images
    Start-Services
    Test-Health
    Show-DeploymentInfo
    
    Write-ColorOutput "✨ 배포가 성공적으로 완료되었습니다!" "Green"
}

# 스크립트 실행
try {
    Main
}
catch {
    Print-Error "배포 중 오류가 발생했습니다: $($_.Exception.Message)"
    exit 1
}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그 관리 API 엔드포인트 테스트 스크립트

log_router.py에서 추출된 모든 엔드포인트를 체계적으로 테스트합니다.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

import httpx
from httpx import AsyncClient

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/logs"
TEST_TIMEOUT = 30.0

# 테스트 결과 저장
test_results = []
test_summary = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

# 테스트용 JWT 토큰 (실제 환경에서는 로그인을 통해 획득)
TEST_TOKEN = None

# 테스트용 로그인 정보
TEST_LOGIN_DATA = {
    "user_id": "admin",  # 실제 테스트 계정으로 변경 필요
    "password": "admin123"  # 실제 테스트 비밀번호로 변경 필요
}

class LogRouterTester:
    """
    로그 라우터 API 테스트 클래스
    """
    
    def __init__(self):
        self.client = None
        self.headers = {}
        self.test_log_id = None
        self.test_user_id = "test_user_001"
        
    async def setup(self):
        """
        테스트 환경 설정
        """
        print("🚀 로그 라우터 API 테스트 시작")
        print(f"📡 Base URL: {BASE_URL}")
        print(f"📡 API Prefix: {API_PREFIX}")
        
        # HTTP 클라이언트 초기화
        self.client = AsyncClient(
            base_url=BASE_URL,
            timeout=TEST_TIMEOUT,
            verify=False
        )
        
        # 인증 토큰 획득 시도
        await self.authenticate()
        
        print("✅ 테스트 환경 설정 완료")
    
    async def authenticate(self):
        """
        로그인을 통한 인증 토큰 획득
        """
        global TEST_TOKEN
        
        if TEST_TOKEN:
            self.headers["Authorization"] = f"Bearer {TEST_TOKEN}"
            print("✅ 기존 토큰 사용")
            return
        
        # 두 가지 로그인 엔드포인트 시도
        login_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/users/one-click-login"
        ]
        
        for login_url in login_endpoints:
            try:
                print(f"🔐 로그인 시도: {login_url}")
                
                # 로그인 API 호출 (JSON 형식으로 시도)
                login_response = await self.client.post(
                    login_url,
                    json=TEST_LOGIN_DATA  # JSON 형식으로 전송
                )
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    if "access_token" in login_result:
                        TEST_TOKEN = login_result["access_token"]
                        self.headers["Authorization"] = f"Bearer {TEST_TOKEN}"
                        print(f"✅ 로그인 성공, 토큰 획득 (엔드포인트: {login_url})")
                        return
                    else:
                        print(f"⚠️ 토큰이 응답에 없음: {login_result}")
                else:
                    print(f"❌ 로그인 실패 ({login_url}): {login_response.status_code} - {login_response.text}")
                    
            except Exception as e:
                print(f"❌ 로그인 오류 ({login_url}): {str(e)}")
        
        print("❌ 모든 로그인 엔드포인트에서 실패")
        print("📝 테스트용 더미 토큰 사용 (일부 테스트가 실패할 수 있음)")
        self.headers["Authorization"] = "Bearer test_token_for_development"
    
    async def cleanup(self):
        """
        테스트 환경 정리
        """
        if self.client:
            await self.client.aclose()
        print("🧹 테스트 환경 정리 완료")
    
    def log_test_result(self, test_name: str, success: bool, response_data: Any = None, 
                       error_message: str = None, status_code: int = None):
        """
        테스트 결과 로깅
        """
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error_message": error_message,
            "status_code": status_code
        }
        
        test_results.append(result)
        test_summary["total_tests"] += 1
        
        if success:
            test_summary["passed"] += 1
            print(f"✅ {test_name} - 성공")
        else:
            test_summary["failed"] += 1
            test_summary["errors"].append(error_message or "Unknown error")
            print(f"❌ {test_name} - 실패: {error_message}")
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict = None, 
                           params: Dict = None, expected_status: int = 200, 
                           test_name: str = None, allow_401: bool = False):
        """
        공통 엔드포인트 테스트 메서드
        """
        if not test_name:
            test_name = f"{method} {endpoint}"
        
        try:
            start_time = datetime.now()
            
            if method.upper() == "GET":
                response = await self.client.get(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.headers,
                    params=params or {}
                )
            elif method.upper() == "POST":
                response = await self.client.post(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.headers,
                    json=data,
                    params=params or {}
                )
            elif method.upper() == "PUT":
                response = await self.client.put(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.headers,
                    json=data,
                    params=params or {}
                )
            elif method.upper() == "DELETE":
                response = await self.client.delete(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.headers,
                    params=params or {}
                )
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 응답 처리
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            # 401 오류 처리 (인증 실패)
            if response.status_code == 401:
                if allow_401:
                    self.log_test_result(test_name, True, response_data, "인증 필요 (예상된 결과)", response.status_code)
                    return response_data
                else:
                    error_msg = f"인증 실패 - 유효한 토큰이 필요합니다 (상태코드: 401)"
                    self.log_test_result(test_name, False, response_data, error_msg, response.status_code)
                    return None
            
            # 테스트 결과 판정
            if response.status_code == expected_status:
                self.log_test_result(test_name, True, response_data, status_code=response.status_code)
                return response_data
            else:
                error_msg = f"예상 상태코드: {expected_status}, 실제: {response.status_code}"
                self.log_test_result(test_name, False, response_data, error_msg, response.status_code)
                return None
                
        except Exception as e:
            error_msg = f"요청 실행 중 오류: {str(e)}"
            self.log_test_result(test_name, False, error_message=error_msg)
            return None
    
    # ==================== 로그인 로그 기본 API 테스트 ====================
    
    async def test_get_login_logs(self):
        """
        로그인 로그 목록 조회 테스트
        """
        params = {
            "skip": 0,
            "limit": 10
        }
        return await self.test_endpoint(
            "GET", "/", 
            params=params,
            test_name="로그인 로그 목록 조회"
        )
    
    async def test_get_recent_logs(self):
        """
        최근 로그인 로그 조회 테스트
        """
        params = {
            "hours": 24,
            "limit": 50
        }
        return await self.test_endpoint(
            "GET", "/recent", 
            params=params,
            test_name="최근 로그인 로그 조회"
        )
    
    async def test_get_user_logs(self):
        """
        사용자별 로그인 로그 조회 테스트
        """
        params = {
            "days": 30,
            "limit": 100
        }
        return await self.test_endpoint(
            "GET", f"/user/{self.test_user_id}", 
            params=params,
            test_name="사용자별 로그인 로그 조회"
        )
    
    async def test_get_failed_attempts(self):
        """
        실패한 로그인 시도 조회 테스트
        """
        params = {
            "hours": 24,
            "limit": 100
        }
        return await self.test_endpoint(
            "GET", "/failed", 
            params=params,
            test_name="실패한 로그인 시도 조회"
        )
    
    async def test_create_login_log(self):
        """
        로그인 로그 생성 테스트
        """
        log_data = {
            "user_id": self.test_user_id,
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "login_result": "SUCCESS",
            "failure_reason": None
        }
        
        result = await self.test_endpoint(
            "POST", "/", 
            data=log_data,
            expected_status=200,
            test_name="로그인 로그 생성"
        )
        
        if result and "id" in result:
            self.test_log_id = result["id"]
            print(f"📝 생성된 테스트 로그 ID: {self.test_log_id}")
        
        return result
    
    async def test_get_login_log_detail(self):
        """
        로그인 로그 상세 조회 테스트
        """
        if not self.test_log_id:
            print("⚠️ 테스트 로그 ID가 없어 상세 조회를 건너뜁니다.")
            return None
        
        return await self.test_endpoint(
            "GET", f"/{self.test_log_id}", 
            test_name="로그인 로그 상세 조회"
        )
    
    async def test_update_login_log(self):
        """
        로그인 로그 수정 테스트
        """
        if not self.test_log_id:
            print("⚠️ 테스트 로그 ID가 없어 수정을 건너뜁니다.")
            return None
        
        update_data = {
            "failure_reason": "테스트 수정"
        }
        
        return await self.test_endpoint(
            "PUT", f"/{self.test_log_id}", 
            data=update_data,
            test_name="로그인 로그 수정"
        )
    
    async def test_delete_login_log(self):
        """
        로그인 로그 삭제 테스트
        """
        if not self.test_log_id:
            print("⚠️ 테스트 로그 ID가 없어 삭제를 건너뜁니다.")
            return None
        
        return await self.test_endpoint(
            "DELETE", f"/{self.test_log_id}", 
            test_name="로그인 로그 삭제"
        )
    
    # ==================== 로그 통계 및 분석 API 테스트 ====================
    
    async def test_get_login_statistics(self):
        """
        로그인 통계 조회 테스트
        """
        params = {"days": 30}
        return await self.test_endpoint(
            "GET", "/statistics/overview", 
            params=params,
            test_name="로그인 통계 조회"
        )
    
    async def test_get_daily_statistics(self):
        """
        일별 로그인 통계 조회 테스트
        """
        params = {"days": 30}
        return await self.test_endpoint(
            "GET", "/statistics/daily", 
            params=params,
            test_name="일별 로그인 통계 조회"
        )
    
    async def test_get_hourly_statistics(self):
        """
        시간별 로그인 통계 조회 테스트
        """
        params = {"days": 7}
        return await self.test_endpoint(
            "GET", "/statistics/hourly", 
            params=params,
            test_name="시간별 로그인 통계 조회"
        )
    
    async def test_get_top_ip_statistics(self):
        """
        상위 IP 주소 통계 조회 테스트
        """
        params = {
            "days": 30,
            "limit": 10
        }
        return await self.test_endpoint(
            "GET", "/statistics/top-ips", 
            params=params,
            test_name="상위 IP 주소 통계 조회"
        )
    
    # ==================== 보안 및 모니터링 API 테스트 ====================
    
    async def test_get_security_alerts(self):
        """
        보안 알림 조회 테스트
        """
        params = {"hours": 24}
        return await self.test_endpoint(
            "GET", "/security/alerts", 
            params=params,
            test_name="보안 알림 조회"
        )
    
    async def test_get_suspicious_activities(self):
        """
        의심스러운 활동 조회 테스트
        """
        params = {"hours": 24}
        return await self.test_endpoint(
            "GET", "/security/suspicious", 
            params=params,
            test_name="의심스러운 활동 조회"
        )
    
    async def test_get_repeated_failures(self):
        """
        반복 실패 시도 조회 테스트
        """
        params = {
            "hours": 24,
            "min_attempts": 5
        }
        return await self.test_endpoint(
            "GET", "/security/repeated-failures", 
            params=params,
            test_name="반복 실패 시도 조회"
        )
    
    async def test_get_unusual_login_times(self):
        """
        비정상 시간대 로그인 조회 테스트
        """
        params = {"days": 7}
        return await self.test_endpoint(
            "GET", "/security/unusual-times", 
            params=params,
            test_name="비정상 시간대 로그인 조회"
        )
    
    async def test_get_new_ip_logins(self):
        """
        새로운 IP 로그인 조회 테스트
        """
        params = {"days": 7}
        return await self.test_endpoint(
            "GET", "/security/new-ip-logins", 
            params=params,
            test_name="새로운 IP 로그인 조회"
        )
    
    # ==================== 세션 관리 API 테스트 ====================
    
    async def test_get_active_sessions(self):
        """
        활성 세션 조회 테스트
        """
        return await self.test_endpoint(
            "GET", "/sessions/active", 
            test_name="활성 세션 조회"
        )
    
    async def test_get_user_sessions(self):
        """
        사용자 세션 조회 테스트
        """
        return await self.test_endpoint(
            "GET", f"/sessions/user/{self.test_user_id}", 
            test_name="사용자 세션 조회"
        )
    
    # ==================== 로그 관리 API 테스트 ====================
    
    async def test_cleanup_old_logs(self):
        """
        오래된 로그 정리 테스트
        """
        params = {"days": 90}
        return await self.test_endpoint(
            "POST", "/cleanup", 
            params=params,
            test_name="오래된 로그 정리"
        )
    
    async def test_export_logs(self):
        """
        로그 데이터 내보내기 테스트
        """
        params = {
            "format": "csv",
            "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
            "end_date": datetime.now().isoformat()
        }
        return await self.test_endpoint(
            "GET", "/export", 
            params=params,
            test_name="로그 데이터 내보내기"
        )
    
    async def test_analyze_logs(self):
        """
        로그 분석 테스트
        """
        params = {
            "days": 30,
            "analysis_type": "overview"
        }
        return await self.test_endpoint(
            "GET", "/analysis", 
            params=params,
            test_name="로그 분석"
        )
    
    # ==================== 전체 테스트 실행 ====================
    
    async def run_all_tests(self):
        """
        모든 테스트 실행
        """
        await self.setup()
        
        try:
            print("\n📋 기본 로그 API 테스트 시작")
            await self.test_get_login_logs()
            await self.test_get_recent_logs()
            await self.test_get_user_logs()
            await self.test_get_failed_attempts()
            
            # CRUD 테스트 (순서 중요)
            print("\n📋 CRUD 테스트 시작")
            await self.test_create_login_log()
            await self.test_get_login_log_detail()
            await self.test_update_login_log()
            # 삭제는 마지막에 실행
            
            print("\n📊 통계 및 분석 API 테스트 시작")
            await self.test_get_login_statistics()
            await self.test_get_daily_statistics()
            await self.test_get_hourly_statistics()
            await self.test_get_top_ip_statistics()
            
            print("\n🔒 보안 및 모니터링 API 테스트 시작")
            await self.test_get_security_alerts()
            await self.test_get_suspicious_activities()
            await self.test_get_repeated_failures()
            await self.test_get_unusual_login_times()
            await self.test_get_new_ip_logins()
            
            print("\n👥 세션 관리 API 테스트 시작")
            await self.test_get_active_sessions()
            await self.test_get_user_sessions()
            
            print("\n🗂️ 로그 관리 API 테스트 시작")
            await self.test_export_logs()
            await self.test_analyze_logs()
            # cleanup은 실제 데이터에 영향을 줄 수 있으므로 주석 처리
            # await self.test_cleanup_old_logs()
            
            # 마지막에 삭제 테스트
            print("\n🗑️ 삭제 테스트 시작")
            await self.test_delete_login_log()
            
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류 발생: {str(e)}")
            traceback.print_exc()
        
        finally:
            await self.cleanup()
            self.print_test_summary()
            await self.save_test_results()
    
    def print_test_summary(self):
        """
        테스트 결과 요약 출력
        """
        print("\n" + "="*60)
        print("📊 테스트 결과 요약")
        print("="*60)
        print(f"총 테스트 수: {test_summary['total_tests']}")
        print(f"성공: {test_summary['passed']}")
        print(f"실패: {test_summary['failed']}")
        
        if test_summary['total_tests'] > 0:
            success_rate = (test_summary['passed'] / test_summary['total_tests']) * 100
            print(f"성공률: {success_rate:.1f}%")
        
        if test_summary['errors']:
            print("\n❌ 오류 목록:")
            for i, error in enumerate(test_summary['errors'], 1):
                print(f"  {i}. {error}")
    
    async def save_test_results(self):
        """
        테스트 결과를 파일로 저장
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON 결과 파일
        json_filename = f"log_router_test_results_{timestamp}.json"
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump({
                "summary": test_summary,
                "test_results": test_results
            }, f, ensure_ascii=False, indent=2, default=str)
        
        # 마크다운 보고서
        md_filename = f"log_router_test_report_{timestamp}.md"
        report_content = f"""# Log Router API 테스트 보고서

**테스트 실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Base URL**: {BASE_URL}
**API Prefix**: {API_PREFIX}

## 📊 테스트 결과 요약

- **총 테스트 수**: {test_summary['total_tests']}
- **성공**: {test_summary['passed']}
- **실패**: {test_summary['failed']}
- **성공률**: {(test_summary['passed'] / test_summary['total_tests'] * 100):.1f}%

## 📋 상세 테스트 결과

"""
        
        for result in test_results:
            status = "✅ 성공" if result['success'] else "❌ 실패"
            report_content += f"### {result['test_name']}\n"
            report_content += f"- **상태**: {status}\n"
            report_content += f"- **실행 시간**: {result['timestamp']}\n"
            
            if result['status_code']:
                report_content += f"- **상태 코드**: {result['status_code']}\n"
            
            if result['error_message']:
                report_content += f"- **오류 메시지**: {result['error_message']}\n"
            
            report_content += "\n"
        
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n📄 테스트 결과 저장 완료:")
        print(f"  - JSON: {json_filename}")
        print(f"  - 보고서: {md_filename}")


async def main():
    """
    메인 실행 함수
    """
    tester = LogRouterTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # 이벤트 루프 실행
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
"""시스템 라우터 통합 테스트

시스템 라우터의 모든 엔드포인트에 대한 통합 테스트를 수행합니다.
시스템 로그, 웹 로그, 시스템 모니터링 기능을 종합적으로 검증합니다.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/system"

class SystemRouterIntegrationTester:
    """시스템 라우터 통합 테스터"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_prefix = API_PREFIX
        self.test_results = []
        self.session = requests.Session()
        self.access_token = None
        self.created_resources = []  # 생성된 리소스 추적
    
    def log_test_result(self, test_name: str, endpoint: str, method: str, 
                       status_code: int, expected_status: int, 
                       response_data: Any = None, error_message: str = None):
        """테스트 결과 로깅"""
        success = status_code == expected_status
        result = {
            "test_name": test_name,
            "endpoint": endpoint,
            "method": method,
            "expected_status": expected_status,
            "actual_status": status_code,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data,
            "error_message": error_message
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {test_name}: {method} {endpoint} - 예상: {expected_status}, 실제: {status_code}")
        if error_message:
            print(f"   오류: {error_message}")
    
    def authenticate(self):
        """로그인을 통한 인증 토큰 획득"""
        login_data = {
            "user_id": "admin",
            "password": "admin123"
        }
        
        # 두 가지 로그인 엔드포인트 시도
        login_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/users/one-click-login"
        ]
        
        for login_url in login_endpoints:
            try:
                print(f"🔐 로그인 시도: {login_url}")
                response = self.session.post(f"{self.base_url}{login_url}", json=login_data)
                
                if response.status_code == 200:
                    login_result = response.json()
                    if "access_token" in login_result:
                        self.access_token = login_result["access_token"]
                        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                        print(f"✅ 로그인 성공, 토큰 획득")
                        return True
                    else:
                        print(f"⚠️ 토큰이 응답에 없음: {login_result}")
                else:
                    print(f"❌ 로그인 실패: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ 로그인 오류: {str(e)}")
        
        print("❌ 모든 로그인 시도 실패")
        return False
    
    def test_system_health_endpoints(self):
        """시스템 상태 관련 엔드포인트 테스트"""
        print("\n🏥 시스템 상태 관련 엔드포인트 테스트")
        
        # 1. 시스템 상태 확인
        endpoint = f"{self.api_prefix}/health"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            self.log_test_result(
                "시스템 상태 확인",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "시스템 상태 확인",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
        
        # 2. 대시보드 요약
        endpoint = f"{self.api_prefix}/dashboard"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            self.log_test_result(
                "대시보드 요약 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "대시보드 요약 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_syslog_crud_workflow(self):
        """시스템 로그 CRUD 워크플로우 테스트"""
        print("\n📋 시스템 로그 CRUD 워크플로우 테스트")
        
        # 테스트 데이터
        test_data = {
            "requst_id": f"INTEGRATION_TEST_{int(time.time())}",
            "job_se_code": "001",
            "instt_code": "1234567",
            "rqester_id": "integration_test_user",
            "rqester_ip": "192.168.1.200",
            "trget_menu_nm": "통합테스트메뉴",
            "svc_nm": "통합테스트서비스",
            "method_nm": "integration_test_method",
            "process_se_code": "SUC",
            "process_co": 1,
            "process_time": "2000",
            "rspns_code": "200",
            "error_se": "N",
            "error_co": 0,
            "error_code": None
        }
        
        # 1. 시스템 로그 생성
        endpoint = f"{self.api_prefix}/logs/"
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.log_test_result(
                "시스템 로그 생성",
                endpoint,
                "POST",
                response.status_code,
                201,
                response.json() if response.status_code == 201 else None,
                response.text if response.status_code != 201 else None
            )
            
            if response.status_code == 201:
                created_log = response.json()
                log_id = created_log.get("id")
                self.created_resources.append(("syslog", log_id))
                
                # 2. 생성된 로그 조회
                endpoint = f"{self.api_prefix}/logs/{log_id}"
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    self.log_test_result(
                        "시스템 로그 상세 조회",
                        endpoint,
                        "GET",
                        response.status_code,
                        200,
                        response.json() if response.status_code == 200 else None,
                        response.text if response.status_code != 200 else None
                    )
                except Exception as e:
                    self.log_test_result(
                        "시스템 로그 상세 조회",
                        endpoint,
                        "GET",
                        0,
                        200,
                        error_message=str(e)
                    )
                
                # 3. 로그 수정
                update_data = {"process_time": "3000"}
                endpoint = f"{self.api_prefix}/logs/{log_id}"
                try:
                    response = self.session.put(
                        f"{self.base_url}{endpoint}",
                        json=update_data,
                        headers={"Content-Type": "application/json"}
                    )
                    self.log_test_result(
                        "시스템 로그 수정",
                        endpoint,
                        "PUT",
                        response.status_code,
                        200,
                        response.json() if response.status_code == 200 else None,
                        response.text if response.status_code != 200 else None
                    )
                except Exception as e:
                    self.log_test_result(
                        "시스템 로그 수정",
                        endpoint,
                        "PUT",
                        0,
                        200,
                        error_message=str(e)
                    )
                
        except Exception as e:
            self.log_test_result(
                "시스템 로그 생성",
                endpoint,
                "POST",
                0,
                201,
                error_message=str(e)
            )
        
        # 4. 시스템 로그 목록 조회
        endpoint = f"{self.api_prefix}/logs/"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}?skip=0&limit=10")
            self.log_test_result(
                "시스템 로그 목록 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "시스템 로그 목록 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
        
        # 5. 시스템 로그 검색
        endpoint = f"{self.api_prefix}/logs/search"
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?rqester_id=integration_test_user&skip=0&limit=10"
            )
            self.log_test_result(
                "시스템 로그 검색",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "시스템 로그 검색",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
        
        # 6. 시스템 로그 통계
        endpoint = f"{self.api_prefix}/logs/statistics"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}?days=30")
            self.log_test_result(
                "시스템 로그 통계 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "시스템 로그 통계 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_weblog_crud_workflow(self):
        """웹 로그 CRUD 워크플로우 테스트"""
        print("\n🌐 웹 로그 CRUD 워크플로우 테스트")
        
        # 테스트 데이터
        test_data = {
            "conect_id": f"INTEGRATION_WEB_{int(time.time())}",
            "user_id": "integration_test_user",
            "ip_adres": "192.168.1.200",
            "conect_dt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "url": "/integration/test/page",
            "http_method": "GET",
            "user_agent": "Integration Test Agent",
            "referer": "https://test.example.com",
            "response_code": 200,
            "response_time": 150,
            "bytes_sent": 2048
        }
        
        # 1. 웹 로그 생성
        endpoint = f"{self.api_prefix}/web-logs/"
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.log_test_result(
                "웹 로그 생성",
                endpoint,
                "POST",
                response.status_code,
                201,
                response.json() if response.status_code == 201 else None,
                response.text if response.status_code != 201 else None
            )
            
            if response.status_code == 201:
                created_log = response.json()
                conect_id = created_log.get("conect_id")
                self.created_resources.append(("weblog", conect_id))
                
                # 2. 생성된 웹 로그 조회
                endpoint = f"{self.api_prefix}/web-logs/{conect_id}"
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                    self.log_test_result(
                        "웹 로그 상세 조회",
                        endpoint,
                        "GET",
                        response.status_code,
                        200,
                        response.json() if response.status_code == 200 else None,
                        response.text if response.status_code != 200 else None
                    )
                except Exception as e:
                    self.log_test_result(
                        "웹 로그 상세 조회",
                        endpoint,
                        "GET",
                        0,
                        200,
                        error_message=str(e)
                    )
                
        except Exception as e:
            self.log_test_result(
                "웹 로그 생성",
                endpoint,
                "POST",
                0,
                201,
                error_message=str(e)
            )
        
        # 3. 웹 로그 목록 조회
        endpoint = f"{self.api_prefix}/web-logs/"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}?skip=0&limit=10")
            self.log_test_result(
                "웹 로그 목록 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "웹 로그 목록 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
        
        # 4. 인기 페이지 조회
        endpoint = f"{self.api_prefix}/web-logs/popular-pages"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}?days=30&limit=10")
            self.log_test_result(
                "인기 페이지 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "인기 페이지 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
        
        # 5. 시간별 트래픽 조회
        endpoint = f"{self.api_prefix}/web-logs/hourly-traffic"
        try:
            response = self.session.get(f"{self.base_url}{endpoint}?days=7")
            self.log_test_result(
                "시간별 트래픽 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
        except Exception as e:
            self.log_test_result(
                "시간별 트래픽 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def cleanup_created_resources(self):
        """생성된 리소스 정리"""
        print("\n🧹 생성된 리소스 정리")
        
        for resource_type, resource_id in self.created_resources:
            if resource_type == "syslog":
                endpoint = f"{self.api_prefix}/logs/{resource_id}"
                try:
                    response = self.session.delete(f"{self.base_url}{endpoint}")
                    self.log_test_result(
                        "시스템 로그 삭제 (정리)",
                        endpoint,
                        "DELETE",
                        response.status_code,
                        200,
                        response.json() if response.status_code == 200 else None,
                        response.text if response.status_code != 200 else None
                    )
                except Exception as e:
                    self.log_test_result(
                        "시스템 로그 삭제 (정리)",
                        endpoint,
                        "DELETE",
                        0,
                        200,
                        error_message=str(e)
                    )
            
            elif resource_type == "weblog":
                endpoint = f"{self.api_prefix}/web-logs/{resource_id}"
                try:
                    response = self.session.delete(f"{self.base_url}{endpoint}")
                    self.log_test_result(
                        "웹 로그 삭제 (정리)",
                        endpoint,
                        "DELETE",
                        response.status_code,
                        200,
                        response.json() if response.status_code == 200 else None,
                        response.text if response.status_code != 200 else None
                    )
                except Exception as e:
                    self.log_test_result(
                        "웹 로그 삭제 (정리)",
                        endpoint,
                        "DELETE",
                        0,
                        200,
                        error_message=str(e)
                    )
    
    def run_integration_tests(self):
        """통합 테스트 실행"""
        print("\n🚀 시스템 라우터 통합 테스트 시작")
        print("=" * 60)
        
        # 인증 토큰 획득
        if not self.authenticate():
            print("❌ 인증 실패로 테스트를 중단합니다.")
            return
        
        # 1. 시스템 상태 관련 엔드포인트 테스트
        self.test_system_health_endpoints()
        
        # 2. 시스템 로그 CRUD 워크플로우 테스트
        self.test_syslog_crud_workflow()
        
        # 3. 웹 로그 CRUD 워크플로우 테스트
        self.test_weblog_crud_workflow()
        
        # 4. 생성된 리소스 정리
        self.cleanup_created_resources()
        
        # 결과 요약
        self.print_test_summary()
        
        # 결과를 JSON 파일로 저장
        self.save_test_results()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 시스템 라우터 통합 테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {successful_tests}개 ✅")
        print(f"실패: {failed_tests}개 ❌")
        print(f"성공률: {(successful_tests/total_tests*100):.1f}%")
        
        # 카테고리별 성공률
        categories = {
            "시스템 상태": ["시스템 상태 확인", "대시보드 요약 조회"],
            "시스템 로그": ["시스템 로그 생성", "시스템 로그 상세 조회", "시스템 로그 수정", "시스템 로그 목록 조회", "시스템 로그 검색", "시스템 로그 통계 조회", "시스템 로그 삭제 (정리)"],
            "웹 로그": ["웹 로그 생성", "웹 로그 상세 조회", "웹 로그 목록 조회", "인기 페이지 조회", "시간별 트래픽 조회", "웹 로그 삭제 (정리)"]
        }
        
        print("\n📈 카테고리별 성공률:")
        for category, test_names in categories.items():
            category_results = [r for r in self.test_results if r["test_name"] in test_names]
            if category_results:
                category_success = sum(1 for r in category_results if r["success"])
                category_total = len(category_results)
                category_rate = (category_success / category_total * 100) if category_total > 0 else 0
                print(f"  - {category}: {category_success}/{category_total} ({category_rate:.1f}%)")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    error_msg = result["error_message"] or "상태코드 불일치"
                    if len(error_msg) > 100:
                        error_msg = error_msg[:100] + "..."
                    print(f"  - {result['test_name']}: {error_msg}")
    
    def save_test_results(self):
        """테스트 결과를 JSON 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_router_integration_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 통합 테스트 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = SystemRouterIntegrationTester()
    tester.run_integration_tests()


if __name__ == "__main__":
    main()
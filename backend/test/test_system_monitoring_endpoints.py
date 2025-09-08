"""시스템 모니터링 엔드포인트 테스트

시스템 모니터링 관련 5개 엔드포인트에 대한 단위 테스트를 수행합니다.
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List
import time

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/system"

class SystemMonitoringEndpointTester:
    """시스템 모니터링 엔드포인트 테스터"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_prefix = API_PREFIX
        self.test_results = []
        self.session = requests.Session()
        self.access_token = None
    
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
    
    def test_get_health_check(self):
        """1. 시스템 상태 확인 테스트"""
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
    
    def test_get_log_statistics(self):
        """2. 시스템 로그 통계 조회 테스트"""
        endpoint = f"{self.api_prefix}/logs/statistics"
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?days=30"
            )
            
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
    
    def test_get_dashboard_summary(self):
        """3. 대시보드 요약 조회 테스트"""
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
    
    def test_get_program_list(self):
        """4. 프로그램 목록 조회 테스트"""
        endpoint = "/api/v1/programs"
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?skip=0&limit=10"
            )
            
            self.log_test_result(
                "프로그램 목록 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "프로그램 목록 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_search_programs(self):
        """5. 프로그램 검색 테스트"""
        endpoint = "/api/v1/programs/search"
        
        search_params = {
            "progrm_korean_nm": "테스트",
            "skip": 0,
            "limit": 10
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=search_params
            )
            
            self.log_test_result(
                "프로그램 검색",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "프로그램 검색",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_create_program(self) -> str:
        """보너스: 프로그램 생성 테스트 (CRUD 완성을 위해)"""
        endpoint = "/api/v1/programs"
        
        test_program_data = {
            "progrm_nm": f"test_program_{int(time.time())}",
            "progrm_file_nm": f"test_program_{int(time.time())}.py",
            "progrm_stre_path": "/test/path",
            "progrm_korean_nm": "테스트프로그램",
            "progrm_dc": "테스트용 프로그램입니다",
            "url": "/test/url"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=test_program_data,
                headers={"Content-Type": "application/json"}
            )
            
            self.log_test_result(
                "프로그램 생성 (보너스)",
                endpoint,
                "POST",
                response.status_code,
                201,
                response.json() if response.status_code == 201 else None,
                response.text if response.status_code != 201 else None
            )
            
            if response.status_code == 201:
                return response.json().get("progrm_file_nm")
            return test_program_data["progrm_file_nm"]
            
        except Exception as e:
            self.log_test_result(
                "프로그램 생성 (보너스)",
                endpoint,
                "POST",
                0,
                201,
                error_message=str(e)
            )
            return test_program_data["progrm_file_nm"]
    
    def test_delete_program(self, program_file_name: str):
        """보너스: 프로그램 삭제 테스트 (정리용)"""
        endpoint = f"/api/v1/programs/{program_file_name}"
        
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}")
            
            self.log_test_result(
                "프로그램 삭제 (정리)",
                endpoint,
                "DELETE",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "프로그램 삭제 (정리)",
                endpoint,
                "DELETE",
                0,
                200,
                error_message=str(e)
            )
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n🚀 시스템 모니터링 엔드포인트 테스트 시작")
        print("=" * 50)
        
        # 인증 토큰 획득
        if not self.authenticate():
            print("❌ 인증 실패로 테스트를 중단합니다.")
            return
        
        # 1. 시스템 상태 확인
        self.test_get_health_check()
        
        # 2. 로그 통계 조회
        self.test_get_log_statistics()
        
        # 3. 대시보드 요약 조회
        self.test_get_dashboard_summary()
        
        # 4. 프로그램 목록 조회
        self.test_get_program_list()
        
        # 5. 프로그램 검색
        self.test_search_programs()
        
        # 보너스: 프로그램 CRUD 테스트
        print("\n📋 보너스: 프로그램 CRUD 테스트")
        program_file_name = self.test_create_program()
        self.test_delete_program(program_file_name)
        
        # 결과 요약
        self.print_test_summary()
        
        # 결과를 JSON 파일로 저장
        self.save_test_results()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📊 시스템 모니터링 엔드포인트 테스트 결과 요약")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {successful_tests}개 ✅")
        print(f"실패: {failed_tests}개 ❌")
        print(f"성공률: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['error_message'] or '상태코드 불일치'}")
    
    def save_test_results(self):
        """테스트 결과를 JSON 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monitoring_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = SystemMonitoringEndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
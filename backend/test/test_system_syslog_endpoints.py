"""시스템 로그(SysLog) 엔드포인트 테스트

시스템 로그 관련 8개 엔드포인트에 대한 단위 테스트를 수행합니다.
"""

import json
import requests
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
import time

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/system"

class SysLogEndpointTester:
    """시스템 로그 엔드포인트 테스터"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_prefix = API_PREFIX
        self.test_results = []
        self.session = requests.Session()
        self.access_token = None
        self.test_data = {
            "requst_id": f"TEST_{int(time.time())}",
            "job_se_code": "001",
            "instt_code": "1234567",
            "rqester_id": "test_user",
            "rqester_ip": "192.168.1.100",
            "trget_menu_nm": "테스트메뉴",
            "svc_nm": "테스트서비스",
            "method_nm": "test_method",
            "process_se_code": "SUC",
            "process_co": 1,
            "process_time": "1500",
            "rspns_code": "200",
            "error_se": "N",
            "error_co": 0,
            "error_code": None
        }
    
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
    
    def test_create_syslog(self) -> str:
        """1. 시스템 로그 생성 테스트"""
        endpoint = f"{self.api_prefix}/logs/"
        
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=self.test_data,
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
                return response.json().get("requst_id")
            return self.test_data["requst_id"]
            
        except Exception as e:
            self.log_test_result(
                "시스템 로그 생성",
                endpoint,
                "POST",
                0,
                201,
                error_message=str(e)
            )
            return self.test_data["requst_id"]
    
    def test_get_syslogs(self):
        """2. 시스템 로그 목록 조회 테스트"""
        endpoint = f"{self.api_prefix}/logs/"
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?page=1&size=10"
            )
            
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
    
    def test_get_syslog_detail(self, requst_id: str):
        """3. 시스템 로그 상세 조회 테스트"""
        endpoint = f"{self.api_prefix}/logs/{requst_id}"
        
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
    
    def test_update_syslog(self, requst_id: str):
        """4. 시스템 로그 수정 테스트"""
        endpoint = f"{self.api_prefix}/logs/{requst_id}"
        
        update_data = {
            "process_time": "2000"
        }
        
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
    
    def test_search_syslogs(self):
        """5. 시스템 로그 검색 테스트"""
        endpoint = f"{self.api_prefix}/logs/search"
        
        search_params = {
            "rqester_id": "test_user",
            "process_se_code": "SUCCESS",
            "page": 1,
            "size": 10
        }
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}",
                params=search_params
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
    
    def test_get_user_logs(self):
        """6. 사용자별 로그 조회 테스트"""
        endpoint = f"{self.api_prefix}/logs/user/test_user"
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?days=30"
            )
            
            self.log_test_result(
                "사용자별 로그 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "사용자별 로그 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_get_error_logs(self):
        """7. 오류 로그 조회 테스트"""
        endpoint = f"{self.api_prefix}/logs/errors"
        
        try:
            response = self.session.get(
                f"{self.base_url}{endpoint}?days=7"
            )
            
            self.log_test_result(
                "오류 로그 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "오류 로그 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_delete_syslog(self, requst_id: str):
        """8. 시스템 로그 삭제 테스트"""
        endpoint = f"{self.api_prefix}/logs/{requst_id}"
        
        try:
            response = self.session.delete(f"{self.base_url}{endpoint}")
            
            self.log_test_result(
                "시스템 로그 삭제",
                endpoint,
                "DELETE",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "시스템 로그 삭제",
                endpoint,
                "DELETE",
                0,
                200,
                error_message=str(e)
            )
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n🚀 시스템 로그 엔드포인트 테스트 시작")
        print("=" * 50)
        
        # 인증 토큰 획득
        if not self.authenticate():
            print("❌ 인증 실패로 테스트를 중단합니다.")
            return
        
        # 1. 시스템 로그 생성
        requst_id = self.test_create_syslog()
        
        # 2. 시스템 로그 목록 조회
        self.test_get_syslogs()
        
        # 3. 시스템 로그 상세 조회
        self.test_get_syslog_detail(requst_id)
        
        # 4. 시스템 로그 수정
        self.test_update_syslog(requst_id)
        
        # 5. 시스템 로그 검색
        self.test_search_syslogs()
        
        # 6. 사용자별 로그 조회
        self.test_get_user_logs()
        
        # 7. 오류 로그 조회
        self.test_get_error_logs()
        
        # 8. 시스템 로그 삭제
        self.test_delete_syslog(requst_id)
        
        # 결과 요약
        self.print_test_summary()
        
        # 결과를 JSON 파일로 저장
        self.save_test_results()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📊 시스템 로그 엔드포인트 테스트 결과 요약")
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
        filename = f"syslog_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = SysLogEndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
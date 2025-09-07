"""웹 로그(WebLog) 엔드포인트 테스트

웹 로그 관련 9개 엔드포인트에 대한 단위 테스트를 수행합니다.
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

class WebLogEndpointTester:
    """웹 로그 엔드포인트 테스터"""
    
    def __init__(self):
        self.base_url = BASE_URL
        self.api_prefix = API_PREFIX
        self.test_results = []
        self.access_token = None
        self.test_data = {
            "requst_id": f"WEB_TEST_{int(time.time())}",
            "rqester_id": "web_test_user",
            "rqester_ip": "192.168.1.200",
            "rqester_nm": "웹테스트사용자",
            "trget_menu_nm": "웹테스트메뉴",
            "process_se_code": "SUCCESS",
            "process_cn": "웹 테스트 처리 내용",
            "process_time": 0.8
        }
    
    def login(self) -> bool:
        """로그인하여 액세스 토큰 획득"""
        login_data = {
            "user_id": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                print(f"🔑 로그인 성공: 토큰 획득")
                return True
            else:
                print(f"❌ 로그인 실패: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 로그인 오류: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """인증 헤더 반환"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
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
    
    def test_create_weblog(self) -> str:
        """1. 웹 로그 생성 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/"
        
        weblog_data = {
            "requst_id": f"WEB_TEST_{int(time.time())}",
            "rqester_id": "web_test_user",
            "rqester_ip": "192.168.1.200",
            "rqester_nm": "웹테스트사용자",
            "trget_menu_nm": "웹테스트메뉴",
            "process_se_code": "SUCCESS",
            "process_cn": "웹 테스트 처리 내용",
            "process_time": 0.8
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                json=weblog_data,
                headers=self.get_headers()
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
                return response.json().get("requst_id")
            return weblog_data["requst_id"]
            
        except Exception as e:
            self.log_test_result(
                "웹 로그 생성",
                endpoint,
                "POST",
                0,
                201,
                error_message=str(e)
            )
            return weblog_data["requst_id"]
    
    def test_get_weblog_list(self):
        """2. 웹 로그 목록 조회 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}?page=1&size=10",
                headers=self.get_headers()
            )
            
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
    
    def test_get_weblog_by_id(self, requst_id: str):
        """3. 웹 로그 상세 조회 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/{requst_id}"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            )
            
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
    
    def test_update_weblog(self, requst_id: str):
        """4. 웹 로그 수정 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/{requst_id}"
        
        update_data = {
            "process_cn": "수정된 웹 처리 내용",
            "process_time": 1.2
        }
        
        try:
            response = requests.put(
                f"{self.base_url}{endpoint}",
                json=update_data,
                headers=self.get_headers()
            )
            
            self.log_test_result(
                "웹 로그 수정",
                endpoint,
                "PUT",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "웹 로그 수정",
                endpoint,
                "PUT",
                0,
                200,
                error_message=str(e)
            )
    
    def test_search_weblogs(self):
        """5. 웹 로그 검색 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/search"
        
        search_params = {
            "rqester_id": "web_test_user",
            "process_se_code": "SUCCESS",
            "page": 1,
            "size": 10
        }
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=search_params,
                headers=self.get_headers()
            )
            
            self.log_test_result(
                "웹 로그 검색",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "웹 로그 검색",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_get_popular_pages(self):
        """6. 인기 페이지 조회 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/popular-pages"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}?days=30&limit=10",
                headers=self.get_headers()
            )
            
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
    
    def test_get_hourly_traffic(self):
        """7. 시간별 트래픽 조회 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/hourly-traffic"
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}?date={today}",
                headers=self.get_headers()
            )
            
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
    
    def test_get_weblog_statistics(self):
        """8. 웹 로그 통계 조회 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/statistics"
        
        try:
            response = requests.get(
                f"{self.base_url}{endpoint}?days=30",
                headers=self.get_headers()
            )
            
            self.log_test_result(
                "웹 로그 통계 조회",
                endpoint,
                "GET",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "웹 로그 통계 조회",
                endpoint,
                "GET",
                0,
                200,
                error_message=str(e)
            )
    
    def test_delete_weblog(self, requst_id: str):
        """9. 웹 로그 삭제 테스트"""
        endpoint = f"{self.api_prefix}/web-logs/{requst_id}"
        
        try:
            response = requests.delete(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers()
            )
            
            self.log_test_result(
                "웹 로그 삭제",
                endpoint,
                "DELETE",
                response.status_code,
                200,
                response.json() if response.status_code == 200 else None,
                response.text if response.status_code != 200 else None
            )
            
        except Exception as e:
            self.log_test_result(
                "웹 로그 삭제",
                endpoint,
                "DELETE",
                0,
                200,
                error_message=str(e)
            )
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("\n🚀 웹 로그 엔드포인트 테스트 시작")
        print("=" * 50)
        
        # 로그인 먼저 수행
        if not self.login():
            print("❌ 로그인 실패로 테스트를 중단합니다.")
            return
        
        # 1. 웹 로그 생성
        requst_id = self.test_create_weblog()
        
        # 2. 웹 로그 목록 조회
        self.test_get_weblog_list()
        
        # 3. 웹 로그 상세 조회
        self.test_get_weblog_by_id(requst_id)
        
        # 4. 웹 로그 수정
        self.test_update_weblog(requst_id)
        
        # 5. 웹 로그 검색
        self.test_search_weblogs()
        
        # 6. 인기 페이지 조회
        self.test_get_popular_pages()
        
        # 7. 시간별 트래픽 조회
        self.test_get_hourly_traffic()
        
        # 8. 웹 로그 통계 조회
        self.test_get_weblog_statistics()
        
        # 9. 웹 로그 삭제
        self.test_delete_weblog(requst_id)
        
        # 결과 요약
        self.print_test_summary()
        
        # 결과를 JSON 파일로 저장
        self.save_test_results()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 50)
        print("📊 웹 로그 엔드포인트 테스트 결과 요약")
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
        filename = f"weblog_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 테스트 결과가 {filename}에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = WebLogEndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
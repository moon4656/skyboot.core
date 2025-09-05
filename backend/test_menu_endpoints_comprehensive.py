#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
메뉴 라우터 엔드포인트 종합 테스트 스크립트

메뉴 관리 API의 모든 엔드포인트를 체계적으로 테스트합니다.
"""

import requests
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime

class MenuEndpointTester:
    """메뉴 엔드포인트 테스터 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.auth_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, response_data: Any = None, error: str = None):
        """테스트 결과를 로깅합니다."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "success": success,
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if error:
            print(f"   Error: {error}")
        if response_data and isinstance(response_data, dict):
            if 'status_code' in response_data:
                print(f"   Status: {response_data['status_code']}")
        print()
    
    def authenticate(self, username: str = "admin", password: str = "admin123") -> bool:
        """인증 토큰을 획득합니다."""
        try:
            auth_data = {
                "user_id": username,
                "password": password
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=auth_data,
                headers=self.headers
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.headers["Authorization"] = f"Bearer {self.auth_token}"
                
                self.log_test(
                    "Authentication", 
                    True, 
                    {"status_code": response.status_code, "token_acquired": bool(self.auth_token)}
                )
                return True
            else:
                self.log_test(
                    "Authentication", 
                    False, 
                    {"status_code": response.status_code}, 
                    f"Login failed: {response.text}"
                )
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, None, str(e))
            return False
    
    def test_get_menus(self):
        """메뉴 목록 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/",
                headers=self.headers,
                params={"skip": 0, "limit": 10}
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("GET /menus/ - 메뉴 목록 조회", success, response_data, 
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("GET /menus/ - 메뉴 목록 조회", False, None, str(e))
    
    def test_get_menu_tree(self):
        """메뉴 트리 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/tree",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("GET /menus/tree - 메뉴 트리 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("GET /menus/tree - 메뉴 트리 조회", False, None, str(e))
    
    def test_get_root_menus(self):
        """루트 메뉴 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/root",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("GET /menus/root - 루트 메뉴 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("GET /menus/root - 루트 메뉴 조회", False, None, str(e))
    
    def test_get_menu_statistics(self):
        """메뉴 통계 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/statistics",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("GET /menus/statistics - 메뉴 통계 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("GET /menus/statistics - 메뉴 통계 조회", False, None, str(e))
    
    def test_create_menu(self) -> Optional[str]:
        """메뉴 생성 테스트"""
        try:
            test_menu_data = {
                "menu_no": f"TEST_MENU_{int(time.time())}",
                "menu_nm": "테스트 메뉴",
                "menu_ty": "MENU",
                "menu_url": "/test",
                "progrm_file_nm": "/test-menu",
                "use_at": "Y",
                "sort_ordr": 1,
                "frst_register_id": "admin"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/menus/",
                json=test_menu_data,
                headers=self.headers
            )
            
            success = response.status_code == 201
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            menu_id = None
            if success:
                menu_id = response.json().get("menu_no")
            
            self.log_test("POST /menus/ - 메뉴 생성", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
            return menu_id
            
        except Exception as e:
            self.log_test("POST /menus/ - 메뉴 생성", False, None, str(e))
            return None
    
    def test_get_menu_detail(self, menu_id: str):
        """메뉴 상세 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/{menu_id}",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test(f"GET /menus/{menu_id} - 메뉴 상세 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test(f"GET /menus/{menu_id} - 메뉴 상세 조회", False, None, str(e))
    
    def test_update_menu(self, menu_id: str):
        """메뉴 수정 테스트"""
        try:
            update_data = {
                "menu_nm": "수정된 테스트 메뉴",
                "menu_url": "/test-updated"
            }
            
            response = requests.put(
                f"{self.base_url}/api/v1/menus/{menu_id}",
                json=update_data,
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test(f"PUT /menus/{menu_id} - 메뉴 수정", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test(f"PUT /menus/{menu_id} - 메뉴 수정", False, None, str(e))
    
    def test_get_child_menus(self, menu_id: str):
        """하위 메뉴 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/{menu_id}/children",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test(f"GET /menus/{menu_id}/children - 하위 메뉴 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test(f"GET /menus/{menu_id}/children - 하위 메뉴 조회", False, None, str(e))
    
    def test_get_menu_breadcrumb(self, menu_id: str):
        """메뉴 경로 조회 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/{menu_id}/breadcrumb",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test(f"GET /menus/{menu_id}/breadcrumb - 메뉴 경로 조회", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test(f"GET /menus/{menu_id}/breadcrumb - 메뉴 경로 조회", False, None, str(e))
    
    def test_validate_menu(self):
        """메뉴 검증 테스트"""
        try:
            validation_data = {
                "menu_no": "VALIDATION_TEST",
                "menu_nm": "검증 테스트 메뉴",
                "menu_ty": "MENU",
                "menu_url": "/validation-test",
                "progrm_file_nm": "/validation-test-menu",
                "use_at": "Y",
                "sort_ordr": 1,
                "frst_register_id": "admin"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/menus/validate",
                json=validation_data,
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("POST /menus/validate - 메뉴 검증", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("POST /menus/validate - 메뉴 검증", False, None, str(e))
    
    def test_export_menu_data(self):
        """메뉴 데이터 내보내기 테스트"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/menus/export/json",
                headers=self.headers,
                params={"format": "json", "include_inactive": False}
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test("GET /menus/export/json - 메뉴 데이터 내보내기", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test("GET /menus/export/json - 메뉴 데이터 내보내기", False, None, str(e))
    
    def test_delete_menu(self, menu_id: str):
        """메뉴 삭제 테스트"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/menus/{menu_id}",
                headers=self.headers
            )
            
            success = response.status_code == 200
            response_data = {
                "status_code": response.status_code,
                "data": response.json() if success else response.text
            }
            
            self.log_test(f"DELETE /menus/{menu_id} - 메뉴 삭제", success, response_data,
                         None if success else f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_test(f"DELETE /menus/{menu_id} - 메뉴 삭제", False, None, str(e))
    
    def run_all_tests(self):
        """모든 테스트를 실행합니다."""
        print("=" * 80)
        print("메뉴 엔드포인트 종합 테스트 시작")
        print("=" * 80)
        print()
        
        # 1. 인증
        if not self.authenticate():
            print("❌ 인증 실패로 테스트를 중단합니다.")
            return
        
        # 2. 기본 조회 테스트
        print("📋 기본 조회 테스트")
        print("-" * 40)
        self.test_get_menus()
        self.test_get_menu_tree()
        self.test_get_root_menus()
        self.test_get_menu_statistics()
        
        # 3. CRUD 테스트
        print("🔧 CRUD 테스트")
        print("-" * 40)
        test_menu_id = self.test_create_menu()
        
        if test_menu_id:
            self.test_get_menu_detail(test_menu_id)
            self.test_update_menu(test_menu_id)
            self.test_get_child_menus(test_menu_id)
            # 메뉴 경로 조회 테스트 (삭제 전에 실행)
            self.test_get_menu_breadcrumb(test_menu_id)
            
            # 삭제는 마지막에
            self.test_delete_menu(test_menu_id)
        
        # 4. 유틸리티 테스트
        print("🛠️ 유틸리티 테스트")
        print("-" * 40)
        self.test_validate_menu()
        self.test_export_menu_data()
        
        # 5. 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약을 출력합니다."""
        print("=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  ❌ {result['test_name']}: {result['error']}")
        
        # 결과를 파일로 저장
        with open(f"menu_test_results_{int(time.time())}.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n상세 결과가 menu_test_results_{int(time.time())}.json 파일에 저장되었습니다.")


def main():
    """메인 함수"""
    tester = MenuEndpointTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
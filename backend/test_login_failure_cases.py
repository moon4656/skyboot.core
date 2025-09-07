#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그인 실패 케이스 단위 테스트

다양한 로그인 실패 시나리오를 테스트합니다.
- 잘못된 사용자 ID
- 잘못된 비밀번호
- 존재하지 않는 사용자
- 비활성화된 사용자 (있는 경우)
- 잘못된 요청 형식
- 필수 필드 누락
"""

import requests
import json
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional

# 테스트 설정
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"

# 실패 테스트 케이스들
FAILURE_TEST_CASES = {
    "wrong_password": {
        "user_id": "admin",
        "password": "wrongpassword123"
    },
    "wrong_user_id": {
        "user_id": "nonexistent_user",
        "password": "admin123"
    },
    "empty_user_id": {
        "user_id": "",
        "password": "admin123"
    },
    "empty_password": {
        "user_id": "admin",
        "password": ""
    },
    "short_password": {
        "user_id": "admin",
        "password": "123"  # 4자 미만
    },
    "null_user_id": {
        "user_id": None,
        "password": "admin123"
    },
    "null_password": {
        "user_id": "admin",
        "password": None
    },
    "special_characters": {
        "user_id": "admin'; DROP TABLE users; --",
        "password": "admin123"
    },
    "very_long_user_id": {
        "user_id": "a" * 1000,  # 매우 긴 사용자 ID
        "password": "admin123"
    },
    "very_long_password": {
        "user_id": "admin",
        "password": "a" * 1000  # 매우 긴 비밀번호
    }
}

class LoginFailureTester:
    """로그인 실패 케이스 테스트 클래스"""
    
    def __init__(self):
        self.test_results = []
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def log_test_result(self, test_name: str, success: bool, details: Dict[str, Any] = None, error: str = None):
        """테스트 결과를 로깅합니다."""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
            "error": error
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"[{status}] {test_name}")
        if details:
            print(f"    Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
        if error:
            print(f"    Error: {error}")
        print()
    
    def test_failure_case(self, case_name: str, test_data: Dict[str, Any], expected_status_codes: list = None):
        """개별 실패 케이스 테스트"""
        if expected_status_codes is None:
            expected_status_codes = [400, 401, 422]  # 일반적인 실패 상태 코드들
        
        try:
            response = self.session.post(LOGIN_URL, json=test_data, timeout=10)
            
            if response.status_code in expected_status_codes:
                try:
                    data = response.json()
                    error_message = data.get("detail", "")
                except:
                    error_message = response.text
                
                self.log_test_result(
                    f"실패 케이스: {case_name}", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "error_message": error_message,
                        "test_data": test_data
                    }
                )
                return True
            else:
                self.log_test_result(
                    f"실패 케이스: {case_name}", 
                    False, 
                    {
                        "status_code": response.status_code,
                        "expected_codes": expected_status_codes,
                        "response": response.text[:200],
                        "test_data": test_data
                    },
                    f"예상된 상태 코드가 아님: {response.status_code}"
                )
                return False
                
        except Exception as e:
            self.log_test_result(
                f"실패 케이스: {case_name}", 
                False, 
                {"test_data": test_data},
                f"테스트 실행 중 오류: {str(e)}"
            )
            return False
    
    def test_malformed_requests(self):
        """잘못된 형식의 요청 테스트"""
        malformed_cases = [
            {
                "name": "missing_user_id",
                "data": {"password": "admin123"},
                "expected_codes": [422]
            },
            {
                "name": "missing_password",
                "data": {"user_id": "admin"},
                "expected_codes": [422]
            },
            {
                "name": "empty_json",
                "data": {},
                "expected_codes": [422]
            },
            {
                "name": "extra_fields",
                "data": {
                    "user_id": "admin",
                    "password": "admin123",
                    "extra_field": "should_be_ignored"
                },
                "expected_codes": [200, 400, 401]  # 추가 필드는 무시될 수 있음
            }
        ]
        
        for case in malformed_cases:
            self.test_failure_case(
                case["name"], 
                case["data"], 
                case["expected_codes"]
            )
    
    def test_invalid_json(self):
        """잘못된 JSON 형식 테스트"""
        try:
            # 잘못된 JSON 전송
            response = self.session.post(
                LOGIN_URL, 
                data="{invalid json}",  # 잘못된 JSON
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code in [400, 422]:
                self.log_test_result(
                    "잘못된 JSON 형식", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    }
                )
            else:
                self.log_test_result(
                    "잘못된 JSON 형식", 
                    False, 
                    {"status_code": response.status_code},
                    f"예상된 400/422 상태 코드가 아님: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "잘못된 JSON 형식", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def test_content_type_errors(self):
        """잘못된 Content-Type 테스트"""
        try:
            # 잘못된 Content-Type으로 요청
            response = self.session.post(
                LOGIN_URL,
                data="user_id=admin&password=admin123",  # form data
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=10
            )
            
            if response.status_code in [400, 422, 415]:  # 415: Unsupported Media Type
                self.log_test_result(
                    "잘못된 Content-Type", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "response": response.text[:200]
                    }
                )
            else:
                self.log_test_result(
                    "잘못된 Content-Type", 
                    False, 
                    {"status_code": response.status_code},
                    f"예상된 오류 상태 코드가 아님: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "잘못된 Content-Type", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def run_all_failure_tests(self):
        """모든 실패 케이스 테스트 실행"""
        print("=" * 60)
        print("로그인 실패 케이스 단위 테스트 시작")
        print(f"테스트 대상: {LOGIN_URL}")
        print("=" * 60)
        print()
        
        # 1. 기본 실패 케이스들
        print("📋 기본 실패 케이스 테스트")
        print("-" * 30)
        for case_name, test_data in FAILURE_TEST_CASES.items():
            self.test_failure_case(case_name, test_data)
        
        # 2. 잘못된 형식 요청 테스트
        print("📋 잘못된 형식 요청 테스트")
        print("-" * 30)
        self.test_malformed_requests()
        
        # 3. 잘못된 JSON 테스트
        print("📋 잘못된 JSON 형식 테스트")
        print("-" * 30)
        self.test_invalid_json()
        
        # 4. 잘못된 Content-Type 테스트
        print("📋 잘못된 Content-Type 테스트")
        print("-" * 30)
        self.test_content_type_errors()
        
        # 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {success_rate:.1f}%")
        print()
        
        if failed_tests > 0:
            print("❌ 실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result.get('error', 'Unknown error')}")
            print()
        
        print("상세 결과는 위의 로그를 참조하세요.")
        print("=" * 60)
        
        # 결과를 JSON 파일로 저장
        with open('login_failure_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        print("테스트 결과가 'login_failure_test_results.json' 파일에 저장되었습니다.")

def main():
    """메인 함수"""
    tester = LoginFailureTester()
    tester.run_all_failure_tests()

if __name__ == "__main__":
    main()
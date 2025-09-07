#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그인 기능 단위 테스트

/api/v1/auth/login 엔드포인트의 기능을 검증합니다.
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
REFRESH_URL = f"{BASE_URL}/api/v1/auth/refresh"

# 테스트 사용자 정보
TEST_USERS = {
    "valid_user": {
        "user_id": "admin",
        "password": "admin123"
    },
    "invalid_user": {
        "user_id": "invalid_user",
        "password": "wrong_password"
    },
    "empty_password": {
        "user_id": "admin",
        "password": ""
    }
}

class LoginTester:
    """로그인 기능 테스트 클래스"""
    
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
    
    def test_valid_login(self) -> Optional[Dict[str, Any]]:
        """유효한 사용자 정보로 로그인 테스트"""
        try:
            user_data = TEST_USERS["valid_user"]
            response = self.session.post(LOGIN_URL, json=user_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # 응답 데이터 검증
                required_fields = ["access_token", "refresh_token", "token_type", "expires_in", "user_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        "Valid Login Test", 
                        False, 
                        {"missing_fields": missing_fields, "response": data},
                        f"응답에 필수 필드가 누락됨: {missing_fields}"
                    )
                    return None
                
                # 토큰 형식 검증
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")
                
                if not access_token or len(access_token.split('.')) != 3:
                    self.log_test_result(
                        "Valid Login Test", 
                        False, 
                        {"access_token_format": "invalid"},
                        "액세스 토큰 형식이 올바르지 않음"
                    )
                    return None
                
                if not refresh_token or len(refresh_token.split('.')) != 3:
                    self.log_test_result(
                        "Valid Login Test", 
                        False, 
                        {"refresh_token_format": "invalid"},
                        "리프레시 토큰 형식이 올바르지 않음"
                    )
                    return None
                
                self.log_test_result(
                    "Valid Login Test", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "token_type": data.get("token_type"),
                        "expires_in": data.get("expires_in"),
                        "user_id": data.get("user_info", {}).get("user_id"),
                        "access_token_length": len(access_token),
                        "refresh_token_length": len(refresh_token)
                    }
                )
                return data
            else:
                self.log_test_result(
                    "Valid Login Test", 
                    False, 
                    {"status_code": response.status_code, "response": response.text},
                    f"로그인 실패: HTTP {response.status_code}"
                )
                return None
                
        except Exception as e:
            self.log_test_result(
                "Valid Login Test", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
            return None
    
    def test_invalid_login(self):
        """잘못된 사용자 정보로 로그인 테스트"""
        try:
            user_data = TEST_USERS["invalid_user"]
            response = self.session.post(LOGIN_URL, json=user_data)
            
            if response.status_code == 401:
                data = response.json()
                self.log_test_result(
                    "Invalid Login Test", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "error_message": data.get("detail", "")
                    }
                )
            else:
                self.log_test_result(
                    "Invalid Login Test", 
                    False, 
                    {"status_code": response.status_code, "response": response.text},
                    f"예상된 401 상태 코드가 아님: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Invalid Login Test", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def test_empty_password_login(self):
        """빈 비밀번호로 로그인 테스트"""
        try:
            user_data = TEST_USERS["empty_password"]
            response = self.session.post(LOGIN_URL, json=user_data)
            
            if response.status_code in [400, 422]:  # 유효성 검사 오류
                data = response.json()
                self.log_test_result(
                    "Empty Password Test", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "error_message": data.get("detail", "")
                    }
                )
            else:
                self.log_test_result(
                    "Empty Password Test", 
                    False, 
                    {"status_code": response.status_code, "response": response.text},
                    f"예상된 400/422 상태 코드가 아님: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Empty Password Test", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def test_token_refresh(self, login_data: Dict[str, Any]):
        """토큰 갱신 테스트"""
        try:
            refresh_token = login_data.get("refresh_token")
            if not refresh_token:
                self.log_test_result(
                    "Token Refresh Test", 
                    False, 
                    {},
                    "리프레시 토큰이 없음"
                )
                return
            
            refresh_data = {"refresh_token": refresh_token}
            response = self.session.post(REFRESH_URL, json=refresh_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # 응답 데이터 검증
                required_fields = ["access_token", "token_type", "expires_in"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result(
                        "Token Refresh Test", 
                        False, 
                        {"missing_fields": missing_fields, "response": data},
                        f"응답에 필수 필드가 누락됨: {missing_fields}"
                    )
                    return
                
                self.log_test_result(
                    "Token Refresh Test", 
                    True, 
                    {
                        "status_code": response.status_code,
                        "token_type": data.get("token_type"),
                        "expires_in": data.get("expires_in"),
                        "new_access_token_length": len(data.get("access_token", ""))
                    }
                )
            else:
                self.log_test_result(
                    "Token Refresh Test", 
                    False, 
                    {"status_code": response.status_code, "response": response.text},
                    f"토큰 갱신 실패: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Token Refresh Test", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def test_malformed_request(self):
        """잘못된 형식의 요청 테스트"""
        try:
            # JSON이 아닌 데이터 전송
            response = self.session.post(LOGIN_URL, data="invalid json")
            
            if response.status_code in [400, 422]:
                self.log_test_result(
                    "Malformed Request Test", 
                    True, 
                    {"status_code": response.status_code}
                )
            else:
                self.log_test_result(
                    "Malformed Request Test", 
                    False, 
                    {"status_code": response.status_code, "response": response.text},
                    f"예상된 400/422 상태 코드가 아님: {response.status_code}"
                )
                
        except Exception as e:
            self.log_test_result(
                "Malformed Request Test", 
                False, 
                {},
                f"테스트 실행 중 오류: {str(e)}"
            )
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=" * 60)
        print("로그인 기능 단위 테스트 시작")
        print(f"테스트 대상: {LOGIN_URL}")
        print("=" * 60)
        print()
        
        # 1. 유효한 로그인 테스트
        login_data = self.test_valid_login()
        
        # 2. 토큰 갱신 테스트 (유효한 로그인이 성공한 경우에만)
        if login_data:
            self.test_token_refresh(login_data)
        
        # 3. 잘못된 로그인 테스트
        self.test_invalid_login()
        
        # 4. 빈 비밀번호 테스트
        self.test_empty_password_login()
        
        # 5. 잘못된 형식 요청 테스트
        self.test_malformed_request()
        
        # 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약 출력"""
        print("=" * 60)
        print("테스트 결과 요약")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
        print()
        
        if failed_tests > 0:
            print("실패한 테스트:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['error']}")
            print()
        
        print("상세 결과는 위의 로그를 참조하세요.")
        print("=" * 60)

def main():
    """메인 함수"""
    try:
        tester = LoginTester()
        tester.run_all_tests()
        
        # 테스트 결과를 파일로 저장
        with open('login_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(tester.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"테스트 결과가 'login_test_results.json' 파일에 저장되었습니다.")
        
    except KeyboardInterrupt:
        print("\n테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"테스트 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
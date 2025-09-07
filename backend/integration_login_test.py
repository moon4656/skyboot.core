#!/usr/bin/env python3
"""
로그인 기능 통합 테스트

전체 로그인 플로우에 대한 종합적인 테스트를 수행합니다.
- 사용자 인증
- JWT 토큰 발급 및 검증
- 토큰 갱신
- 보호된 엔드포인트 접근
- 로그 기록 확인
"""

import requests
import json
import time
from datetime import datetime
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.log_models import LoginLog
from sqlalchemy.orm import Session

# 테스트 설정
BASE_URL = "http://localhost:8000/api/v1"
TEST_USER = {
    "user_id": "admin",
    "password": "admin123"
}

class LoginIntegrationTest:
    """
    로그인 기능 통합 테스트 클래스
    """
    
    def __init__(self):
        self.base_url = BASE_URL
        self.test_results = []
        self.access_token = None
        self.refresh_token = None
        
    def log_test(self, test_name: str, success: bool, details: dict = None, error: str = None):
        """
        테스트 결과를 로깅합니다.
        """
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
        
    def test_1_user_login(self):
        """
        테스트 1: 사용자 로그인
        """
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=TEST_USER,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                
                self.log_test("User Login", True, {
                    "status_code": response.status_code,
                    "token_type": data.get("token_type"),
                    "expires_in": data.get("expires_in"),
                    "user_id": data.get("user_info", {}).get("user_id"),
                    "access_token_received": bool(self.access_token),
                    "refresh_token_received": bool(self.refresh_token)
                })
                return True
            else:
                self.log_test("User Login", False, {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("User Login", False, error=str(e))
            return False
            
    def test_2_token_validation(self):
        """
        테스트 2: 토큰 검증 (보호된 엔드포인트 접근)
        """
        if not self.access_token:
            self.log_test("Token Validation", False, error="No access token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # 사용자 정보 조회 엔드포인트 테스트 (올바른 엔드포인트 사용)
            response = requests.get(
                f"{self.base_url}/users/profile",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Token Validation", True, {
                    "status_code": response.status_code,
                    "user_id": data.get("user_id"),
                    "endpoint_accessed": "/users/profile"
                })
                return True
            else:
                self.log_test("Token Validation", False, {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Token Validation", False, error=str(e))
            return False
            
    def test_3_token_refresh(self):
        """
        테스트 3: 토큰 갱신
        """
        if not self.refresh_token:
            self.log_test("Token Refresh", False, error="No refresh token available")
            return False
            
        try:
            response = requests.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self.refresh_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                new_access_token = data.get("access_token")
                
                self.log_test("Token Refresh", True, {
                    "status_code": response.status_code,
                    "token_type": data.get("token_type"),
                    "expires_in": data.get("expires_in"),
                    "new_token_received": bool(new_access_token),
                    "token_different": new_access_token != self.access_token
                })
                
                # 새 토큰으로 업데이트
                self.access_token = new_access_token
                return True
            else:
                self.log_test("Token Refresh", False, {
                    "status_code": response.status_code,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Token Refresh", False, error=str(e))
            return False
            
    def test_4_invalid_token_access(self):
        """
        테스트 4: 잘못된 토큰으로 접근 시도
        """
        try:
            headers = {"Authorization": "Bearer invalid_token_12345"}
            
            response = requests.get(
                f"{self.base_url}/users/profile",
                headers=headers,
                timeout=10
            )
            
            # 401 Unauthorized가 예상되는 결과
            if response.status_code == 401:
                self.log_test("Invalid Token Access", True, {
                    "status_code": response.status_code,
                    "expected_behavior": "401 Unauthorized"
                })
                return True
            else:
                self.log_test("Invalid Token Access", False, {
                    "status_code": response.status_code,
                    "expected": 401,
                    "response": response.text
                })
                return False
                
        except Exception as e:
            self.log_test("Invalid Token Access", False, error=str(e))
            return False
            
    def test_5_login_log_verification(self):
        """
        테스트 5: 로그인 로그 기록 확인
        """
        try:
            db = next(get_db())
            
            # 최근 로그인 로그 조회 (올바른 필드명 사용)
            recent_logs = db.query(LoginLog).filter(
                LoginLog.conect_id == TEST_USER["user_id"]
            ).order_by(LoginLog.frst_regist_pnttm.desc()).limit(5).all()
            
            if recent_logs:
                latest_log = recent_logs[0]
                self.log_test("Login Log Verification", True, {
                    "logs_found": len(recent_logs),
                    "latest_log_id": latest_log.log_id,
                    "latest_login_time": latest_log.frst_regist_pnttm.isoformat() if latest_log.frst_regist_pnttm else None,
                    "user_id": latest_log.conect_id,
                    "connection_ip": latest_log.conect_ip,
                    "connection_method": latest_log.conect_mthd
                })
                return True
            else:
                self.log_test("Login Log Verification", False, {
                    "logs_found": 0,
                    "message": "No login logs found for user"
                })
                return False
                
        except Exception as e:
            self.log_test("Login Log Verification", False, error=str(e))
            return False
        finally:
            if 'db' in locals():
                db.close()
                
    def test_6_multiple_login_attempts(self):
        """
        테스트 6: 다중 로그인 시도 (부하 테스트)
        """
        success_count = 0
        total_attempts = 3
        
        try:
            for i in range(total_attempts):
                response = requests.post(
                    f"{self.base_url}/auth/login",
                    json=TEST_USER,
                    timeout=10
                )
                
                if response.status_code == 200:
                    success_count += 1
                    
                time.sleep(0.5)  # 0.5초 간격
                
            success_rate = (success_count / total_attempts) * 100
            
            self.log_test("Multiple Login Attempts", success_rate >= 80, {
                "total_attempts": total_attempts,
                "successful_logins": success_count,
                "success_rate": f"{success_rate:.1f}%",
                "threshold": "80%"
            })
            
            return success_rate >= 80
            
        except Exception as e:
            self.log_test("Multiple Login Attempts", False, error=str(e))
            return False
            
    def run_all_tests(self):
        """
        모든 테스트를 실행합니다.
        """
        print("=" * 80)
        print("로그인 기능 통합 테스트 시작")
        print(f"테스트 대상: {self.base_url}")
        print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # 테스트 실행
        tests = [
            self.test_1_user_login,
            self.test_2_token_validation,
            self.test_3_token_refresh,
            self.test_4_invalid_token_access,
            self.test_5_login_log_verification,
            self.test_6_multiple_login_attempts
        ]
        
        passed_tests = 0
        for test in tests:
            if test():
                passed_tests += 1
                
        # 결과 요약
        print("=" * 80)
        print("통합 테스트 결과 요약")
        print("=" * 80)
        print(f"총 테스트: {len(tests)}")
        print(f"성공: {passed_tests}")
        print(f"실패: {len(tests) - passed_tests}")
        print(f"성공률: {(passed_tests / len(tests)) * 100:.1f}%")
        print()
        
        if passed_tests == len(tests):
            print("🎉 모든 통합 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 상세 로그를 확인하세요.")
            
        print("=" * 80)
        
        # 결과를 JSON 파일로 저장
        with open("integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "test_summary": {
                    "total_tests": len(tests),
                    "passed_tests": passed_tests,
                    "failed_tests": len(tests) - passed_tests,
                    "success_rate": f"{(passed_tests / len(tests)) * 100:.1f}%",
                    "test_time": datetime.now().isoformat()
                },
                "detailed_results": self.test_results
            }, f, indent=2, ensure_ascii=False)
            
        print("테스트 결과가 'integration_test_results.json' 파일에 저장되었습니다.")
        
        return passed_tests == len(tests)

def main():
    """
    메인 함수
    """
    tester = LoginIntegrationTest()
    success = tester.run_all_tests()
    
    # 종료 코드 설정
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
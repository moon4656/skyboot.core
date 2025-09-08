#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
user_router.py 전용 테스트 스크립트

이 스크립트는 user_router.py의 모든 엔드포인트를 체계적으로 테스트하고
상세한 리포트를 생성합니다.
"""

import json
import requests
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
import os

class UserRouterTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        self.bearer_token = None
        self.test_results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = f"user_router_test_report_{self.timestamp}.md"
        
        # 테스트용 사용자 데이터 (고유 ID 생성 - 20자 제한)
        self.unique_suffix = self.timestamp[-6:]  # 마지막 6자리만 사용 (HHMMSS)
        unique_id = f"test_{self.unique_suffix}"
        self.test_user_data = {
            "user_id": unique_id,
            "password": "testpass123",
            "user_nm": "테스트사용자",
            "email_adres": f"test_{self.timestamp}@example.com",
            "orgnzt_id": "ORG001",
            "emplyr_sttus_code": "1"  # 필수 필드 추가
        }
        
        # 관리자 계정 정보
        self.admin_data = {
            "user_id": "admin",
            "password": "admin123"
        }
    
    def log_test_result(self, test_name: str, method: str, endpoint: str, 
                       status_code: int, success: bool, response_data: Any = None, 
                       error_message: str = None, execution_time: float = 0):
        """테스트 결과를 로깅합니다."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "success": success,
            "execution_time": execution_time,
            "response_data": response_data,
            "error_message": error_message
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name} | {method} {endpoint} | {status_code} | {execution_time:.3f}s")
        if error_message:
            print(f"    Error: {error_message}")
    
    def test_one_click_login(self) -> bool:
        """원클릭 로그인 테스트 (인증 없는 엔드포인트)"""
        print("\n=== 원클릭 로그인 테스트 ===")
        
        endpoint = "/api/v1/users/one-click-login"
        url = f"{self.base_url}{endpoint}"
        
        # 1. 정상 로그인 테스트
        start_time = time.time()
        try:
            response = self.session.post(url, json=self.admin_data)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.bearer_token = data.get("access_token")
                self.log_test_result(
                    "원클릭 로그인 - 정상", "POST", endpoint, 
                    response.status_code, True, data, None, execution_time
                )
                return True
            else:
                self.log_test_result(
                    "원클릭 로그인 - 정상", "POST", endpoint,
                    response.status_code, False, None, response.text, execution_time
                )
                return False
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test_result(
                "원클릭 로그인 - 정상", "POST", endpoint,
                0, False, None, str(e), execution_time
            )
            return False
        
        # 2. 잘못된 비밀번호 테스트
        start_time = time.time()
        try:
            wrong_data = {"user_id": "admin", "password": "wrongpass"}
            response = self.session.post(url, json=wrong_data)
            execution_time = time.time() - start_time
            
            success = response.status_code == 401
            self.log_test_result(
                "원클릭 로그인 - 잘못된 비밀번호", "POST", endpoint,
                response.status_code, success, None, 
                None if success else "Expected 401 status", execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test_result(
                "원클릭 로그인 - 잘못된 비밀번호", "POST", endpoint,
                0, False, None, str(e), execution_time
            )
    
    def test_bearer_auth_endpoints(self):
        """HTTPBearer 인증 엔드포인트 테스트"""
        print("\n=== HTTPBearer 인증 엔드포인트 테스트 ===")
        
        if not self.bearer_token:
            print("❌ Bearer 토큰이 없습니다. 로그인을 먼저 수행하세요.")
            return
        
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        
        # 1. 내 프로필 조회
        self._test_endpoint(
            "내 프로필 조회", "GET", "/api/v1/users/profile", headers=headers
        )
        
        # 2. 내 프로필 수정
        update_data = {"user_nm": "수정된사용자명"}
        self._test_endpoint(
            "내 프로필 수정", "PUT", "/api/v1/users/profile", 
            headers=headers, json_data=update_data
        )
        
        # 3. 사용자 목록 조회 (관리자)
        self._test_endpoint(
            "사용자 목록 조회 (관리자)", "GET", "/api/v1/users/list", 
            headers=headers, params={"skip": 0, "limit": 10}
        )
        
        # 4. 사용자 검색 (관리자)
        self._test_endpoint(
            "사용자 검색 (관리자)", "GET", "/api/v1/users/search", 
            headers=headers, params={"query": "admin"}
        )
    
    def test_jwt_auth_endpoints(self):
        """기존 JWT 인증 엔드포인트 테스트"""
        print("\n=== 기존 JWT 인증 엔드포인트 테스트 ===")
        
        # JWT 토큰 획득 (기존 auth 엔드포인트 사용)
        auth_url = f"{self.base_url}/api/v1/auth/login"
        try:
            response = self.session.post(auth_url, json=self.admin_data)
            if response.status_code == 200:
                self.access_token = response.json().get("access_token")
                print(f"✅ JWT 토큰 획득 성공")
            else:
                print(f"❌ JWT 토큰 획득 실패: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ JWT 토큰 획득 오류: {str(e)}")
            return
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # 1. 사용자 생성 (관리자용)
        print(f"DEBUG: 전송할 사용자 데이터: {self.test_user_data}")
        self._test_endpoint(
            "사용자 생성 (관리자용)", "POST", "/api/v1/users/admin/create",
            headers=headers, json_data=self.test_user_data
        )
        
        # 2. 사용자 기본 자료 생성
        basic_data = {
            "user_id": f"basic_{self.unique_suffix}",
            "user_nm": "기본사용자",
            "password": "basicpass123"
        }
        self._test_endpoint(
            "사용자 기본 자료 생성", "POST", "/api/v1/users/basic",
            headers=headers, json_data=basic_data
        )
        
        # 3. 사용자 목록 조회
        self._test_endpoint(
            "사용자 목록 조회", "GET", "/api/v1/users/",
            headers=headers, params={"skip": 0, "limit": 10}
        )
        
        # 4. 사용자 통계
        self._test_endpoint(
            "사용자 통계", "GET", "/api/v1/users/statistics",
            headers=headers
        )
        
        # 5. 특정 사용자 조회
        self._test_endpoint(
            "특정 사용자 조회", "GET", f"/api/v1/users/{self.test_user_data['user_id']}",
            headers=headers
        )
        
        # 6. 사용자 정보 수정
        update_data = {"user_nm": "수정된테스트사용자"}
        self._test_endpoint(
            "사용자 정보 수정", "PUT", f"/api/v1/users/{self.test_user_data['user_id']}",
            headers=headers, json_data=update_data
        )
        
        # 7. 사용자 계정 잠금
        self._test_endpoint(
            "사용자 계정 잠금", "POST", f"/api/v1/users/{self.test_user_data['user_id']}/lock",
            headers=headers
        )
        
        # 8. 사용자 계정 잠금 해제
        self._test_endpoint(
            "사용자 계정 잠금 해제", "POST", f"/api/v1/users/{self.test_user_data['user_id']}/unlock",
            headers=headers
        )
        
        # 9. 사용자 삭제
        self._test_endpoint(
            "사용자 삭제", "DELETE", f"/api/v1/users/{self.test_user_data['user_id']}",
            headers=headers
        )
    
    def test_error_handling(self):
        """에러 처리 및 예외 상황 테스트"""
        print("\n=== 에러 처리 및 예외 상황 테스트 ===")
        
        # 1. 인증 없이 보호된 엔드포인트 접근
        self._test_endpoint(
            "인증 없이 프로필 조회", "GET", "/api/v1/users/profile",
            expected_status=401
        )
        
        # 2. 잘못된 토큰으로 접근
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        self._test_endpoint(
            "잘못된 토큰으로 프로필 조회", "GET", "/api/v1/users/profile",
            headers=invalid_headers, expected_status=401
        )
        
        # 3. 존재하지 않는 사용자 조회
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            self._test_endpoint(
                "존재하지 않는 사용자 조회", "GET", "/api/v1/users/nonexistent_user",
                headers=headers, expected_status=404
            )
        
        # 4. 잘못된 데이터로 사용자 생성
        if self.access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            invalid_data = {"user_id": "", "password": "123"}  # 빈 user_id, 짧은 password
            self._test_endpoint(
                "잘못된 데이터로 사용자 생성", "POST", "/api/v1/users/admin/create",
                headers=headers, json_data=invalid_data, expected_status=422
            )
    
    def _test_endpoint(self, test_name: str, method: str, endpoint: str, 
                      headers: Dict = None, json_data: Dict = None, 
                      params: Dict = None, expected_status: int = None):
        """개별 엔드포인트 테스트 헬퍼 메서드"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method == "POST":
                response = self.session.post(url, headers=headers, json=json_data)
            elif method == "PUT":
                response = self.session.put(url, headers=headers, json=json_data)
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            execution_time = time.time() - start_time
            
            # 성공 여부 판단
            if expected_status:
                success = response.status_code == expected_status
            else:
                success = 200 <= response.status_code < 300
            
            # 응답 데이터 파싱
            try:
                response_data = response.json() if response.content else None
            except:
                response_data = response.text
            
            error_message = None if success else f"Unexpected status: {response.status_code}"
            
            # 422 에러 시 상세 정보 출력
            if response.status_code == 422:
                print(f"DEBUG: 422 에러 응답 내용: {response_data}")
                error_message = f"Validation error: {response_data}"
            
            self.log_test_result(
                test_name, method, endpoint, response.status_code, 
                success, response_data, error_message, execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_test_result(
                test_name, method, endpoint, 0, False, None, str(e), execution_time
            )
    
    def generate_report(self):
        """상세한 테스트 리포트 생성"""
        print(f"\n=== 테스트 리포트 생성 중... ===")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report_content = f"""# User Router 테스트 리포트

**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**테스트 대상**: user_router.py
**서버 URL**: {self.base_url}

## 📊 테스트 요약

- **총 테스트 수**: {total_tests}
- **성공**: {passed_tests}
- **실패**: {failed_tests}
- **성공률**: {success_rate:.1f}%

## 📋 엔드포인트 분류

### 1. 인증 없는 엔드포인트
- `POST /api/v1/users/one-click-login` - 원클릭 로그인

### 2. HTTPBearer 인증 엔드포인트
- `GET /api/v1/users/profile` - 내 프로필 조회
- `PUT /api/v1/users/profile` - 내 프로필 수정
- `GET /api/v1/users/list` - 사용자 목록 조회 (관리자)
- `GET /api/v1/users/search` - 사용자 검색 (관리자)

### 3. 기존 JWT 인증 엔드포인트
- `POST /api/v1/users/admin/create` - 사용자 생성 (관리자용)
- `POST /api/v1/users/basic` - 사용자 기본 자료 생성
- `GET /api/v1/users/` - 사용자 목록 조회
- `GET /api/v1/users/statistics` - 사용자 통계
- `GET /api/v1/users/{{user_id}}` - 사용자 상세 조회
- `PUT /api/v1/users/{{user_id}}` - 사용자 정보 수정
- `DELETE /api/v1/users/{{user_id}}` - 사용자 삭제
- `POST /api/v1/users/{{user_id}}/lock` - 사용자 계정 잠금
- `POST /api/v1/users/{{user_id}}/unlock` - 사용자 계정 잠금 해제

## 🔍 상세 테스트 결과

"""
        
        for i, result in enumerate(self.test_results, 1):
            status_icon = "✅" if result["success"] else "❌"
            report_content += f"""### {i}. {result['test_name']}

- **상태**: {status_icon} {'성공' if result['success'] else '실패'}
- **메서드**: {result['method']}
- **엔드포인트**: {result['endpoint']}
- **응답 코드**: {result['status_code']}
- **실행 시간**: {result['execution_time']:.3f}초
- **실행 시각**: {result['timestamp']}

"""
            
            if result["error_message"]:
                report_content += f"**오류 메시지**: {result['error_message']}\n\n"
            
            if result["response_data"] and result["success"]:
                # 응답 데이터가 너무 길면 요약
                response_str = str(result["response_data"])
                if len(response_str) > 500:
                    response_str = response_str[:500] + "..."
                report_content += f"**응답 데이터**: ```json\n{response_str}\n```\n\n"
            
            report_content += "---\n\n"
        
        # 발견된 문제점 및 개선사항
        report_content += """## 🚨 발견된 문제점

"""
        
        issues_found = []
        for result in self.test_results:
            if not result["success"]:
                issues_found.append(f"- **{result['test_name']}**: {result['error_message']}")
        
        if issues_found:
            report_content += "\n".join(issues_found) + "\n\n"
        else:
            report_content += "발견된 문제점이 없습니다.\n\n"
        
        report_content += """## 💡 개선 권장사항

1. **에러 응답 표준화**: 모든 에러 응답이 일관된 형식을 따르는지 확인
2. **입력 검증 강화**: 사용자 입력에 대한 더 엄격한 검증 로직 추가
3. **로깅 개선**: 각 엔드포인트의 요청/응답 로깅 강화
4. **성능 최적화**: 응답 시간이 긴 엔드포인트에 대한 최적화 검토
5. **보안 강화**: 인증/인가 로직의 보안성 재검토

## 📈 성능 분석

"""
        
        # 성능 통계
        execution_times = [r["execution_time"] for r in self.test_results if r["execution_time"] > 0]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            
            report_content += f"""- **평균 응답 시간**: {avg_time:.3f}초
- **최대 응답 시간**: {max_time:.3f}초
- **최소 응답 시간**: {min_time:.3f}초

"""
        
        report_content += """## 🎯 결론

"""
        
        if success_rate >= 90:
            report_content += "✅ **우수**: 대부분의 테스트가 성공적으로 통과했습니다.\n"
        elif success_rate >= 70:
            report_content += "⚠️ **양호**: 일부 개선이 필요하지만 전반적으로 안정적입니다.\n"
        else:
            report_content += "❌ **개선 필요**: 다수의 문제점이 발견되어 즉시 수정이 필요합니다.\n"
        
        report_content += f"\n전체 {total_tests}개 테스트 중 {passed_tests}개가 성공하여 {success_rate:.1f}%의 성공률을 기록했습니다.\n"
        
        # 리포트 파일 저장
        with open(self.report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 테스트 리포트가 생성되었습니다: {self.report_file}")
        print(f"📊 테스트 결과: {passed_tests}/{total_tests} 성공 ({success_rate:.1f}%)")
        
        return self.report_file
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 User Router 테스트 시작...")
        print(f"서버 URL: {self.base_url}")
        print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 1. 인증 없는 엔드포인트 테스트
        self.test_one_click_login()
        
        # 2. HTTPBearer 인증 엔드포인트 테스트
        self.test_bearer_auth_endpoints()
        
        # 3. 기존 JWT 인증 엔드포인트 테스트
        self.test_jwt_auth_endpoints()
        
        # 4. 에러 처리 테스트
        self.test_error_handling()
        
        # 5. 리포트 생성
        report_file = self.generate_report()
        
        print(f"\n🎉 모든 테스트가 완료되었습니다!")
        print(f"📄 상세 리포트: {report_file}")
        
        return report_file

if __name__ == "__main__":
    tester = UserRouterTester()
    tester.run_all_tests()
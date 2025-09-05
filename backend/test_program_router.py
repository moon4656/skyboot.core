#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Router 엔드포인트 테스트 스크립트

program_router.py의 모든 엔드포인트를 단계적으로 테스트합니다.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

import httpx
from httpx import AsyncClient

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/programs"
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


class ProgramRouterTester:
    """Program Router 테스트 클래스"""
    
    def __init__(self):
        self.client = None
        self.headers = {}
        # 테스트 데이터 설정 (고유한 프로그램명 사용)
        import time
        timestamp = str(int(time.time()))
        self.test_data = {
            "create_program": {
                "progrm_nm": f"test_program_{timestamp}",  # 스키마에서 필수 필드
                "progrm_file_nm": f"test_program_{timestamp}.exe",
                "progrm_stre_path": "/test/path",
                "progrm_korean_nm": "테스트 프로그램",
                "progrm_dc": "테스트용 프로그램입니다",
                "url": "http://test.example.com"
            },
            "update_program": {
                "progrm_nm": "updated_test_program",  # 스키마에서 필수 필드
                "progrm_stre_path": "/updated/path",
                "progrm_korean_nm": "수정된 테스트 프로그램",
                "progrm_dc": "수정된 테스트용 프로그램입니다",
                "url": "http://updated.example.com"
            }
        }
    
    async def setup(self):
        """테스트 환경 설정"""
        self.client = AsyncClient(base_url=BASE_URL, timeout=TEST_TIMEOUT)
        
        # JWT 토큰 획득 시도
        await self.get_auth_token()
        
        if TEST_TOKEN:
            self.headers["Authorization"] = f"Bearer {TEST_TOKEN}"
        
        print(f"🔧 테스트 환경 설정 완료")
        print(f"📍 Base URL: {BASE_URL}")
        print(f"🔑 인증 토큰: {'설정됨' if TEST_TOKEN else '없음'}")
        print("-" * 60)
    
    async def get_auth_token(self):
        """인증 토큰 획득"""
        global TEST_TOKEN
        try:
            # 테스트용 사용자로 로그인 시도
            login_data = {
                "user_id": "admin",  # 기본 관리자 계정
                "password": "admin123"  # 기본 비밀번호
            }
            
            response = await self.client.post("/api/v1/auth/login", json=login_data)
            print(f"🔍 로그인 시도 - 상태코드: {response.status_code}")
            print(f"🔍 로그인 응답: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                TEST_TOKEN = result.get("access_token")
                print(f"✅ 인증 토큰 획득 성공")
                print(f"🔑 토큰: {TEST_TOKEN[:50]}..." if TEST_TOKEN else "토큰 없음")
            else:
                print(f"⚠️ 인증 토큰 획득 실패: {response.status_code}")
                print(f"응답: {response.text}")
        except Exception as e:
            print(f"❌ 인증 토큰 획득 중 오류: {str(e)}")
    
    async def cleanup(self):
        """테스트 환경 정리"""
        if self.client:
            await self.client.aclose()
        print(f"🧹 테스트 환경 정리 완료")
    
    def log_test_result(self, test_name: str, success: bool, 
                       response_data: Optional[Dict] = None, 
                       error_message: Optional[str] = None,
                       status_code: Optional[int] = None):
        """테스트 결과 로깅"""
        global test_summary
        
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "status_code": status_code,
            "response_data": response_data,
            "error_message": error_message
        }
        
        test_results.append(result)
        test_summary["total_tests"] += 1
        
        if success:
            test_summary["passed"] += 1
            print(f"✅ {test_name} - 성공 (상태코드: {status_code})")
        else:
            test_summary["failed"] += 1
            test_summary["errors"].append({
                "test_name": test_name,
                "error": error_message,
                "status_code": status_code
            })
            print(f"❌ {test_name} - 실패")
            if error_message:
                print(f"   오류: {error_message}")
            if status_code:
                print(f"   상태코드: {status_code}")
    
    async def test_create_program(self):
        """프로그램 생성 테스트"""
        test_name = "프로그램 생성 (POST /programs)"
        try:
            response = await self.client.post(
                f"{API_PREFIX}/",
                json=self.test_data["create_program"],
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False, 
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def test_get_programs(self):
        """프로그램 목록 조회 테스트"""
        test_name = "프로그램 목록 조회 (GET /programs)"
        try:
            response = await self.client.get(
                f"{API_PREFIX}/?skip=0&limit=10",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False,
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def test_search_programs(self):
        """프로그램 검색 테스트"""
        test_name = "프로그램 검색 (GET /programs/search)"
        try:
            params = {
                "progrm_korean_nm": "테스트",
                "skip": 0,
                "limit": 10
            }
            
            response = await self.client.get(
                f"{API_PREFIX}/search",
                params=params,
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False,
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def test_get_program(self, progrm_file_nm: str):
        """프로그램 상세 조회 테스트"""
        test_name = f"프로그램 상세 조회 (GET /programs/{progrm_file_nm})"
        try:
            response = await self.client.get(
                f"{API_PREFIX}/{progrm_file_nm}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False,
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def test_update_program(self, progrm_file_nm: str):
        """프로그램 정보 수정 테스트"""
        test_name = f"프로그램 정보 수정 (PUT /programs/{progrm_file_nm})"
        try:
            response = await self.client.put(
                f"{API_PREFIX}/{progrm_file_nm}",
                json=self.test_data["update_program"],
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False,
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def test_delete_program(self, progrm_file_nm: str):
        """프로그램 삭제 테스트"""
        test_name = f"프로그램 삭제 (DELETE /programs/{progrm_file_nm})"
        try:
            response = await self.client.delete(
                f"{API_PREFIX}/{progrm_file_nm}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test_result(test_name, True, data, status_code=response.status_code)
                return data
            else:
                self.log_test_result(
                    test_name, False,
                    error_message=response.text,
                    status_code=response.status_code
                )
                return None
                
        except Exception as e:
            self.log_test_result(test_name, False, error_message=str(e))
            return None
    
    async def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 Program Router 엔드포인트 테스트 시작")
        print("=" * 60)
        
        await self.setup()
        
        # 1. 프로그램 생성 테스트
        print("\n📝 1. 프로그램 생성 테스트")
        created_program = await self.test_create_program()
        
        # 2. 프로그램 목록 조회 테스트
        print("\n📋 2. 프로그램 목록 조회 테스트")
        await self.test_get_programs()
        
        # 3. 프로그램 검색 테스트
        print("\n🔍 3. 프로그램 검색 테스트")
        await self.test_search_programs()
        
        # 4. 프로그램 상세 조회 테스트 (생성된 프로그램이 있는 경우)
        if created_program:
            progrm_file_nm = created_program.get("progrm_file_nm")
            if progrm_file_nm:
                print(f"\n👁️ 4. 프로그램 상세 조회 테스트 ({progrm_file_nm})")
                await self.test_get_program(progrm_file_nm)
                
                # 5. 프로그램 정보 수정 테스트
                print(f"\n✏️ 5. 프로그램 정보 수정 테스트 ({progrm_file_nm})")
                await self.test_update_program(progrm_file_nm)
                
                # 6. 프로그램 삭제 테스트
                print(f"\n🗑️ 6. 프로그램 삭제 테스트 ({progrm_file_nm})")
                await self.test_delete_program(progrm_file_nm)
        else:
            print("\n⚠️ 프로그램 생성이 실패하여 상세 조회, 수정, 삭제 테스트를 건너뜁니다.")
        
        await self.cleanup()
        
        # 테스트 결과 출력
        self.print_test_summary()
        
        # 테스트 결과 파일 저장
        await self.save_test_results()
    
    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"총 테스트 수: {test_summary['total_tests']}")
        print(f"성공: {test_summary['passed']}")
        print(f"실패: {test_summary['failed']}")
        print(f"성공률: {(test_summary['passed'] / test_summary['total_tests'] * 100):.1f}%")
        
        if test_summary['errors']:
            print("\n❌ 실패한 테스트:")
            for error in test_summary['errors']:
                print(f"  - {error['test_name']}: {error['error']}")
    
    async def save_test_results(self):
        """테스트 결과를 파일로 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"program_router_test_report_{timestamp}.md"
        
        report_content = f"""# Program Router 테스트 보고서

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
            
            if result['response_data']:
                report_content += f"- **응답 데이터**: ```json\n{json.dumps(result['response_data'], indent=2, ensure_ascii=False)}\n```\n"
            
            report_content += "\n"
        
        if test_summary['errors']:
            report_content += "## ❌ 오류 상세 정보\n\n"
            for error in test_summary['errors']:
                report_content += f"### {error['test_name']}\n"
                report_content += f"- **오류**: {error['error']}\n"
                if error['status_code']:
                    report_content += f"- **상태 코드**: {error['status_code']}\n"
                report_content += "\n"
        
        # 파일 저장
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"\n📄 테스트 보고서 저장: {filename}")
        except Exception as e:
            print(f"\n❌ 테스트 보고서 저장 실패: {str(e)}")


async def main():
    """메인 함수"""
    try:
        tester = ProgramRouterTester()
        await tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        traceback.print_exc()


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())
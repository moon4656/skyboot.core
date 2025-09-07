#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공통 코드 관리 API 엔드포인트 테스트 스크립트

common_router.py에서 추출된 모든 엔드포인트를 체계적으로 테스트합니다.
"""

import asyncio
import json
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any

import httpx
from httpx import AsyncClient

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
TEST_TIMEOUT = 30.0

# 테스트 결과 저장
test_results = []
test_summary = {
    "total_tests": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

class CommonRouterEndpointTester:
    """
    공통 코드 관리 API 엔드포인트 테스터 클래스
    """
    
    def __init__(self):
        self.client = None
        self.auth_token = None
        self.test_group_code_id = "TEST01"
        self.test_code_id = "TC001"
        
    async def setup(self):
        """
        테스트 환경 설정
        """
        self.client = AsyncClient(base_url=BASE_URL, timeout=TEST_TIMEOUT)
        
        # 인증 토큰 획득 (필요시)
        try:
            # 로그인 API 호출하여 토큰 획득
            login_response = await self.client.post(
                f"{API_PREFIX}/auth/login",
                json={
                    "user_id": "admin",
                    "password": "admin123"
                }
            )
            if login_response.status_code == 200:
                token_data = login_response.json()
                self.auth_token = token_data.get("access_token")
                print(f"✅ 인증 토큰 획득 성공")
            else:
                print(f"⚠️ 인증 토큰 획득 실패: {login_response.status_code}")
        except Exception as e:
            print(f"⚠️ 인증 설정 중 오류: {str(e)}")
    
    def get_headers(self) -> Dict[str, str]:
        """
        API 요청 헤더 생성
        """
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def test_endpoint(self, method: str, endpoint: str, 
                          data: Dict = None, params: Dict = None,
                          expected_status: int = 200,
                          test_name: str = "") -> Dict[str, Any]:
        """
        개별 엔드포인트 테스트 실행
        """
        global test_summary
        test_summary["total_tests"] += 1
        
        test_result = {
            "test_name": test_name or f"{method} {endpoint}",
            "method": method,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "status": "PENDING",
            "response_status": None,
            "response_data": None,
            "error": None,
            "execution_time": 0
        }
        
        try:
            start_time = datetime.now()
            
            # HTTP 요청 실행
            if method.upper() == "GET":
                response = await self.client.get(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.get_headers(),
                    params=params or {}
                )
            elif method.upper() == "POST":
                response = await self.client.post(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.get_headers(),
                    json=data,
                    params=params or {}
                )
            elif method.upper() == "PUT":
                response = await self.client.put(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.get_headers(),
                    json=data,
                    params=params or {}
                )
            elif method.upper() == "DELETE":
                response = await self.client.delete(
                    f"{API_PREFIX}{endpoint}",
                    headers=self.get_headers(),
                    params=params or {}
                )
            else:
                raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # 응답 처리
            test_result["response_status"] = response.status_code
            test_result["execution_time"] = execution_time
            
            try:
                test_result["response_data"] = response.json()
            except:
                test_result["response_data"] = response.text
            
            # 테스트 결과 판정
            if response.status_code == expected_status:
                test_result["status"] = "PASSED"
                test_summary["passed"] += 1
                print(f"✅ {test_result['test_name']} - 성공 ({response.status_code})")
            else:
                test_result["status"] = "FAILED"
                test_result["error"] = f"예상 상태코드: {expected_status}, 실제: {response.status_code}"
                test_summary["failed"] += 1
                test_summary["errors"].append(test_result["error"])
                print(f"❌ {test_result['test_name']} - 실패 ({response.status_code})")
                
        except Exception as e:
            test_result["status"] = "ERROR"
            test_result["error"] = str(e)
            test_summary["failed"] += 1
            test_summary["errors"].append(str(e))
            print(f"💥 {test_result['test_name']} - 오류: {str(e)}")
        
        test_results.append(test_result)
        return test_result
    
    async def test_group_code_endpoints(self):
        """
        공통 그룹 코드 API 엔드포인트 테스트
        """
        print("\n🔍 공통 그룹 코드 API 테스트 시작")
        print("=" * 50)
        
        # 1. 그룹 코드 목록 조회 (GET /group-codes/)
        await self.test_endpoint(
            "GET", "/group-codes/",
            params={"skip": 0, "limit": 10},
            test_name="그룹 코드 목록 조회"
        )
        
        # 2. 활성 그룹 코드 목록 조회 (GET /group-codes/active)
        await self.test_endpoint(
            "GET", "/group-codes/active",
            test_name="활성 그룹 코드 목록 조회"
        )
        
        # 3. 그룹 코드 통계 조회 (GET /group-codes/statistics)
        await self.test_endpoint(
            "GET", "/group-codes/statistics",
            test_name="그룹 코드 통계 조회"
        )
        
        # 4. 그룹 코드 생성 (POST /group-codes/)
        create_data = {
            "code_id": self.test_group_code_id,
            "code_id_nm": "테스트 그룹 코드",
            "code_id_dc": "테스트용 그룹 코드입니다",
            "use_yn": "Y",
            "frst_register_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/group-codes/",
            data=create_data,
            expected_status=200,
            test_name="그룹 코드 생성"
        )
        
        # 5. 그룹 코드 상세 조회 (GET /group-codes/{group_code_id})
        await self.test_endpoint(
            "GET", f"/group-codes/{self.test_group_code_id}",
            test_name="그룹 코드 상세 조회"
        )
        
        # 6. 그룹 코드 수정 (PUT /group-codes/{group_code_id})
        update_data = {
            "code_id_nm": "수정된 테스트 그룹 코드",
            "code_id_dc": "수정된 테스트용 그룹 코드입니다",
            "use_yn": "Y"
        }
        await self.test_endpoint(
            "PUT", f"/group-codes/{self.test_group_code_id}",
            data=update_data,
            test_name="그룹 코드 수정"
        )
        
        # 7. 그룹 코드와 하위 코드 일괄 생성 (POST /group-codes/{group_code_id}/with-codes)
        batch_create_data = {
            "code_id": "TEST02",
            "code_id_nm": "일괄 생성 테스트 그룹",
            "code_id_dc": "일괄 생성 테스트용 그룹 코드",
            "use_yn": "Y",
            "frst_register_id": "test_user"
        }
        codes_data = [
            {
                "code": "CODE_001",
                "code_nm": "코드 1",
                "code_dc": "테스트 코드 1",
                "code_id": "TEST02",
                "use_yn": "Y",
                "code_ordr": 1,
                "frst_register_id": "test_user"
            }
        ]
        await self.test_endpoint(
            "POST", "/group-codes/TEST02/with-codes",
            data={"group_code_data": batch_create_data, "codes_data": codes_data},
            test_name="그룹 코드와 하위 코드 일괄 생성"
        )
    
    async def test_code_endpoints(self):
        """
        공통 코드 API 엔드포인트 테스트
        """
        print("\n🔍 공통 코드 API 테스트 시작")
        print("=" * 50)
        
        # 1. 공통 코드 목록 조회 (GET /codes/)
        await self.test_endpoint(
            "GET", "/codes/",
            params={"skip": 0, "limit": 10},
            test_name="공통 코드 목록 조회"
        )
        
        # 2. 그룹별 코드 조회 (GET /codes/group/{group_code_id})
        await self.test_endpoint(
            "GET", f"/codes/group/{self.test_group_code_id}",
            test_name="그룹별 코드 조회"
        )
        
        # 3. 공통 코드 통계 조회 (GET /codes/statistics)
        await self.test_endpoint(
            "GET", "/codes/statistics",
            test_name="공통 코드 통계 조회"
        )
        
        # 4. 공통 코드 생성 (POST /codes/)
        code_create_data = {
            "code": self.test_code_id,
            "code_nm": "테스트 코드",
            "code_dc": "테스트용 코드입니다",
            "code_id": self.test_group_code_id,
            "group_code_id": self.test_group_code_id,
            "use_yn": "Y",
            "code_ordr": 1,
            "frst_register_id": "test_user"
        }
        await self.test_endpoint(
            "POST", "/codes/",
            data=code_create_data,
            test_name="공통 코드 생성"
        )
        
        # 5. 공통 코드 상세 조회 (GET /codes/{group_id}/{code_id})
        await self.test_endpoint(
            "GET", f"/codes/{self.test_group_code_id}/{self.test_code_id}",
            test_name="공통 코드 상세 조회"
        )
        
        # 6. 공통 코드 수정 (PUT /codes/{group_id}/{code_id})
        code_update_data = {
            "code_nm": "수정된 테스트 코드",
            "code_dc": "수정된 테스트용 코드입니다",
            "use_yn": "Y"
        }
        await self.test_endpoint(
            "PUT", f"/codes/{self.test_group_code_id}/{self.test_code_id}",
            data=code_update_data,
            test_name="공통 코드 수정"
        )
        
        # 7. 코드 복사 (POST /codes/copy)
        await self.test_endpoint(
            "POST", "/codes/copy",
            params={
                "source_group_id": self.test_group_code_id,
                "target_group_id": "TEST02"
            },
            test_name="코드 복사"
        )
        
        # 8. 코드 정렬 순서 업데이트 (PUT /codes/sort-order)
        sort_updates = [
            {"code": self.test_code_id, "code_ordr": 2}
        ]
        await self.test_endpoint(
            "PUT", "/codes/sort-order",
            data=sort_updates,
            test_name="코드 정렬 순서 업데이트"
        )
    
    async def cleanup_test_data(self):
        """
        테스트 데이터 정리 - API와 직접 DB 접근 모두 시도
        """
        print("\n🧹 테스트 데이터 정리 중...")
        
        # API를 통한 삭제 시도 (실패해도 계속 진행)
        try:
            await self.test_endpoint(
                "DELETE", f"/codes/{self.test_group_code_id}/{self.test_code_id}",
                expected_status=200,
                test_name="테스트 코드 삭제"
            )
        except Exception as e:
            print(f"⚠️ API를 통한 코드 삭제 실패: {e}")
        
        try:
            await self.test_endpoint(
                "DELETE", f"/group-codes/{self.test_group_code_id}",
                expected_status=200,
                test_name="테스트 그룹 코드 삭제"
            )
        except Exception as e:
            print(f"⚠️ API를 통한 그룹 코드 삭제 실패: {e}")
            
        # 직접 DB 정리 시도
        await self.direct_cleanup_database()
        
        await self.test_endpoint(
            "DELETE", "/group-codes/TEST02",
            expected_status=200,
            test_name="일괄 생성 테스트 그룹 코드 삭제"
        )
    
    async def direct_cleanup_database(self):
        """
        데이터베이스에서 직접 테스트 데이터 삭제
        """
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            # 환경변수에서 DB 연결 정보 가져오기
            import os
            database_url = os.getenv('DATABASE_URL', 'postgresql://skybootcore:skybootcore123!@localhost:5432/skybootcore')
            
            # URL 파싱
            parsed = urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],  # '/' 제거
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            
            # 테스트 데이터 직접 삭제
            test_codes = ['TEST01', 'TEST02']
            for code in test_codes:
                # 공통 코드 삭제
                cursor.execute(
                    "DELETE FROM skybootcore.tb_cmmn_code WHERE code_id = %s",
                    (code,)
                )
                # 그룹 코드 삭제
                cursor.execute(
                    "DELETE FROM skybootcore.tb_cmmn_grp_code WHERE grp_code_id = %s",
                    (code,)
                )
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ 데이터베이스 직접 정리 완료")
            
        except Exception as e:
            print(f"⚠️ 데이터베이스 직접 정리 실패: {e}")
    
    async def run_all_tests(self):
        """
        모든 테스트 실행
        """
        try:
            await self.setup()
            
            print("🚀 공통 코드 관리 API 엔드포인트 테스트 시작")
            print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🌐 테스트 대상 서버: {BASE_URL}")
            print("=" * 70)
            
            # 기존 테스트 데이터 정리 (테스트 시작 전)
            print("🧹 기존 테스트 데이터 정리 중...")
            await self.direct_cleanup_database()
            print("✅ 테스트 시작 전 데이터 정리 완료")
            
            # 그룹 코드 API 테스트
            await self.test_group_code_endpoints()
            
            # 공통 코드 API 테스트
            await self.test_code_endpoints()
            
            # 테스트 데이터 정리
            print("🧹 테스트 데이터 정리 중...")
            await self.cleanup_test_data()
            await self.direct_cleanup_database()
            print("✅ 테스트 완료 후 데이터 정리 완료")
            
        except Exception as e:
            print(f"💥 테스트 실행 중 치명적 오류: {str(e)}")
            traceback.print_exc()
        
        finally:
            if self.client:
                await self.client.aclose()
    
    def generate_report(self):
        """
        테스트 결과 보고서 생성
        """
        print("\n" + "=" * 70)
        print("📊 테스트 결과 요약")
        print("=" * 70)
        print(f"총 테스트 수: {test_summary['total_tests']}")
        print(f"성공: {test_summary['passed']}")
        print(f"실패: {test_summary['failed']}")
        print(f"성공률: {(test_summary['passed'] / test_summary['total_tests'] * 100):.1f}%")
        
        if test_summary['errors']:
            print("\n❌ 발생한 오류들:")
            for i, error in enumerate(test_summary['errors'], 1):
                print(f"  {i}. {error}")
        
        # 상세 결과를 JSON 파일로 저장
        report_data = {
            "summary": test_summary,
            "test_results": test_results,
            "generated_at": datetime.now().isoformat()
        }
        
        with open("common_router_test_results.json", "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 상세 결과가 'common_router_test_results.json' 파일에 저장되었습니다.")


async def main():
    """
    메인 실행 함수
    """
    tester = CommonRouterEndpointTester()
    
    try:
        await tester.run_all_tests()
    finally:
        tester.generate_report()


if __name__ == "__main__":
    # 이벤트 루프 실행
    asyncio.run(main())
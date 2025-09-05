#!/usr/bin/env python3
"""
조직 API 엔드포인트 테스트 스크립트

조직 관련 모든 API 엔드포인트를 체계적으로 테스트합니다.
"""

import requests
import json
from decimal import Decimal
from datetime import datetime
import time

# 기본 설정
BASE_URL = "http://localhost:8000/api/v1"
ORG_BASE_URL = f"{BASE_URL}/organizations"
AUTH_URL = f"{BASE_URL}/auth/login"

# 테스트 결과 저장
test_results = []
created_orgs = []  # 생성된 조직 추적

def log_test_result(test_name, success, details=None, error=None):
    """테스트 결과를 로깅합니다."""
    result = {
        "test_name": test_name,
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "details": details,
        "error": str(error) if error else None
    }
    test_results.append(result)
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if error:
        print(f"   Error: {error}")
    if details:
        print(f"   Details: {details}")

def get_auth_token():
    """인증 토큰을 획득합니다."""
    try:
        login_data = {
            "user_id": "admin",
            "password": "admin123"
        }
        
        response = requests.post(AUTH_URL, json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            log_test_result("인증 토큰 획득", True, f"토큰 타입: {token_data['token_type']}")
            return access_token
        else:
            log_test_result("인증 토큰 획득", False, error=f"Status: {response.status_code}, Response: {response.text}")
            return None
            
    except Exception as e:
        log_test_result("인증 토큰 획득", False, error=e)
        return None

def test_create_organization(headers, org_data):
    """조직 생성 테스트"""
    try:
        response = requests.post(ORG_BASE_URL, json=org_data, headers=headers)
        
        if response.status_code == 200:
            org = response.json()
            created_orgs.append(org["org_no"])
            log_test_result(
                f"조직 생성 (org_no: {org_data['org_no']})", 
                True, 
                f"생성된 조직: {org['org_nm']}"
            )
            return org
        else:
            log_test_result(
                f"조직 생성 (org_no: {org_data['org_no']})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result(f"조직 생성 (org_no: {org_data['org_no']})", False, error=e)
        return None

def test_get_organizations(headers):
    """조직 목록 조회 테스트"""
    try:
        response = requests.get(ORG_BASE_URL, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            log_test_result(
                "조직 목록 조회", 
                True, 
                f"총 {data['total']}개 조직, 페이지: {data['page']}/{data['pages']}"
            )
            return data
        else:
            log_test_result(
                "조직 목록 조회", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result("조직 목록 조회", False, error=e)
        return None

def test_get_organization(headers, org_no):
    """조직 상세 조회 테스트"""
    try:
        response = requests.get(f"{ORG_BASE_URL}/{org_no}", headers=headers)
        
        if response.status_code == 200:
            org = response.json()
            log_test_result(
                f"조직 상세 조회 (org_no: {org_no})", 
                True, 
                f"조직명: {org['org_nm']}"
            )
            return org
        else:
            log_test_result(
                f"조직 상세 조회 (org_no: {org_no})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result(f"조직 상세 조회 (org_no: {org_no})", False, error=e)
        return None

def test_update_organization(headers, org_no, update_data):
    """조직 정보 수정 테스트"""
    try:
        response = requests.put(f"{ORG_BASE_URL}/{org_no}", json=update_data, headers=headers)
        
        if response.status_code == 200:
            org = response.json()
            log_test_result(
                f"조직 정보 수정 (org_no: {org_no})", 
                True, 
                f"수정된 조직명: {org['org_nm']}"
            )
            return org
        else:
            log_test_result(
                f"조직 정보 수정 (org_no: {org_no})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result(f"조직 정보 수정 (org_no: {org_no})", False, error=e)
        return None

def test_delete_organization(headers, org_no):
    """조직 삭제 테스트"""
    try:
        response = requests.delete(f"{ORG_BASE_URL}/{org_no}", headers=headers)
        
        if response.status_code == 200:
            log_test_result(
                f"조직 삭제 (org_no: {org_no})", 
                True, 
                "조직이 성공적으로 삭제됨"
            )
            if org_no in created_orgs:
                created_orgs.remove(org_no)
            return True
        else:
            log_test_result(
                f"조직 삭제 (org_no: {org_no})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return False
            
    except Exception as e:
        log_test_result(f"조직 삭제 (org_no: {org_no})", False, error=e)
        return False

def test_organization_tree(headers):
    """조직 트리 구조 조회 테스트"""
    try:
        response = requests.get(f"{ORG_BASE_URL}/tree", headers=headers)
        
        if response.status_code == 200:
            tree_data = response.json()
            log_test_result(
                "조직 트리 구조 조회", 
                True, 
                f"트리 노드 수: {len(tree_data)}"
            )
            return tree_data
        else:
            log_test_result(
                "조직 트리 구조 조회", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result("조직 트리 구조 조회", False, error=e)
        return None

def test_organization_children(headers, org_no):
    """하위 조직 조회 테스트"""
    try:
        response = requests.get(f"{ORG_BASE_URL}/{org_no}/children", headers=headers)
        
        if response.status_code == 200:
            children = response.json()
            log_test_result(
                f"하위 조직 조회 (org_no: {org_no})", 
                True, 
                f"하위 조직 수: {len(children)}"
            )
            return children
        else:
            log_test_result(
                f"하위 조직 조회 (org_no: {org_no})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result(f"하위 조직 조회 (org_no: {org_no})", False, error=e)
        return None

def test_organization_path(headers, org_no):
    """조직 경로 조회 테스트"""
    try:
        response = requests.get(f"{ORG_BASE_URL}/{org_no}/path", headers=headers)
        
        if response.status_code == 200:
            path = response.json()
            log_test_result(
                f"조직 경로 조회 (org_no: {org_no})", 
                True, 
                f"경로 깊이: {len(path)}"
            )
            return path
        else:
            log_test_result(
                f"조직 경로 조회 (org_no: {org_no})", 
                False, 
                error=f"Status: {response.status_code}, Response: {response.text}"
            )
            return None
            
    except Exception as e:
        log_test_result(f"조직 경로 조회 (org_no: {org_no})", False, error=e)
        return None

def cleanup_test_data(headers):
    """테스트 데이터 정리"""
    print("\n🧹 테스트 데이터 정리 중...")
    
    for org_no in created_orgs.copy():
        test_delete_organization(headers, org_no)
        time.sleep(0.1)  # API 호출 간격

def print_summary():
    """테스트 결과 요약 출력"""
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result["success"])
    failed_tests = total_tests - passed_tests
    
    print("\n" + "="*60)
    print("📊 조직 API 테스트 결과 요약")
    print("="*60)
    print(f"총 테스트: {total_tests}")
    print(f"성공: {passed_tests} ✅")
    print(f"실패: {failed_tests} ❌")
    print(f"성공률: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\n❌ 실패한 테스트:")
        for result in test_results:
            if not result["success"]:
                print(f"  - {result['test_name']}: {result['error']}")

def main():
    """메인 테스트 실행 함수"""
    print("🚀 조직 API 엔드포인트 테스트 시작")
    print("="*60)
    
    # 1. 인증 토큰 획득
    access_token = get_auth_token()
    if not access_token:
        print("❌ 인증 실패로 테스트를 중단합니다.")
        return
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # 2. 기본 CRUD 테스트
    print("\n📋 기본 CRUD 테스트")
    print("-" * 30)
    
    # 조직 목록 조회 (초기 상태)
    test_get_organizations(headers)
    
    # 테스트용 조직 데이터
    timestamp = int(time.time())
    test_org_data = {
        "org_no": timestamp,
        "org_nm": f"테스트 조직 {timestamp}",
        "org_ordr": 1
    }
    
    # 조직 생성
    created_org = test_create_organization(headers, test_org_data)
    if not created_org:
        print("❌ 조직 생성 실패로 후속 테스트를 건너뜁니다.")
    else:
        org_no = created_org["org_no"]
        
        # 조직 상세 조회
        test_get_organization(headers, org_no)
        
        # 조직 정보 수정
        update_data = {
            "org_nm": f"수정된 테스트 조직 {timestamp}",
            "org_ordr": 2
        }
        test_update_organization(headers, org_no, update_data)
        
        # 수정 후 다시 조회
        test_get_organization(headers, org_no)
    
    # 3. 트리 및 계층 구조 테스트
    print("\n🌳 트리 및 계층 구조 테스트")
    print("-" * 30)
    
    # 조직 트리 구조 조회
    tree_data = test_organization_tree(headers)
    
    # 기존 조직이 있다면 하위 조직 및 경로 테스트
    if created_orgs:
        test_org_no = created_orgs[0]
        test_organization_children(headers, test_org_no)
        test_organization_path(headers, test_org_no)
    
    # 4. 테스트 데이터 정리
    cleanup_test_data(headers)
    
    # 5. 결과 요약
    print_summary()

if __name__ == "__main__":
    main()
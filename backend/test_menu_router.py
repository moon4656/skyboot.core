#!/usr/bin/env python3
"""
메뉴 라우터 엔드포인트 테스트 스크립트

메뉴 관리 API의 모든 엔드포인트를 체계적으로 테스트합니다.
"""

import requests
import json
from datetime import datetime
import time

# 기본 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
MENU_PREFIX = f"{API_PREFIX}/menus"

# 테스트 결과 저장
test_results = []
test_summary = {
    "total_tests": 0,
    "passed_tests": 0,
    "failed_tests": 0,
    "success_rate": 0.0
}

def log_test_result(test_name, method, endpoint, status_code, expected_status, response_data=None, error=None):
    """테스트 결과를 로깅합니다."""
    is_success = status_code == expected_status
    result = {
        "test_name": test_name,
        "method": method,
        "endpoint": endpoint,
        "status_code": status_code,
        "expected_status": expected_status,
        "success": is_success,
        "response_data": response_data,
        "error": str(error) if error else None,
        "timestamp": datetime.now().isoformat()
    }
    
    test_results.append(result)
    test_summary["total_tests"] += 1
    
    if is_success:
        test_summary["passed_tests"] += 1
        print(f"✅ {test_name}: {method} {endpoint} - {status_code}")
    else:
        test_summary["failed_tests"] += 1
        print(f"❌ {test_name}: {method} {endpoint} - {status_code} (expected {expected_status})")
        if error:
            print(f"   Error: {error}")
    
    return is_success

def login_and_get_token():
    """로그인하여 JWT 토큰을 획득합니다."""
    login_url = f"{BASE_URL}{API_PREFIX}/auth/login"
    login_data = {
        "user_id": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ 로그인 성공: {access_token[:20]}...")
            return access_token
        else:
            print(f"❌ 로그인 실패: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 로그인 오류: {e}")
        return None

def get_headers(token):
    """인증 헤더를 반환합니다."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_menu_list(token):
    """메뉴 목록 조회 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 목록 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 목록 조회", "GET", url, 
            0, 200, None, e
        )

def test_menu_tree(token):
    """메뉴 트리 조회 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/tree"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 트리 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 트리 조회", "GET", url, 
            0, 200, None, e
        )

def test_root_menus(token):
    """루트 메뉴 조회 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/root"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "루트 메뉴 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "루트 메뉴 조회", "GET", url, 
            0, 200, None, e
        )

def test_menu_statistics(token):
    """메뉴 통계 조회 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/statistics"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 통계 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 통계 조회", "GET", url, 
            0, 200, None, e
        )

def test_create_menu(token):
    """메뉴 생성 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/"
    timestamp = int(time.time())
    menu_data = {
        "menu_no": f"TEST_MENU_{timestamp}",
        "menu_nm": f"테스트 메뉴 {timestamp}",
        "progrm_file_nm": f"/test-menu-{timestamp}",
        "menu_dc": "테스트용 메뉴입니다",
        "frst_register_id": "admin"
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=menu_data)
        success = log_test_result(
            "메뉴 생성", "POST", url, 
            response.status_code, 201, 
            response.json() if response.status_code == 201 else None
        )
        
        if success:
            return menu_data["menu_no"]
        return None
    except Exception as e:
        log_test_result(
            "메뉴 생성", "POST", url, 
            0, 201, None, e
        )
        return None

def test_get_menu_detail(token, menu_id):
    """메뉴 상세 조회 테스트"""
    if not menu_id:
        log_test_result(
            "메뉴 상세 조회", "GET", "N/A", 
            0, 200, None, "메뉴 ID가 없습니다"
        )
        return False
    
    url = f"{BASE_URL}{MENU_PREFIX}/{menu_id}"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 상세 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 상세 조회", "GET", url, 
            0, 200, None, e
        )

def test_get_child_menus(token, menu_id):
    """하위 메뉴 조회 테스트"""
    if not menu_id:
        log_test_result(
            "하위 메뉴 조회", "GET", "N/A", 
            0, 200, None, "메뉴 ID가 없습니다"
        )
        return False
    
    url = f"{BASE_URL}{MENU_PREFIX}/{menu_id}/children"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "하위 메뉴 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "하위 메뉴 조회", "GET", url, 
            0, 200, None, e
        )

def test_get_menu_breadcrumb(token, menu_id):
    """메뉴 경로 조회 테스트"""
    if not menu_id:
        log_test_result(
            "메뉴 경로 조회", "GET", "N/A", 
            0, 200, None, "메뉴 ID가 없습니다"
        )
        return False
    
    url = f"{BASE_URL}{MENU_PREFIX}/{menu_id}/breadcrumb"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 경로 조회", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 경로 조회", "GET", url, 
            0, 200, None, e
        )

def test_update_menu(token, menu_id):
    """메뉴 수정 테스트"""
    if not menu_id:
        log_test_result(
            "메뉴 수정", "PUT", "N/A", 
            0, 200, None, "메뉴 ID가 없습니다"
        )
        return False
    
    url = f"{BASE_URL}{MENU_PREFIX}/{menu_id}"
    update_data = {
        "menu_nm": f"수정된 테스트 메뉴 {int(time.time())}",
        "menu_dc": "수정된 테스트용 메뉴입니다"
    }
    
    try:
        response = requests.put(url, headers=get_headers(token), json=update_data)
        return log_test_result(
            "메뉴 수정", "PUT", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 수정", "PUT", url, 
            0, 200, None, e
        )

def test_validate_menu(token):
    """메뉴 검증 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/validate"
    timestamp = int(time.time())
    menu_data = {
        "menu_no": f"VAL_{timestamp % 100000}",
        "menu_nm": f"검증 테스트 메뉴 {timestamp}",
        "progrm_file_nm": f"/validate-test-{timestamp}",
        "menu_dc": "검증 테스트용 메뉴입니다",
        "frst_register_id": "admin"
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=menu_data)
        response_data = None
        try:
            response_data = response.json()
        except:
            response_data = response.text
        
        # 422 오류인 경우 상세 정보 출력
        if response.status_code == 422:
            print(f"\n❌ 422 오류 상세 정보:")
            print(f"요청 데이터: {menu_data}")
            print(f"응답 데이터: {response_data}")
        
        return log_test_result(
            "메뉴 검증", "POST", url, 
            response.status_code, 200, 
            response_data
        )
    except Exception as e:
        return log_test_result(
            "메뉴 검증", "POST", url, 
            0, 200, None, e
        )

def test_export_menu_data(token):
    """메뉴 데이터 내보내기 테스트"""
    url = f"{BASE_URL}{MENU_PREFIX}/export/json"
    try:
        response = requests.get(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 데이터 내보내기", "GET", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 데이터 내보내기", "GET", url, 
            0, 200, None, e
        )

def test_delete_menu(token, menu_id):
    """메뉴 삭제 테스트"""
    if not menu_id:
        log_test_result(
            "메뉴 삭제", "DELETE", "N/A", 
            0, 200, None, "메뉴 ID가 없습니다"
        )
        return False
    
    url = f"{BASE_URL}{MENU_PREFIX}/{menu_id}"
    try:
        response = requests.delete(url, headers=get_headers(token))
        return log_test_result(
            "메뉴 삭제", "DELETE", url, 
            response.status_code, 200, 
            response.json() if response.status_code == 200 else None
        )
    except Exception as e:
        return log_test_result(
            "메뉴 삭제", "DELETE", url, 
            0, 200, None, e
        )

def generate_test_report():
    """테스트 결과 보고서를 생성합니다."""
    test_summary["success_rate"] = (
        test_summary["passed_tests"] / test_summary["total_tests"] * 100
        if test_summary["total_tests"] > 0 else 0
    )
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_filename = f"menu_router_test_report_{timestamp}.md"
    
    report_content = f"""# 메뉴 라우터 엔드포인트 테스트 보고서

## 테스트 개요
- **테스트 실행 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **총 테스트 수**: {test_summary['total_tests']}
- **성공한 테스트**: {test_summary['passed_tests']}
- **실패한 테스트**: {test_summary['failed_tests']}
- **성공률**: {test_summary['success_rate']:.1f}%

## 테스트 결과 상세

"""
    
    for result in test_results:
        status_icon = "✅" if result["success"] else "❌"
        report_content += f"### {status_icon} {result['test_name']}\n"
        report_content += f"- **메소드**: {result['method']}\n"
        report_content += f"- **엔드포인트**: {result['endpoint']}\n"
        report_content += f"- **상태 코드**: {result['status_code']} (예상: {result['expected_status']})\n"
        report_content += f"- **실행 시간**: {result['timestamp']}\n"
        
        if result["error"]:
            report_content += f"- **오류**: {result['error']}\n"
        
        if result["response_data"] and isinstance(result["response_data"], dict):
            if "detail" in result["response_data"]:
                report_content += f"- **응답 상세**: {result['response_data']['detail']}\n"
        
        report_content += "\n"
    
    # 실패한 테스트 요약
    failed_tests = [r for r in test_results if not r["success"]]
    if failed_tests:
        report_content += "## 실패한 테스트 요약\n\n"
        for result in failed_tests:
            report_content += f"- **{result['test_name']}**: {result['method']} {result['endpoint']} - {result['status_code']}\n"
            if result["error"]:
                report_content += f"  - 오류: {result['error']}\n"
        report_content += "\n"
    
    # 보고서 파일 저장
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n📊 테스트 보고서가 생성되었습니다: {report_filename}")
    return report_filename

def main():
    """메인 테스트 실행 함수"""
    print("🚀 메뉴 라우터 엔드포인트 테스트 시작\n")
    
    # 1. 로그인
    token = login_and_get_token()
    if not token:
        print("❌ 로그인에 실패했습니다. 테스트를 중단합니다.")
        return
    
    print("\n📋 메뉴 엔드포인트 테스트 실행 중...\n")
    
    # 2. 기본 조회 테스트
    test_menu_list(token)
    test_menu_tree(token)
    test_root_menus(token)
    test_menu_statistics(token)
    
    # 3. 메뉴 생성 테스트
    created_menu_id = test_create_menu(token)
    
    # 4. 생성된 메뉴로 상세 테스트
    if created_menu_id:
        test_get_menu_detail(token, created_menu_id)
        test_get_child_menus(token, created_menu_id)
        test_get_menu_breadcrumb(token, created_menu_id)
        test_update_menu(token, created_menu_id)
    
    # 5. 기타 기능 테스트
    test_validate_menu(token)
    test_export_menu_data(token)
    
    # 6. 메뉴 삭제 테스트 (마지막에 실행)
    if created_menu_id:
        test_delete_menu(token, created_menu_id)
    
    # 7. 테스트 결과 요약
    print("\n" + "="*50)
    print(f"📊 테스트 완료: {test_summary['passed_tests']}/{test_summary['total_tests']} 성공 ({test_summary['success_rate']:.1f}%)")
    print("="*50)
    
    # 8. 보고서 생성
    generate_test_report()

if __name__ == "__main__":
    main()
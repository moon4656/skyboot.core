#!/usr/bin/env python3
"""
메뉴 고급 기능 엔드포인트 테스트 스크립트

이 스크립트는 메뉴 API의 고급 기능들을 테스트합니다:
- POST /menus/move - 메뉴 이동
- PUT /menus/order - 메뉴 순서 일괄 업데이트
- POST /menus/copy - 메뉴 복사
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 설정
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123"

class MenuAdvancedTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.test_results = []
        self.created_menus = []  # 테스트 중 생성된 메뉴들 추적
        
    def log_test(self, test_name: str, success: bool, response_data: Dict[str, Any], error: Optional[str] = None):
        """테스트 결과를 로깅합니다."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "success": success,
            "response_data": response_data,
            "error": error
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {'PASS' if success else 'FAIL'} {test_name}")
        if not success and error:
            print(f"   Error: {error}")
        if 'status_code' in response_data:
            print(f"   Status: {response_data['status_code']}")
        print()
    
    def authenticate(self) -> bool:
        """인증 토큰을 획득합니다."""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"user_id": USERNAME, "password": PASSWORD}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log_test("Authentication", True, {
                    "status_code": response.status_code,
                    "token_acquired": bool(self.token)
                })
                return True
            else:
                self.log_test("Authentication", False, {
                    "status_code": response.status_code
                }, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication", False, {}, str(e))
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """인증 헤더를 반환합니다."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def create_test_menu(self, menu_id: str, menu_name: str, parent_id: Optional[str] = None) -> bool:
        """테스트용 메뉴를 생성합니다."""
        try:
            menu_data = {
                "menu_no": menu_id,
                "menu_nm": menu_name,
                "progrm_file_nm": f"/test/{menu_id}",
                "upper_menu_no": parent_id,
                "menu_ordr": 1,
                "menu_dc": f"테스트용 메뉴: {menu_name}",
                "use_at": "Y",
                "delete_at": "N",
                "frst_register_id": "SYSTEM"
            }
            
            response = requests.post(
                f"{self.base_url}/menus/",
                headers=self.get_headers(),
                json=menu_data
            )
            
            if response.status_code == 201:
                self.created_menus.append(menu_id)
                return True
            else:
                print(f"메뉴 생성 실패 - Status: {response.status_code}, Response: {response.text}")
                return False
            
        except Exception as e:
            print(f"메뉴 생성 예외 발생: {str(e)}")
            return False
    
    def test_menu_move(self):
        """메뉴 이동 기능을 테스트합니다."""
        print("🔄 메뉴 이동 테스트")
        print("-" * 40)
        
        # 테스트용 메뉴들 생성
        timestamp = str(int(time.time()))
        parent_menu_id = f"PARENT_{timestamp}"
        child_menu_id = f"CHILD_{timestamp}"
        target_parent_id = f"TARGET_{timestamp}"
        
        # 부모 메뉴 생성
        if not self.create_test_menu(parent_menu_id, "부모 메뉴"):
            self.log_test("POST /menus/move - 부모 메뉴 생성", False, {}, "부모 메뉴 생성 실패")
            return
        
        # 자식 메뉴 생성
        if not self.create_test_menu(child_menu_id, "자식 메뉴", parent_menu_id):
            self.log_test("POST /menus/move - 자식 메뉴 생성", False, {}, "자식 메뉴 생성 실패")
            return
        
        # 이동 대상 부모 메뉴 생성
        if not self.create_test_menu(target_parent_id, "이동 대상 부모"):
            self.log_test("POST /menus/move - 대상 부모 메뉴 생성", False, {}, "대상 부모 메뉴 생성 실패")
            return
        
        try:
            # 메뉴 이동 테스트
            move_data = {
                "target_menu_id": child_menu_id,
                "new_parent_id": target_parent_id,
                "new_order": 5
            }
            
            response = requests.post(
                f"{self.base_url}/menus/move",
                headers=self.get_headers(),
                json=move_data
            )
            
            success = response.status_code == 200
            response_data = {"status_code": response.status_code}
            
            if success:
                data = response.json()
                response_data["data"] = data
                # 이동이 성공했는지 확인
                if data.get("upper_menu_no") == target_parent_id:
                    response_data["move_verified"] = True
                else:
                    success = False
                    response_data["move_verified"] = False
            
            self.log_test(
                "POST /menus/move - 메뉴 이동",
                success,
                response_data,
                None if success else f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_test("POST /menus/move - 메뉴 이동", False, {}, str(e))
    
    def test_menu_order_update(self):
        """메뉴 순서 일괄 업데이트를 테스트합니다."""
        print("📊 메뉴 순서 업데이트 테스트")
        print("-" * 40)
        
        # 테스트용 메뉴들 생성
        timestamp = str(int(time.time()))[-6:]  # 마지막 6자리만 사용
        menu_ids = [f"ORD_{i}_{timestamp}" for i in range(1, 4)]
        
        # 메뉴들 생성
        for i, menu_id in enumerate(menu_ids):
            if not self.create_test_menu(menu_id, f"순서 테스트 메뉴 {i+1}"):
                self.log_test(f"PUT /menus/order - 메뉴 {i+1} 생성", False, {}, f"메뉴 {i+1} 생성 실패")
                return
        
        try:
            # 순서 업데이트 데이터
            order_updates = {
                "menu_orders": [
                    {"menu_id": menu_ids[0], "menu_ordr": 3},
                    {"menu_id": menu_ids[1], "menu_ordr": 1},
                    {"menu_id": menu_ids[2], "menu_ordr": 2}
                ]
            }
            
            response = requests.put(
                f"{self.base_url}/menus/order",
                headers=self.get_headers(),
                json=order_updates
            )
            
            success = response.status_code == 200
            response_data = {"status_code": response.status_code}
            
            if success:
                data = response.json()
                response_data["data"] = data
            
            self.log_test(
                "PUT /menus/order - 메뉴 순서 일괄 업데이트",
                success,
                response_data,
                None if success else f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_test("PUT /menus/order - 메뉴 순서 일괄 업데이트", False, {}, str(e))
    
    def test_menu_copy(self):
        """메뉴 복사 기능을 테스트합니다."""
        print("📋 메뉴 복사 테스트")
        print("-" * 40)
        
        # 테스트용 메뉴 생성
        timestamp = str(int(time.time()))
        source_menu_id = f"SOURCE_{timestamp}"
        copied_menu_id = f"COPIED_{timestamp}"
        
        # 원본 메뉴 생성
        if not self.create_test_menu(source_menu_id, "원본 메뉴"):
            self.log_test("POST /menus/copy - 원본 메뉴 생성", False, {}, "원본 메뉴 생성 실패")
            return
        
        try:
            # 메뉴 복사 테스트
            copy_data = {
                "source_menu_id": source_menu_id,
                "new_parent_id": None,
                "new_menu_id": copied_menu_id,
                "new_menu_nm": f"복사된 메뉴 {timestamp}",
                "copy_children": False
            }
            
            response = requests.post(
                f"{self.base_url}/menus/copy",
                headers=self.get_headers(),
                json=copy_data
            )
            
            success = response.status_code == 200
            response_data = {"status_code": response.status_code}
            
            if success:
                data = response.json()
                response_data["data"] = data
                self.created_menus.append(copied_menu_id)  # 복사된 메뉴도 추적
                # 복사가 성공했는지 확인
                if data.get("menu_no") == copied_menu_id:
                    response_data["copy_verified"] = True
                else:
                    success = False
                    response_data["copy_verified"] = False
            
            self.log_test(
                "POST /menus/copy - 메뉴 복사",
                success,
                response_data,
                None if success else f"Status: {response.status_code}"
            )
            
        except Exception as e:
            self.log_test("POST /menus/copy - 메뉴 복사", False, {}, str(e))
    
    def cleanup_test_menus(self):
        """테스트 중 생성된 메뉴들을 정리합니다."""
        print("🧹 테스트 메뉴 정리")
        print("-" * 40)
        
        deleted_count = 0
        for menu_id in self.created_menus:
            try:
                response = requests.delete(
                    f"{self.base_url}/menus/{menu_id}",
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    deleted_count += 1
                    print(f"✅ 메뉴 삭제 완료: {menu_id}")
                else:
                    print(f"❌ 메뉴 삭제 실패: {menu_id} (Status: {response.status_code})")
            except Exception as e:
                print(f"❌ 메뉴 삭제 오류: {menu_id} - {str(e)}")
        
        print(f"\n총 {deleted_count}/{len(self.created_menus)}개 메뉴 정리 완료")
        print()
    
    def save_results(self):
        """테스트 결과를 JSON 파일로 저장합니다."""
        timestamp = str(int(time.time()))
        filename = f"menu_advanced_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def print_summary(self):
        """테스트 결과 요약을 출력합니다."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("=" * 80)
        print("테스트 결과 요약")
        print("=" * 80)
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n실패한 테스트:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test_name']}: {result.get('error', 'Unknown error')}")
    
    def run_all_tests(self):
        """모든 테스트를 실행합니다."""
        print("=" * 80)
        print("메뉴 고급 기능 엔드포인트 테스트 시작")
        print("=" * 80)
        print()
        
        # 1. 인증
        if not self.authenticate():
            print("❌ 인증 실패. 테스트를 중단합니다.")
            return
        
        # 2. 고급 기능 테스트
        self.test_menu_move()
        self.test_menu_order_update()
        self.test_menu_copy()
        
        # 3. 정리
        self.cleanup_test_menus()
        
        # 4. 결과 저장 및 요약
        filename = self.save_results()
        self.print_summary()
        print(f"\n상세 결과가 {filename} 파일에 저장되었습니다.")

def main():
    """메인 함수"""
    tester = MenuAdvancedTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
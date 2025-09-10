import requests
import json

def test_original_menu_copy():
    """원래 사용자 요청 시나리오 테스트"""
    base_url = "http://localhost:8000"
    
    # 1. 로그인하여 토큰 획득
    login_data = {
        "username": "admin",
        "password": "admin123",
        "user_id": "admin"
    }
    
    try:
        print("=== 로그인 시도 ===")
        login_response = requests.post(f"{base_url}/api/v1/auth/login", json=login_data)
        print(f"로그인 응답 상태: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"로그인 실패: {login_response.text}")
            return
        
        token = login_response.json().get("access_token")
        if not token:
            print("토큰을 받지 못했습니다.")
            return
        
        print(f"✅ 로그인 성공, 토큰 획득")
        
        # 2. 원래 요청 시나리오 테스트
        headers = {"Authorization": f"Bearer {token}"}
        
        # 원래 요청 데이터
        copy_data = {
            "source_menu_id": "10900004", 
            "new_parent_id": "10900004", 
            "new_menu_id": "10900016", 
            "new_menu_nm": "복사 테스트", 
            "copy_children": True
        }
        
        print("\n=== 원래 요청 시나리오 테스트 ===")
        print(f"요청 데이터: {json.dumps(copy_data, ensure_ascii=False, indent=2)}")
        
        copy_response = requests.post(
            f"{base_url}/api/v1/menus/copy", 
            json=copy_data, 
            headers=headers
        )
        
        print(f"응답 상태: {copy_response.status_code}")
        print(f"응답 내용: {copy_response.text}")
        
        if copy_response.status_code == 400:
            response_data = copy_response.json()
            if "자기 자신을 복사할 수 없습니다" in response_data.get("detail", ""):
                print("✅ 예상된 오류: 자기 자신을 복사하려는 시도가 올바르게 차단되었습니다.")
            else:
                print(f"❌ 예상과 다른 오류: {response_data.get('detail')}")
        elif copy_response.status_code == 200:
            print("✅ 메뉴 복사 성공")
        else:
            print(f"❌ 예상치 못한 응답: {copy_response.status_code}")
        
        # 3. 올바른 시나리오 테스트 (다른 상위 메뉴로 복사)
        correct_copy_data = {
            "source_menu_id": "10900004", 
            "new_parent_id": "10900000",  # 다른 상위 메뉴
            "new_menu_id": "10900017", 
            "new_menu_nm": "올바른 복사 테스트", 
            "copy_children": True
        }
        
        print("\n=== 올바른 복사 시나리오 테스트 ===")
        print(f"요청 데이터: {json.dumps(correct_copy_data, ensure_ascii=False, indent=2)}")
        
        correct_response = requests.post(
            f"{base_url}/api/v1/menus/copy", 
            json=correct_copy_data, 
            headers=headers
        )
        
        print(f"응답 상태: {correct_response.status_code}")
        print(f"응답 내용: {correct_response.text}")
        
        if correct_response.status_code == 200:
            print("✅ 올바른 메뉴 복사 성공")
        else:
            print(f"❌ 올바른 복사 실패: {correct_response.status_code}")
        
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_original_menu_copy()
import requests
import json

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_file_statistics():
    """
    파일 통계 조회 테스트
    """
    try:
        # 1. 로그인
        login_data = {
            "user_id": "admin",
            "password": "admin123"
        }
        
        login_response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
        if login_response.status_code != 200:
            print(f"❌ 로그인 실패: {login_response.status_code}")
            print(f"응답: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        print("✅ 로그인 성공")
        
        # 2. 파일 통계 조회
        stats_response = requests.get(f"{BASE_URL}/api/v1/files/statistics", headers=headers)
        
        print(f"상태 코드: {stats_response.status_code}")
        
        if stats_response.status_code == 200:
            stats_data = stats_response.json()
            print(f"응답 내용: {json.dumps(stats_data, indent=2, ensure_ascii=False)}")
            print("✅ 파일 통계 조회 성공")
        else:
            print(f"❌ 파일 통계 조회 실패")
            print(f"응답: {stats_response.text}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_file_statistics()
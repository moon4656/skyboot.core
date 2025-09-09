import requests
import json

def test_login_api():
    """
    로그인 API 테스트
    """
    url = "http://localhost:8000/api/auth/login"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "user_id": "admin",
        "password": "admin123"
    }
    
    try:
        print(f"🚀 로그인 API 테스트 시작")
        print(f"URL: {url}")
        print(f"Data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        
        print(f"\n📡 응답 상태 코드: {response.status_code}")
        print(f"📡 응답 헤더: {dict(response.headers)}")
        print(f"📡 응답 내용: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 로그인 성공!")
            print(f"Access Token: {result.get('access_token', 'N/A')}")
            print(f"Refresh Token: {result.get('refresh_token', 'N/A')}")
        else:
            print(f"\n❌ 로그인 실패: {response.status_code}")
            try:
                error_data = response.json()
                print(f"오류 내용: {error_data}")
            except:
                print(f"오류 내용: {response.text}")
                
    except Exception as e:
        print(f"❌ 요청 중 오류 발생: {e}")

if __name__ == "__main__":
    test_login_api()
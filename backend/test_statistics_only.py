import asyncio
import httpx

async def test_statistics():
    """공통 코드 통계 조회만 테스트"""
    async with httpx.AsyncClient() as client:
        try:
            # 먼저 로그인해서 토큰 획득
            login_response = await client.post(
                "http://localhost:8000/api/v1/auth/login",
                json={"user_id": "admin", "password": "admin123"}
            )
            
            if login_response.status_code != 200:
                print(f"로그인 실패: {login_response.text}")
                return
                
            token = login_response.json()["access_token"]
            
            response = await client.get(
                "http://localhost:8000/api/v1/codes/statistics",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            print(f"상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
            if response.status_code == 200:
                print("✅ 성공")
            else:
                print("❌ 실패")
        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    asyncio.run(test_statistics())
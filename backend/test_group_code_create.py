import asyncio
import httpx
import json
from datetime import datetime

async def test_group_code_create():
    """
    그룹 코드 생성 API 테스트
    """
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        # 1. 로그인하여 토큰 획득
        login_response = await client.post(
            f"{base_url}/api/v1/auth/login",
            json={"user_id": "admin", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            print(f"로그인 실패: {login_response.status_code}")
            print(f"응답: {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 테스트용 그룹 코드 ID 생성 (6자 제한)
        test_group_id = f"T{datetime.now().strftime('%M%S')}"
        
        # 3. 기존 테스트 데이터가 있다면 삭제
        try:
            delete_response = await client.delete(
                f"{base_url}/api/v1/group-codes/{test_group_id}",
                headers=headers
            )
            if delete_response.status_code == 200:
                print(f"기존 테스트 데이터 삭제됨: {test_group_id}")
        except:
            pass  # 삭제 실패는 무시 (데이터가 없을 수 있음)
        
        # 4. 그룹 코드 생성 테스트
        create_data = {
            "code_id": test_group_id,
            "code_id_nm": f"테스트 그룹 {test_group_id}",
            "code_id_dc": "API 테스트용 그룹 코드",
            "use_yn": "Y",
            "frst_register_id": "admin"
        }
        
        print(f"그룹 코드 생성 테스트 시작: {test_group_id}")
        create_response = await client.post(
            f"{base_url}/api/v1/group-codes/",
            json=create_data,
            headers=headers
        )
        
        print(f"상태 코드: {create_response.status_code}")
        print(f"응답 내용: {create_response.text}")
        
        if create_response.status_code in [200, 201]:
            print("✅ 그룹 코드 생성 성공")
            
            # 5. 생성된 데이터 확인
            get_response = await client.get(
                f"{base_url}/api/v1/group-codes/{test_group_id}",
                headers=headers
            )
            
            if get_response.status_code == 200:
                print("✅ 생성된 그룹 코드 조회 성공")
                print(f"조회 결과: {get_response.json()}")
            else:
                print(f"❌ 생성된 그룹 코드 조회 실패: {get_response.status_code}")
                
        else:
            print("❌ 그룹 코드 생성 실패")
            if create_response.status_code == 400:
                error_detail = create_response.json()
                print(f"오류 상세: {error_detail}")

if __name__ == "__main__":
    asyncio.run(test_group_code_create())
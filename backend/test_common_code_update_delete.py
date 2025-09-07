import asyncio
import httpx
import json
from datetime import datetime

async def test_common_code_update_delete():
    """
    공통 코드 수정/삭제 API 테스트
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
        test_group_id = f"U{datetime.now().strftime('%M%S')}"
        
        # 3. 먼저 테스트용 그룹 코드 생성
        create_group_data = {
            "code_id": test_group_id,
            "code_id_nm": f"수정삭제 테스트 그룹 {test_group_id}",
            "code_id_dc": "수정삭제 테스트용 그룹 코드",
            "use_yn": "Y",
            "frst_register_id": "admin"
        }
        
        print(f"테스트용 그룹 코드 생성: {test_group_id}")
        create_group_response = await client.post(
            f"{base_url}/api/v1/group-codes/",
            json=create_group_data,
            headers=headers
        )
        
        if create_group_response.status_code not in [200, 201]:
            print(f"❌ 테스트용 그룹 코드 생성 실패: {create_group_response.status_code}")
            print(f"응답: {create_group_response.text}")
            return
        
        print("✅ 테스트용 그룹 코드 생성 성공")
        
        # 4. 테스트용 공통 코드 생성
        test_code = f"C{datetime.now().strftime('%M%S')}"
        
        create_code_data = {
            "code": test_code,
            "code_id": test_group_id,
            "group_code_id": test_group_id,
            "code_nm": f"수정삭제 테스트 코드 {test_code}",
            "code_dc": "수정삭제 테스트용 공통 코드",
            "use_yn": "Y",
            "frst_register_id": "admin"
        }
        
        print(f"테스트용 공통 코드 생성: {test_group_id}/{test_code}")
        create_code_response = await client.post(
            f"{base_url}/api/v1/codes/",
            json=create_code_data,
            headers=headers
        )
        
        if create_code_response.status_code not in [200, 201]:
            print(f"❌ 테스트용 공통 코드 생성 실패: {create_code_response.status_code}")
            print(f"응답: {create_code_response.text}")
            return
        
        print("✅ 테스트용 공통 코드 생성 성공")
        
        # 5. 공통 코드 수정 테스트
        print(f"\n공통 코드 수정 테스트 시작: {test_group_id}/{test_code}")
        update_data = {
            "code_nm": f"수정된 테스트 코드 {test_code}",
            "code_dc": "수정된 테스트용 공통 코드",
            "use_yn": "Y",
            "last_updusr_id": "admin"
        }
        
        update_response = await client.put(
            f"{base_url}/api/v1/codes/{test_group_id}/{test_code}",
            json=update_data,
            headers=headers
        )
        
        print(f"상태 코드: {update_response.status_code}")
        print(f"응답 내용: {update_response.text}")
        
        if update_response.status_code == 200:
            print("✅ 공통 코드 수정 성공")
        else:
            print("❌ 공통 코드 수정 실패")
            if update_response.status_code == 422:
                error_detail = update_response.json()
                print(f"검증 오류 상세: {error_detail}")
        
        # 6. 공통 코드 삭제 테스트
        print(f"\n공통 코드 삭제 테스트 시작: {test_group_id}/{test_code}")
        delete_response = await client.delete(
            f"{base_url}/api/v1/codes/{test_group_id}/{test_code}",
            headers=headers
        )
        
        print(f"상태 코드: {delete_response.status_code}")
        print(f"응답 내용: {delete_response.text}")
        
        if delete_response.status_code == 200:
            print("✅ 공통 코드 삭제 성공")
            
            # 7. 삭제된 데이터 확인 (논리적 삭제 - use_yn이 'N'으로 변경되어야 함)
            get_response = await client.get(
                f"{base_url}/api/v1/codes/{test_group_id}/{test_code}",
                headers=headers
            )
            
            if get_response.status_code == 200:
                data = get_response.json()
                if data.get('use_yn') == 'N':
                    print("✅ 삭제 확인 성공 - 공통 코드가 논리적으로 삭제됨 (use_yn='N')")
                else:
                    print(f"❌ 삭제 확인 실패 - use_yn이 여전히 '{data.get('use_yn')}'임")
            elif get_response.status_code == 404:
                print("✅ 삭제 확인 성공 - 공통 코드가 물리적으로 삭제됨")
            else:
                print(f"❌ 삭제 확인 실패 - 상태 코드: {get_response.status_code}")
                print(f"응답: {get_response.text}")
        else:
            print("❌ 공통 코드 삭제 실패")
            if delete_response.status_code == 422:
                error_detail = delete_response.json()
                print(f"검증 오류 상세: {error_detail}")
        
        # 8. 테스트용 그룹 코드 정리
        print(f"\n테스트용 그룹 코드 정리: {test_group_id}")
        cleanup_response = await client.delete(
            f"{base_url}/api/v1/group-codes/{test_group_id}",
            headers=headers
        )
        
        if cleanup_response.status_code == 200:
            print("✅ 테스트용 그룹 코드 정리 완료")
        else:
            print(f"❌ 테스트용 그룹 코드 정리 실패: {cleanup_response.status_code}")

if __name__ == "__main__":
    asyncio.run(test_common_code_update_delete())
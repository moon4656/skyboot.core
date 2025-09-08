#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 상세 목록 조회 API 테스트
"""

import requests
import json

# 서버 URL
BASE_URL = "http://localhost:8000"

def test_file_details():
    print("🔐 로그인 시도...")
    print(f"요청 URL: {BASE_URL}/api/v1/auth/login")
    
    # 로그인 데이터
    login_data = {
        "user_id": "admin",
        "password": "admin123"
    }
    
    print(f"로그인 데이터: {json.dumps(login_data, indent=2)}")
    
    # 로그인 요청
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"로그인 상태 코드: {login_response.status_code}")
        print(f"로그인 응답 헤더: {dict(login_response.headers)}")
        print(f"로그인 응답: {login_response.text}")
        
        if login_response.status_code != 200:
            print("❌ 로그인 실패")
            return
        
        # 토큰 추출
        login_result = login_response.json()
        access_token = login_result.get("access_token")
        
        if not access_token:
            print("❌ 토큰을 찾을 수 없습니다")
            return
        
        print("✅ 로그인 성공!")
        print(f"토큰: {access_token[:50]}...")
        
        # 인증 헤더 설정
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 2. 파일 상세 목록 조회 테스트
        print("\n📁 파일 상세 목록 조회 테스트...")
        
        # 테스트할 첨부파일 ID (실제 존재하는 ID로 변경 필요)
        test_atch_file_id = "test_file_001"
        
        file_details_response = requests.get(
            f"{BASE_URL}/api/v1/files/details",
            headers=headers,
            params={"atch_file_id": test_atch_file_id}
        )
        
        print(f"파일 상세 목록 상태 코드: {file_details_response.status_code}")
        print(f"파일 상세 목록 응답: {file_details_response.text}")
        
        if file_details_response.status_code == 200:
            print("✅ 파일 상세 목록 조회 성공!")
        else:
            print("❌ 파일 상세 목록 조회 실패")
            
    except Exception as e:
        print(f"❌ 로그인 요청 오류: {str(e)}")
        return
        
        # 기본 목록 조회
        response = requests.get(
            f"{base_url}/file-details/details?skip=0&limit=10",
            headers=headers
        )
        
        print(f"상태 코드: {response.status_code}")
        print(f"응답: {response.text}")
        
        if response.status_code == 200:
            print("✅ 파일 상세 목록 조회 성공")
        else:
            print("❌ 파일 상세 목록 조회 실패")
            
        # 3. 특정 첨부파일 ID로 조회 테스트
        print("\n📁 특정 첨부파일 ID로 조회 테스트...")
        response2 = requests.get(
            f"{base_url}/file-details/details?atch_file_id=test123&skip=0&limit=10",
            headers=headers
        )
        
        print(f"상태 코드: {response2.status_code}")
        print(f"응답: {response2.text}")
        
        if response2.status_code == 200:
            print("✅ 첨부파일 ID별 조회 성공")
        else:
            print("❌ 첨부파일 ID별 조회 실패")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_file_details()
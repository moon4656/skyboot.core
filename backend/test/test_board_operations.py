#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
게시판 관련 API 테스트 스크립트

수정된 soft_delete 로직이 정상 작동하는지 확인합니다.
"""

import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000/api/v1"

def login_and_get_token():
    """로그인하여 토큰을 획득합니다."""
    print("🔐 로그인 중...")
    
    login_data = {
        "user_id": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print("✅ 로그인 성공, 토큰 획득")
        return token
    else:
        print(f"❌ 로그인 실패: {response.status_code} - {response.text}")
        return None

def test_board_master_operations(token):
    """게시판 마스터 생성 및 삭제 테스트"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 게시판 마스터 생성
    print("📝 게시판 마스터 생성 중...")
    board_data = {
        "bbs_id": "TEST_BOARD_001",
        "bbs_nm": "테스트 게시판",
        "bbs_intrcn": "테스트용 게시판입니다",
        "bbs_ty_code": "NOTICE",
        "reply_posbl_at": "Y",
        "file_atch_posbl_at": "Y",
        "frst_register_id": "admin"
    }
    
    response = requests.post(f"{BASE_URL}/bbs-master", json=board_data, headers=headers)
    print(f"📊 게시판 생성 응답 상태: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 게시판 마스터 생성 성공!")
        
        # 게시판 마스터 삭제 테스트
        print("🗑️ 게시판 마스터 삭제 테스트 중...")
        delete_response = requests.delete(f"{BASE_URL}/bbs-master/TEST_BOARD_001", headers=headers)
        print(f"📊 삭제 응답 상태: {delete_response.status_code}")
        print(f"📄 삭제 응답 내용: {delete_response.json()}")
        
        if delete_response.status_code == 200:
            print("✅ 게시판 마스터 삭제 성공!")
            return True
        else:
            print(f"❌ 게시판 마스터 삭제 실패: {delete_response.text}")
            return False
    else:
        print(f"❌ 게시판 마스터 생성 실패: {response.text}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 게시판 API 테스트 시작")
    print("=" * 50)
    
    # 로그인
    token = login_and_get_token()
    if not token:
        print("❌ 토큰 획득 실패, 테스트 중단")
        return
    
    # 게시판 마스터 테스트
    success = test_board_master_operations(token)
    
    print("=" * 50)
    if success:
        print("🎉 모든 테스트 완료!")
    else:
        print("❌ 일부 테스트 실패")

if __name__ == "__main__":
    main()
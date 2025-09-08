#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일 삭제 API 테스트 스크립트
"""

import requests
import json

def test_file_delete():
    """파일 삭제 API 테스트"""
    base_url = "http://localhost:8000/api/v1"
    
    # 1. 로그인하여 토큰 획득
    print("🔐 로그인 중...")
    login_response = requests.post(
        f"{base_url}/auth/login",
        json={"user_id": "admin", "password": "admin123"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 로그인 실패: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get("access_token")
    print(f"✅ 로그인 성공, 토큰 획득")
    
    # 2. 파일 업로드하여 테스트용 파일 생성
    print("📤 테스트용 파일 업로드 중...")
    
    # 테스트 파일 생성
    test_content = "파일 삭제 테스트용 내용입니다."
    with open("test_delete_file.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 파일 업로드
    with open("test_delete_file.txt", "rb") as f:
        upload_response = requests.post(
            f"{base_url}/files/upload-process",
            files={"files": ("test_delete_file.txt", f, "text/plain")},
            headers={"Authorization": f"Bearer {token}"}
        )
    
    if upload_response.status_code != 200:
        print(f"❌ 파일 업로드 실패: {upload_response.status_code}")
        print(upload_response.text)
        return
    
    upload_data = upload_response.json()
    atch_file_id = upload_data.get("atch_file_id")
    print(f"✅ 파일 업로드 성공, 첨부파일 ID: {atch_file_id}")
    
    # 3. 파일 삭제 테스트
    print("🗑️ 파일 삭제 테스트 중...")
    delete_response = requests.delete(
        f"{base_url}/files/{atch_file_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"📊 삭제 응답 상태: {delete_response.status_code}")
    print(f"📄 삭제 응답 내용: {delete_response.text}")
    
    if delete_response.status_code == 200:
        print("✅ 파일 삭제 성공!")
    else:
        print("❌ 파일 삭제 실패!")
    
    # 정리
    import os
    if os.path.exists("test_delete_file.txt"):
        os.remove("test_delete_file.txt")
        print("🧹 테스트 파일 정리 완료")

if __name__ == "__main__":
    test_file_delete()
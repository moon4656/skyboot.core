#!/usr/bin/env python3
"""
파일 업로드 프로세스 통합 API 테스트 스크립트
"""

import requests
import json
from pathlib import Path

def test_upload_process():
    """
    파일 업로드 프로세스 통합 API를 테스트합니다.
    """
    # API 엔드포인트
    url = "http://localhost:8000/api/v1/files/upload-process"
    
    # 테스트용 토큰 (임시로 더미 토큰 사용)
    token = "test_token_for_development"
    
    # 헤더 설정
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 테스트 파일 생성
    test_file_path = Path("test_upload_file.txt")
    test_file_content = "이것은 파일 업로드 프로세스 통합 API 테스트용 파일입니다.\n업로드 테스트 중입니다."
    
    with open(test_file_path, 'w', encoding='utf-8') as f:
        f.write(test_file_content)
    
    try:
        # 파일 업로드 요청
        with open(test_file_path, 'rb') as f:
            files = {
                'files': ('test_upload_file.txt', f, 'text/plain')
            }
            data = {
                'use_at': 'Y'
            }
            
            print("🚀 파일 업로드 프로세스 통합 API 테스트 시작...")
            print(f"📡 Request URL: {url}")
            print(f"📄 File: {test_file_path.name}")
            print(f"📊 File Size: {test_file_path.stat().st_size} bytes")
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            print(f"\n📈 Response Status: {response.status_code}")
            print(f"📋 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ 파일 업로드 프로세스 성공!")
                print(f"📁 첨부파일 ID: {result.get('atch_file_id')}")
                print(f"📊 성공한 파일 수: {result.get('success_count')}")
                print(f"❌ 실패한 파일 수: {result.get('failed_count')}")
                print(f"📏 전체 파일 크기: {result.get('total_size')} bytes")
                print(f"📝 업로드된 파일 목록: {len(result.get('uploaded_files', []))}개")
                
                # 업로드된 파일 상세 정보
                for i, file_info in enumerate(result.get('uploaded_files', []), 1):
                    print(f"\n📄 파일 {i}:")
                    print(f"  - 파일 순번: {file_info.get('file_sn')}")
                    print(f"  - 원본 파일명: {file_info.get('orignl_file_nm')}")
                    print(f"  - 저장 파일명: {file_info.get('stre_file_nm')}")
                    print(f"  - 파일 확장자: {file_info.get('file_extsn')}")
                    print(f"  - 파일 크기: {file_info.get('file_size')} bytes")
                    print(f"  - MIME 타입: {file_info.get('file_mime_type')}")
                
            else:
                print(f"\n❌ 파일 업로드 프로세스 실패!")
                print(f"📄 Response: {response.text}")
                
    except Exception as e:
        print(f"\n💥 테스트 중 오류 발생: {str(e)}")
        
    finally:
        # 테스트 파일 정리
        if test_file_path.exists():
            test_file_path.unlink()
            print(f"\n🧹 테스트 파일 정리 완료: {test_file_path.name}")

if __name__ == "__main__":
    test_upload_process()
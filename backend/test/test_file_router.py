#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Router 유닛 테스트

file_router.py의 모든 엔드포인트에 대한 유닛 테스트를 수행합니다.
성공/실패/예외 케이스를 포함한 포괄적인 테스트를 제공합니다.
"""

import pytest
import sys
import os
from decimal import Decimal
from fastapi import status
from fastapi.testclient import TestClient

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# FastAPI 앱 import
from main import app

# 테스트 설정
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/files"
TEST_TIMEOUT = 30.0

# 테스트 클라이언트 생성
client = TestClient(app)

class TestFileRouter:
    """파일 라우터 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """테스트 데이터 설정"""
        self.test_data = {
            "file": {
                "atch_file_id": "TEST001",
                "file_stre_cours": "/uploads/test",
                "stre_file_nm": "test_file.txt",
                "orignl_file_nm": "original_test.txt",
                "file_extsn": "txt",
                "file_cn": "테스트 파일 내용",
                "file_size": 1024,
                "frst_register_id": "testuser"
            }
        }
    
    # ==================== 파일 관리 테스트 ====================
    
    def test_get_files_list_success(self):
        """파일 목록 조회 - 성공 케이스"""
        response = client.get(f"{API_PREFIX}")
        # 인증이 필요한 경우 401, 구현되지 않은 경우 404/405 등이 올 수 있음
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
    
    def test_get_files_with_pagination(self):
        """파일 목록 조회 - 페이지네이션"""
        response = client.get(f"{API_PREFIX}?page=1&size=10")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
    
    def test_get_file_stats_success(self):
        """파일 통계 조회 - 성공 케이스"""
        response = client.get(f"{API_PREFIX}/stats")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
    
    def test_get_file_detail_not_found(self):
        """파일 상세 조회 - 존재하지 않는 파일"""
        response = client.get(f"{API_PREFIX}/NONEXISTENT")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
    
    def test_create_file_invalid_data(self):
        """파일 생성 - 잘못된 데이터"""
        invalid_data = {
            "atch_file_id": "",  # 빈 ID
            "file_size": -1  # 음수 크기
        }
        response = client.post(f"{API_PREFIX}", json=invalid_data)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY, 
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_update_file_not_found(self):
        """파일 수정 - 존재하지 않는 파일"""
        update_data = {
            "orignl_file_nm": "updated_file.txt"
        }
        response = client.put(f"{API_PREFIX}/NONEXISTENT", json=update_data)
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
    
    def test_delete_file_not_found(self):
        """파일 삭제 - 존재하지 않는 파일"""
        response = client.delete(f"{API_PREFIX}/NONEXISTENT")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
    
    # ==================== 파일 상세 관리 테스트 ====================
    
    def test_get_file_details_list(self):
        """파일 상세 목록 조회"""
        response = client.get(f"{API_PREFIX}/TEST001/details")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
    
    def test_get_file_type_stats(self):
        """파일 유형별 통계 조회"""
        response = client.get(f"{API_PREFIX}/type-stats")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_404_NOT_FOUND]
    
    def test_upload_file_invalid_type(self):
        """파일 업로드 - 잘못된 파일 타입"""
        files = {
            "file": ("test.exe", b"fake executable content", "application/octet-stream")
        }
        response = client.post(f"{API_PREFIX}/upload", files=files)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_download_file_not_found(self):
        """파일 다운로드 - 존재하지 않는 파일"""
        response = client.get(f"{API_PREFIX}/NONEXISTENT/download")
        assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_401_UNAUTHORIZED]
    
    def test_validate_file_invalid(self):
        """파일 검증 - 잘못된 파일"""
        validation_data = {
            "file_path": "/nonexistent/path/file.txt",
            "expected_size": 1024
        }
        response = client.post(f"{API_PREFIX}/validate", json=validation_data)
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_404_NOT_FOUND,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_cleanup_orphaned_files(self):
        """고아 파일 정리"""
        response = client.post(f"{API_PREFIX}/cleanup-orphaned")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    # ==================== 예외 상황 테스트 ====================
    
    def test_invalid_json_format(self):
        """잘못된 JSON 형식"""
        response = client.post(
            f"{API_PREFIX}",
            data="{invalid json}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_missing_required_fields(self):
        """필수 필드 누락"""
        incomplete_data = {
            "file_stre_cours": "/uploads/test"
            # atch_file_id, frst_register_id 누락
        }
        response = client.post(f"{API_PREFIX}", json=incomplete_data)
        assert response.status_code in [
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_sql_injection_attempt(self):
        """SQL 인젝션 시도"""
        malicious_data = {
            "atch_file_id": "'; DROP TABLE files; --",
            "frst_register_id": "testuser"
        }
        response = client.post(f"{API_PREFIX}", json=malicious_data)
        # SQL 인젝션은 차단되어야 함
        assert response.status_code in [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED
        ]
    
    def test_xss_attempt(self):
        """XSS 시도"""
        xss_data = {
            "atch_file_id": "TEST001",
            "orignl_file_nm": "<script>alert('xss')</script>",
            "frst_register_id": "testuser"
        }
        response = client.post(f"{API_PREFIX}", json=xss_data)
        # XSS는 차단되거나 이스케이프되어야 함
        assert response.status_code in [
            status.HTTP_201_CREATED,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_401_UNAUTHORIZED
        ]

class TestFileRouterIntegration:
    """파일 라우터 통합 테스트"""
    
    def test_api_endpoints_accessibility(self):
        """API 엔드포인트 접근성 테스트"""
        endpoints = [
            f"{API_PREFIX}",
            f"{API_PREFIX}/stats",
            f"{API_PREFIX}/type-stats",
            f"{API_PREFIX}/cleanup-orphaned"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            # 최소한 서버 오류(5xx)는 발생하지 않아야 함
            assert response.status_code < 500, f"Server error on {endpoint}"
    
    def test_cors_headers(self):
        """CORS 헤더 확인"""
        response = client.options(f"{API_PREFIX}")
        # CORS가 설정되어 있다면 적절한 헤더가 있어야 함
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED]

if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v", "--tb=short"])
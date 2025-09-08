#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로그인 엔드포인트 단위 테스트

이 모듈은 /api/v1/auth/login 엔드포인트의 단위 테스트를 수행합니다.
정상 로그인, 실패 케이스, 오류 처리 등을 검증합니다.
"""

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy.orm import Session

# 테스트 대상 모듈 import
from main import app
from app.schemas.auth_schemas import UserLoginRequest, UserLoginResponse
from app.services.auth_service import AuthorInfoService
from app.services.log_service import LoginLogService


class TestLoginEndpoint:
    """
    로그인 엔드포인트 단위 테스트 클래스
    """
    
    def setup_method(self):
        """테스트 메서드 실행 전 설정"""
        self.client = TestClient(app)
        self.login_url = "/api/v1/auth/login"
        
        # 테스트용 로그인 데이터
        self.valid_login_data = {
            "user_id": "test_user",
            "password": "test_password123"
        }
        
        self.invalid_login_data = {
            "user_id": "invalid_user",
            "password": "wrong_password"
        }
        
        # 모킹용 인증 결과
        self.mock_auth_result = {
            "access_token": "mock_access_token_12345",
            "refresh_token": "mock_refresh_token_67890",
            "token_type": "bearer",
            "expires_in": 86400,
            "user_info": {
                "user_id": "test_user",
                "username": "테스트사용자",
                "email": "test@example.com",
                "is_active": True
            }
        }
    
    def teardown_method(self):
        """
        각 테스트 메서드 실행 후 정리
        """
        # 의존성 오버라이드 초기화
        app.dependency_overrides.clear()
    
    def test_login_success(self):
        """
        정상 로그인 테스트
        
        올바른 사용자 ID와 비밀번호로 로그인 시 성공 응답을 반환하는지 검증
        """
        # Given: 의존성 모킹
        mock_db = Mock(spec=Session)
        
        def mock_get_db():
            return mock_db
        
        # AuthorInfoService 모킹
        mock_auth_service = Mock()
        mock_auth_service.authenticate_and_create_tokens.return_value = self.mock_auth_result
        
        # LoginLogService 모킹
        mock_log_service = Mock()
        mock_log_service.create_login_log.return_value = Mock()
        
        # 의존성 오버라이드
        from app.database import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # 서비스 패치 - 실제 모듈에서 사용되는 경로로 패치
        with patch('app.api.routes.auth_router.AuthorInfoService', return_value=mock_auth_service), \
             patch('app.api.routes.auth_router.LoginLogService', return_value=mock_log_service):
            
            # When: 로그인 요청
            response = self.client.post(
                self.login_url,
                json=self.valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 응답 검증
            assert response.status_code == 200
            
            response_data = response.json()
            assert "access_token" in response_data
            assert "refresh_token" in response_data
            assert "token_type" in response_data
            assert "expires_in" in response_data
            assert "user_info" in response_data
            
            assert response_data["access_token"] == self.mock_auth_result["access_token"]
            assert response_data["token_type"] == "bearer"
            assert response_data["user_info"]["user_id"] == "test_user"
            
            # 서비스 호출 검증
            mock_auth_service.authenticate_and_create_tokens.assert_called_once()
            mock_log_service.create_login_log.assert_called_once_with(
                db=mock_db,
                user_id="test_user",
                ip_address="testclient",
                login_status="SUCCESS"
            )
    
    def test_login_failure_invalid_credentials(self):
        """
        잘못된 인증 정보로 로그인 실패 테스트
        
        잘못된 사용자 ID 또는 비밀번호로 로그인 시 401 오류를 반환하는지 검증
        """
        # Given: 의존성 모킹
        mock_db = Mock(spec=Session)
        
        def mock_get_db():
            return mock_db
        
        # AuthorInfoService에서 인증 실패 (None 반환)
        mock_auth_service = Mock()
        mock_auth_service.authenticate_and_create_tokens.return_value = None
        
        # LoginLogService 모킹
        mock_log_service = Mock()
        mock_log_service.create_login_log.return_value = Mock()
        
        # 의존성 오버라이드
        from app.database import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # 서비스 패치 - 실제 모듈에서 사용되는 경로로 패치
        with patch('app.api.routes.auth_router.AuthorInfoService', return_value=mock_auth_service), \
             patch('app.api.routes.auth_router.LoginLogService', return_value=mock_log_service):
            
            # When: 잘못된 로그인 요청
            response = self.client.post(
                self.login_url,
                json=self.invalid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 응답 검증
            assert response.status_code == 401
            
            response_data = response.json()
            assert "detail" in response_data
            assert "사용자 ID 또는 비밀번호가 올바르지 않습니다" in response_data["detail"]
            
            # 인증 서비스 호출 검증
            mock_auth_service.authenticate_and_create_tokens.assert_called_once()
            
            # 실패 로그 기록 검증
            mock_log_service.create_login_log.assert_called_with(
                db=mock_db,
                user_id="invalid_user",
                ip_address="testclient",
                login_status="FAIL"
            )
    
    def test_login_system_error(self):
        """
        시스템 오류 발생 시 로그인 실패 테스트
        
        예상치 못한 시스템 오류 발생 시 500 오류를 반환하고 오류 로그를 기록하는지 검증
        """
        # Given: 의존성 모킹
        mock_db = Mock(spec=Session)
        
        def mock_get_db():
            return mock_db
        
        # AuthorInfoService에서 시스템 오류 발생
        mock_auth_service = Mock()
        mock_auth_service.authenticate_and_create_tokens.side_effect = Exception("데이터베이스 연결 오류")
        
        # LoginLogService 모킹
        mock_log_service = Mock()
        mock_log_service.create_login_log.return_value = Mock()
        
        # 의존성 오버라이드
        from app.database import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # 서비스 패치 - 실제 모듈에서 사용되는 경로로 패치
        with patch('app.api.routes.auth_router.AuthorInfoService', return_value=mock_auth_service), \
             patch('app.api.routes.auth_router.LoginLogService', return_value=mock_log_service):
            
            # When: 로그인 요청 (시스템 오류 발생)
            response = self.client.post(
                self.login_url,
                json=self.valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 응답 검증
            assert response.status_code == 500
            
            response_data = response.json()
            assert "detail" in response_data
            assert "로그인 처리 중 오류가 발생했습니다" in response_data["detail"]
            
            # 인증 서비스 호출 검증
            mock_auth_service.authenticate_and_create_tokens.assert_called_once()
            
            # 오류 로그 기록 검증
            mock_log_service.create_login_log.assert_called_with(
                db=mock_db,
                user_id="test_user",
                ip_address="testclient",
                login_status="ERROR",
                error_message="데이터베이스 연결 오류"
            )
    
    def test_login_invalid_request_format(self):
        """
        잘못된 요청 형식 테스트
        
        필수 필드가 누락되거나 잘못된 형식의 요청 시 401 또는 422 오류를 반환하는지 검증
        """
        # Given: 잘못된 요청 데이터들
        invalid_requests = [
            {},  # 빈 요청
            {"user_id": "test_user"},  # password 누락
            {"password": "test_password"},  # user_id 누락
            {"user_id": "", "password": "test_password"},  # 빈 user_id
            {"user_id": "test_user", "password": ""},  # 빈 password
        ]
        
        for invalid_data in invalid_requests:
            # When: 잘못된 요청
            response = self.client.post(
                self.login_url,
                json=invalid_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 401 또는 422 오류 응답 검증 (실제 구현에서는 401을 반환할 수 있음)
            assert response.status_code in [401, 422]
            
            response_data = response.json()
            assert "detail" in response_data
    
    def test_login_log_creation_failure(self):
        """
        로그 생성 실패 시에도 로그인 성공 테스트
        
        로그 생성이 실패하더라도 로그인 자체는 성공해야 함을 검증
        """
        # Given: 의존성 모킹
        mock_db = Mock(spec=Session)
        
        def mock_get_db():
            return mock_db
        
        # AuthorInfoService 정상 동작
        mock_auth_service = Mock()
        mock_auth_service.authenticate_and_create_tokens.return_value = self.mock_auth_result
        
        # LoginLogService에서 로그 생성 실패
        mock_log_service = Mock()
        mock_log_service.create_login_log.side_effect = Exception("로그 생성 실패")
        
        # 의존성 오버라이드
        from app.database import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # 서비스 패치 - 실제 모듈에서 사용되는 경로로 패치
        with patch('app.api.routes.auth_router.AuthorInfoService', return_value=mock_auth_service), \
             patch('app.api.routes.auth_router.LoginLogService', return_value=mock_log_service):
            
            # When: 로그인 요청
            response = self.client.post(
                self.login_url,
                json=self.valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 로그인은 성공해야 함
            assert response.status_code == 200
            
            response_data = response.json()
            assert "access_token" in response_data
            assert response_data["access_token"] == self.mock_auth_result["access_token"]
            
            # 인증 서비스 호출 검증
            mock_auth_service.authenticate_and_create_tokens.assert_called_once()
    
    def test_login_response_schema(self):
        """
        로그인 응답 스키마 검증 테스트
        
        응답 데이터가 UserLoginResponse 스키마를 준수하는지 검증
        """
        # Given: 의존성 모킹
        mock_db = Mock(spec=Session)
        
        def mock_get_db():
            return mock_db
        
        # AuthorInfoService 정상 동작
        mock_auth_service = Mock()
        mock_auth_service.authenticate_and_create_tokens.return_value = self.mock_auth_result
        
        # LoginLogService 모킹
        mock_log_service = Mock()
        mock_log_service.create_login_log.return_value = Mock()
        
        # 의존성 오버라이드
        from app.database import get_db
        app.dependency_overrides[get_db] = mock_get_db
        
        # 서비스 패치 - 실제 모듈에서 사용되는 경로로 패치
        with patch('app.api.routes.auth_router.AuthorInfoService', return_value=mock_auth_service), \
             patch('app.api.routes.auth_router.LoginLogService', return_value=mock_log_service):
            
            # When: 로그인 요청
            response = self.client.post(
                self.login_url,
                json=self.valid_login_data,
                headers={"Content-Type": "application/json"}
            )
            
            # Then: 응답 스키마 검증
            assert response.status_code == 200
            
            response_data = response.json()
            
            # UserLoginResponse 스키마 필드 검증
            required_fields = ["access_token", "refresh_token", "token_type", "expires_in", "user_info"]
            for field in required_fields:
                assert field in response_data, f"필수 필드 '{field}'가 응답에 없습니다."
            
            # user_info 하위 필드 검증
            user_info = response_data["user_info"]
            user_info_fields = ["user_id", "username", "email", "is_active"]
            for field in user_info_fields:
                assert field in user_info, f"user_info의 필수 필드 '{field}'가 응답에 없습니다."
            
            # 데이터 타입 검증
            assert isinstance(response_data["access_token"], str)
            assert isinstance(response_data["refresh_token"], str)
            assert isinstance(response_data["token_type"], str)
            assert isinstance(response_data["expires_in"], int)
            assert isinstance(response_data["user_info"], dict)
            assert isinstance(user_info["is_active"], bool)


def run_unit_tests():
    """
    단위 테스트 실행 함수
    
    pytest를 사용하여 모든 테스트를 실행하고 결과를 출력합니다.
    """
    print("🚀 로그인 엔드포인트 단위 테스트 시작")
    print("=" * 60)
    
    # pytest 실행
    test_results = pytest.main([
        __file__,
        "-v",  # 상세 출력
        "--tb=short",  # 짧은 traceback
        "--no-header",  # 헤더 제거
    ])
    
    print("=" * 60)
    if test_results == 0:
        print("✅ 모든 단위 테스트가 성공적으로 완료되었습니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다. 위의 오류를 확인해주세요.")
    
    return test_results == 0


if __name__ == "__main__":
    # 단위 테스트 실행
    success = run_unit_tests()
    
    # 테스트 결과 요약
    print("\n📊 테스트 결과 요약:")
    print(f"- 테스트 성공: {'✅' if success else '❌'}")
    print(f"- 실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not success:
        exit(1)
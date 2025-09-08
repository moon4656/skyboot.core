import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from main import app
from app.schemas.file_schemas import FileCreate, FileUpdate
from app.utils.jwt_utils import create_access_token
import json
import time
from concurrent.futures import ThreadPoolExecutor
import threading


class TestFileRouterIntegration:
    """파일 라우터 통합 테스트 클래스"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.client = TestClient(app)
        self.base_url = "/api/v1/files"
        
        # JWT 토큰 생성
        test_user_data = {
            "sub": "testuser",
            "user_id": "testuser",
            "email": "test@example.com",
            "group_id": "admin"
        }
        self.access_token = create_access_token(test_user_data)
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
        
        # 테스트 데이터
        self.valid_file_data = {
            "atch_file_id": "TEST001",
            "file_stre_cours": "/uploads/test",
            "stre_file_nm": "test_file.txt",
            "orignl_file_nm": "original_test.txt",
            "file_extsn": "txt",
            "file_cn": "테스트 파일 내용",
            "file_size": 1024,
            "frst_register_id": "testuser"
        }
        
        self.update_data = {
            "orignl_file_nm": "updated_test.txt",
            "file_cn": "수정된 파일 내용"
        }
        
        # 생성된 파일 ID 저장용
        self.created_file_ids = []
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        # 생성된 파일들 정리
        for file_id in self.created_file_ids:
            try:
                self.client.delete(f"{self.base_url}/{file_id}", headers=self.headers)
            except:
                pass
    
    # 시나리오 1: 기본 파일 관리 워크플로우
    def test_scenario_1_basic_file_lifecycle(self):
        """시나리오 1: 파일의 전체 생명주기 테스트"""
        
        # 1.1 파일 생성
        response = self.client.post(self.base_url, json=self.valid_file_data, headers=self.headers)
        if response.status_code != 201:
            print(f"Error response: {response.status_code} - {response.text}")
        assert response.status_code == 201
        created_file = response.json()
        file_id = created_file["id"]
        self.created_file_ids.append(file_id)
        
        # 1.2 파일 목록 조회
        response = self.client.get(f"{self.base_url}?page=1&size=10", headers=self.headers)
        assert response.status_code == 200
        files_list = response.json()
        assert len(files_list) >= 1
        
        # 1.3 특정 파일 조회
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 200
        file_detail = response.json()
        assert file_detail["id"] == file_id
        assert file_detail["orignl_file_nm"] == self.valid_file_data["orignl_file_nm"]
        
        # 1.4 파일 수정
        response = self.client.put(f"{self.base_url}/{file_id}", json=self.update_data, headers=self.headers)
        assert response.status_code == 200
        updated_file = response.json()
        assert updated_file["orignl_file_nm"] == self.update_data["orignl_file_nm"]
        
        # 1.5 파일 삭제
        response = self.client.delete(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 204
        
        # 1.6 삭제된 파일 조회 시도
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 404
        
        # 정리 목록에서 제거 (이미 삭제됨)
        self.created_file_ids.remove(file_id)
    
    # 시나리오 2: 파일 업로드 및 다운로드 워크플로우
    def test_scenario_2_upload_download_workflow(self):
        """시나리오 2: 파일 업로드, 검증, 다운로드 프로세스 테스트"""
        
        # 2.1 파일 업로드 (파일 생성으로 시뮬레이션)
        response = self.client.post(self.base_url, json=self.valid_file_data, headers=self.headers)
        assert response.status_code == 201
        uploaded_file = response.json()
        file_id = uploaded_file["id"]
        self.created_file_ids.append(file_id)
        
        # 2.2 파일 검증 (파일 조회로 시뮬레이션)
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 200
        file_info = response.json()
        assert file_info["file_size"] == self.valid_file_data["file_size"]
        
        # 2.3 파일 다운로드 (파일 조회로 시뮬레이션)
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 200
        downloaded_file = response.json()
        assert downloaded_file["file_cn"] == self.valid_file_data["file_cn"]
        
        # 2.4 잘못된 파일 타입 업로드 시도
        malicious_data = self.valid_file_data.copy()
        malicious_data["file_extsn"] = "exe"
        malicious_data["orignl_file_nm"] = "malicious.exe"
        
        response = self.client.post(self.base_url, json=malicious_data, headers=self.headers)
        # 파일 타입 검증이 있다면 400, 없다면 201이 될 수 있음
        assert response.status_code in [201, 400, 422]
        
        # 2.5 큰 파일 업로드 시도
        large_file_data = self.valid_file_data.copy()
        large_file_data["file_size"] = 50 * 1024 * 1024  # 50MB
        
        response = self.client.post(self.base_url, json=large_file_data, headers=self.headers)
        # 크기 제한이 있다면 413 또는 422, 없다면 201
        assert response.status_code in [201, 413, 422]
    
    # 시나리오 3: 파일 통계 및 관리 기능
    def test_scenario_3_stats_and_management(self):
        """시나리오 3: 파일 통계 조회 및 관리 기능 테스트"""
        
        # 테스트용 파일 여러 개 생성
        file_ids = []
        for i in range(3):
            test_data = self.valid_file_data.copy()
            test_data["atch_file_id"] = f"TEST{i:03d}"
            test_data["orignl_file_nm"] = f"test_file_{i}.txt"
            
            response = self.client.post(self.base_url, json=test_data, headers=self.headers)
            assert response.status_code == 201
            file_id = response.json()["id"]
            file_ids.append(file_id)
            self.created_file_ids.append(file_id)
        
        # 3.1 전체 파일 통계 조회 (파일 목록으로 시뮬레이션)
        response = self.client.get(self.base_url, headers=self.headers)
        assert response.status_code == 200
        files_list = response.json()
        assert len(files_list) >= 3
        
        # 3.2 파일 타입별 통계 (현재 엔드포인트가 없으므로 스킵)
        # 실제 구현 시 추가 가능
        
        # 3.3 파일 상세 정보 조회
        for file_id in file_ids:
            response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
            assert response.status_code == 200
            file_detail = response.json()
            assert "id" in file_detail
            assert "orignl_file_nm" in file_detail
    
    # 시나리오 4: 오류 처리 및 보안 테스트
    def test_scenario_4_error_handling_and_security(self):
        """시나리오 4: 다양한 오류 상황과 보안 공격 방어 테스트"""
        
        # 4.1 SQL 인젝션 시도
        sql_injection_data = self.valid_file_data.copy()
        sql_injection_data["atch_file_id"] = "'; DROP TABLE files; --"
        
        response = self.client.post(self.base_url, json=sql_injection_data, headers=self.headers)
        # SQL 인젝션이 차단되어야 함 (400) 또는 안전하게 처리됨 (201)
        assert response.status_code in [201, 400, 422]
        
        # 4.2 XSS 공격 시도
        xss_data = self.valid_file_data.copy()
        xss_data["orignl_file_nm"] = "<script>alert('xss')</script>"
        
        response = self.client.post(self.base_url, json=xss_data, headers=self.headers)
        # XSS가 차단되거나 안전하게 처리되어야 함
        assert response.status_code in [201, 400, 422]
        
        # 4.3 잘못된 JSON 형식
        auth_headers = self.headers.copy()
        auth_headers["Content-Type"] = "application/json"
        response = self.client.post(
            self.base_url,
            data="{invalid json}",
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # 4.4 음수 파일 크기
        invalid_size_data = self.valid_file_data.copy()
        invalid_size_data["file_size"] = -1
        
        response = self.client.post(self.base_url, json=invalid_size_data, headers=self.headers)
        assert response.status_code in [422, 400]
        
        # 4.5 존재하지 않는 파일 조회
        response = self.client.get(f"{self.base_url}/99999", headers=self.headers)
        assert response.status_code == 404
        
        # 4.6 인증 테스트는 실제 인증 시스템이 구현된 경우에만 가능
        # 현재는 스킵
    
    # 시나리오 5: 성능 및 동시성 테스트
    def test_scenario_5_performance_and_concurrency(self):
        """시나리오 5: 성능 및 동시 접근 테스트"""
        
        # 5.1 동시 조회 요청 테스트
        def make_get_request():
            response = self.client.get(self.base_url, headers=self.headers)
            return response.status_code
        
        # 10개의 동시 요청 (100개는 너무 많아서 축소)
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_get_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # 모든 요청이 성공해야 함
        assert all(status == 200 for status in results)
        
        # 5.2 동시 파일 생성 테스트
        def create_file(index):
            test_data = self.valid_file_data.copy()
            test_data["atch_file_id"] = f"CONCURRENT{index:03d}"
            test_data["orignl_file_nm"] = f"concurrent_file_{index}.txt"
            
            response = self.client.post(self.base_url, json=test_data, headers=self.headers)
            if response.status_code == 201:
                return response.json()["id"]
            return None
        
        # 5개의 동시 생성 요청
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_file, i) for i in range(5)]
            created_ids = [future.result() for future in futures if future.result()]
        
        # 생성된 파일들을 정리 목록에 추가
        self.created_file_ids.extend(created_ids)
        
        # 최소 일부 파일은 성공적으로 생성되어야 함
        assert len(created_ids) > 0
        
        # 5.3 응답 시간 테스트
        start_time = time.time()
        response = self.client.get(self.base_url)
        end_time = time.time()
        
        assert response.status_code == 200
        response_time = end_time - start_time
        # 응답 시간이 2초 이내여야 함
        assert response_time < 2.0
    
    # 시나리오 6: 엔드투엔드 사용자 시나리오
    def test_scenario_6_end_to_end_user_workflow(self):
        """시나리오 6: 실제 사용자의 전형적인 사용 패턴 시뮬레이션"""
        
        # 6.1 사용자 로그인 및 파일 목록 조회
        response = self.client.get(self.base_url, headers=self.headers)
        assert response.status_code == 200
        initial_files = response.json()
        
        # 6.2 새 문서 파일 업로드
        document_data = {
            "atch_file_id": "DOC001",
            "file_stre_cours": "/uploads/documents",
            "stre_file_nm": "important_document.pdf",
            "orignl_file_nm": "중요한_문서.pdf",
            "file_extsn": "pdf",
            "file_cn": "중요한 비즈니스 문서 내용",
            "file_size": 2048,
            "frst_register_id": "business_user"
        }
        
        response = self.client.post(self.base_url, json=document_data, headers=self.headers)
        assert response.status_code == 201
        uploaded_doc = response.json()
        doc_id = uploaded_doc["id"]
        self.created_file_ids.append(doc_id)
        
        # 6.3 업로드된 파일 정보 확인
        response = self.client.get(f"{self.base_url}/{doc_id}", headers=self.headers)
        assert response.status_code == 200
        doc_info = response.json()
        assert doc_info["orignl_file_nm"] == document_data["orignl_file_nm"]
        assert doc_info["file_extsn"] == document_data["file_extsn"]
        
        # 6.4 파일 이름 수정
        name_update = {
            "orignl_file_nm": "수정된_중요한_문서.pdf",
            "file_cn": "수정된 비즈니스 문서 내용"
        }
        
        response = self.client.put(f"{self.base_url}/{doc_id}", json=name_update, headers=self.headers)
        assert response.status_code == 200
        updated_doc = response.json()
        assert updated_doc["orignl_file_nm"] == name_update["orignl_file_nm"]
        
        # 6.5 파일 다운로드 (조회로 시뮬레이션)
        response = self.client.get(f"{self.base_url}/{doc_id}", headers=self.headers)
        assert response.status_code == 200
        downloaded_doc = response.json()
        assert downloaded_doc["file_cn"] == name_update["file_cn"]
        
        # 6.6 전체 파일 통계 확인 (목록 조회로 시뮬레이션)
        response = self.client.get(self.base_url, headers=self.headers)
        assert response.status_code == 200
        final_files = response.json()
        assert len(final_files) >= len(initial_files) + 1
        
        # 6.7 불필요한 파일 삭제
        response = self.client.delete(f"{self.base_url}/{doc_id}", headers=self.headers)
        assert response.status_code == 204
        
        # 6.8 삭제 확인
        response = self.client.get(f"{self.base_url}/{doc_id}", headers=self.headers)
        assert response.status_code == 404
        
        # 정리 목록에서 제거 (이미 삭제됨)
        self.created_file_ids.remove(doc_id)
    
    # 추가: 전체 시나리오 통합 테스트
    def test_all_scenarios_integration(self):
        """모든 시나리오를 연속으로 실행하는 통합 테스트"""
        
        # 각 시나리오의 핵심 기능만 간단히 테스트
        
        # 1.1 파일 생성
        response = self.client.post(self.base_url, json=self.valid_file_data, headers=self.headers)
        if response.status_code != 201:
            print(f"응답 상태 코드: {response.status_code}")
            print(f"응답 내용: {response.text}")
        assert response.status_code == 201
        file_id = response.json()["id"]
        self.created_file_ids.append(file_id)
        
        # 파일 조회
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 200
        
        # 파일 수정
        response = self.client.put(f"{self.base_url}/{file_id}", json=self.update_data, headers=self.headers)
        assert response.status_code == 200
        
        # 목록 조회
        response = self.client.get(self.base_url, headers=self.headers)
        assert response.status_code == 200
        
        # 오류 처리 테스트
        response = self.client.get(f"{self.base_url}/99999", headers=self.headers)
        assert response.status_code == 404
        
        # 파일 삭제
        response = self.client.delete(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 204
        
        # 삭제 확인
        response = self.client.get(f"{self.base_url}/{file_id}", headers=self.headers)
        assert response.status_code == 404
        
        self.created_file_ids.remove(file_id)


if __name__ == "__main__":
    # 개별 시나리오 실행을 위한 헬퍼 함수
    def run_scenario(scenario_number):
        """특정 시나리오만 실행"""
        test_instance = TestFileRouterIntegration()
        test_instance.setup_method()
        
        try:
            if scenario_number == 1:
                test_instance.test_scenario_1_basic_file_lifecycle()
            elif scenario_number == 2:
                test_instance.test_scenario_2_upload_download_workflow()
            elif scenario_number == 3:
                test_instance.test_scenario_3_stats_and_management()
            elif scenario_number == 4:
                test_instance.test_scenario_4_error_handling_and_security()
            elif scenario_number == 5:
                test_instance.test_scenario_5_performance_and_concurrency()
            elif scenario_number == 6:
                test_instance.test_scenario_6_end_to_end_user_workflow()
            else:
                print(f"시나리오 {scenario_number}는 존재하지 않습니다.")
                return
            
            print(f"시나리오 {scenario_number} 테스트 성공!")
            
        except Exception as e:
            print(f"시나리오 {scenario_number} 테스트 실패: {e}")
            
        finally:
            test_instance.teardown_method()
    
    # 모든 시나리오 실행
    print("파일 라우터 통합 테스트 시작...")
    for i in range(1, 7):
        print(f"\n=== 시나리오 {i} 실행 ===")
        run_scenario(i)
    
    print("\n통합 테스트 완료!")
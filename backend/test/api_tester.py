import json
import requests
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

class APITester:
    def __init__(self, base_url: str = "http://localhost:8000", batch_size: int = 10):
        self.base_url = base_url
        self.batch_size = batch_size
        self.access_token = None
        self.session = requests.Session()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.logs_dir = f"logs/{self.timestamp}"
        
        # 로그 디렉토리 생성
        os.makedirs(self.logs_dir, exist_ok=True)
        
    def get_access_token(self) -> Optional[str]:
        """로그인하여 액세스 토큰 획득"""
        try:
            login_data = {
                "user_id": "admin",
                "password": "admin123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                print(f"[SUCCESS] 로그인 성공: 토큰 획득")
                return self.access_token
            else:
                print(f"[ERROR] 로그인 실패: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[ERROR] 로그인 중 오류: {str(e)}")
            return None
    
    def generate_dummy_data(self, schema: Dict) -> Any:
        """스키마에 따라 더미 데이터 생성"""
        if not schema:
            return {}
            
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            data = {}
            
            for prop_name, prop_schema in properties.items():
                if prop_name in required or prop_name in ['user_id', 'password', 'email_adres', 'user_nm']:
                    data[prop_name] = self.generate_dummy_value(prop_schema, prop_name)
                    
            return data
            
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self.generate_dummy_data(items_schema)]
            
        else:
            return self.generate_dummy_value(schema)
    
    def generate_dummy_value(self, schema: Dict, field_name: str = "") -> Any:
        """필드별 더미 값 생성"""
        schema_type = schema.get('type', 'string')
        
        # 필드명 기반 더미 데이터
        if 'user_id' in field_name.lower():
            return "test_user_001"
        elif 'password' in field_name.lower():
            return "testpass123"
        elif 'email' in field_name.lower():
            return "test@example.com"
        elif 'user_nm' in field_name.lower() or 'name' in field_name.lower():
            return "테스트사용자"
        elif 'id' in field_name.lower():
            return "test_001"
        elif 'code' in field_name.lower():
            return "TEST"
        elif 'url' in field_name.lower():
            return "https://example.com"
        elif 'path' in field_name.lower():
            return "/test/path"
        elif 'nm' in field_name.lower():
            return "테스트명"
        elif 'dc' in field_name.lower():
            return "테스트 설명"
        
        # 타입 기반 더미 데이터
        if schema_type == 'string':
            max_length = schema.get('maxLength', 50)
            if max_length <= 10:
                return "test"
            elif max_length <= 30:
                return "test_value"
            else:
                return "test_long_value_for_testing"
        elif schema_type == 'integer':
            return 1
        elif schema_type == 'number':
            return 1.0
        elif schema_type == 'boolean':
            return True
        elif schema_type == 'array':
            return []
        else:
            return "test_value"
    
    def prepare_request_data(self, endpoint: Dict) -> Dict:
        """요청 데이터 준비"""
        headers = {
            "Content-Type": "application/json"
        }
        
        # 로그인 엔드포인트가 아닌 경우 인증 헤더 추가
        path = endpoint['path']
        is_login_endpoint = '/auth/login' in path
        
        if not is_login_endpoint and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        # 경로 매개변수 처리
        path = endpoint['path']
        path_params = {}
        
        for param in endpoint.get('parameters', []):
            if param.get('in') == 'path':
                param_name = param['name']
                if '{' + param_name + '}' in path:
                    dummy_value = self.generate_dummy_value(param.get('schema', {}), param_name)
                    path = path.replace('{' + param_name + '}', str(dummy_value))
                    path_params[param_name] = dummy_value
        
        # 쿼리 매개변수 처리
        query_params = {}
        for param in endpoint.get('parameters', []):
            if param.get('in') == 'query':
                param_name = param['name']
                if param.get('required', False) or param_name in ['skip', 'limit']:
                    dummy_value = self.generate_dummy_value(param.get('schema', {}), param_name)
                    if param_name == 'skip':
                        dummy_value = 0
                    elif param_name == 'limit':
                        dummy_value = 10
                    query_params[param_name] = dummy_value
        
        # 요청 본문 처리
        request_body = None
        if endpoint.get('requestBody'):
            content = endpoint['requestBody'].get('content', {})
            if 'application/json' in content:
                schema_ref = content['application/json'].get('schema', {})
                if '$ref' in schema_ref:
                    # 스키마 참조는 기본 더미 데이터로 처리
                    if 'UserInfo' in schema_ref['$ref']:
                        request_body = {
                            "user_id": "test_user_001",
                            "user_nm": "테스트사용자",
                            "password": "testpass123",
                            "email_adres": "test@example.com"
                        }
                    elif 'Login' in schema_ref['$ref']:
                        request_body = {
                            "user_id": "admin",
                            "password": "admin123"
                        }
                    elif 'Token' in schema_ref['$ref']:
                        request_body = {
                            "refresh_token": "dummy_refresh_token"
                        }
                    else:
                        request_body = {"test": "data"}
                else:
                    request_body = self.generate_dummy_data(schema_ref)
        
        return {
            'url': f"{self.base_url}{path}",
            'headers': headers,
            'params': query_params,
            'json': request_body,
            'path_params': path_params
        }
    
    def test_endpoint(self, endpoint: Dict, index: int) -> Dict:
        """단일 엔드포인트 테스트"""
        method = endpoint['method'].lower()
        start_time = time.time()
        
        try:
            # 요청 데이터 준비
            request_data = self.prepare_request_data(endpoint)
            
            # HTTP 요청 실행
            response = self.session.request(
                method=method,
                url=request_data['url'],
                headers=request_data['headers'],
                params=request_data['params'],
                json=request_data['json'],
                timeout=30
            )
            
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)  # ms
            
            # 결과 분석
            success = 200 <= response.status_code < 300
            
            result = {
                'success': success,
                'status_code': response.status_code,
                'duration_ms': duration,
                'request': {
                    'method': method.upper(),
                    'url': request_data['url'],
                    'headers': dict(request_data['headers']),
                    'params': request_data['params'],
                    'body': request_data['json']
                },
                'response': {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'body': response.text[:1000] if response.text else None  # 응답 크기 제한
                },
                'error': None,
                'classification': self.classify_result(response.status_code, response.text)
            }
            
        except requests.exceptions.Timeout:
            result = {
                'success': False,
                'status_code': 0,
                'duration_ms': 30000,
                'error': 'Timeout',
                'classification': 'timeout'
            }
        except Exception as e:
            result = {
                'success': False,
                'status_code': 0,
                'duration_ms': 0,
                'error': str(e),
                'classification': 'error'
            }
        
        # 로그 파일 저장
        self.save_test_log(endpoint, result, index)
        
        return result
    
    def classify_result(self, status_code: int, response_text: str) -> str:
        """테스트 결과 분류"""
        if 200 <= status_code < 300:
            return 'success'
        elif status_code == 401:
            return 'authentication'
        elif status_code == 403:
            return 'authorization'
        elif status_code == 422:
            return 'validation'
        elif 400 <= status_code < 500:
            return 'client_error'
        elif 500 <= status_code < 600:
            return 'server_error'
        else:
            return 'unknown'
    
    def save_test_log(self, endpoint: Dict, result: Dict, index: int):
        """테스트 로그 저장"""
        method = endpoint['method']
        path = endpoint['path'].replace('/', '_').replace('{', '').replace('}', '')
        filename = f"{index:03d}_{method}_{path}.md"
        filepath = os.path.join(self.logs_dir, filename)
        
        log_content = f"""# API 테스트 로그

## 기본 정보
- **엔드포인트**: {method} {endpoint['path']}
- **요약**: {endpoint.get('summary', 'N/A')}
- **테스트 시간**: {datetime.now().isoformat()}
- **소요 시간**: {result.get('duration_ms', 0)}ms
- **결과**: {'[SUCCESS] 성공' if result.get('success') else '[FAIL] 실패'}
- **분류**: {result.get('classification', 'unknown')}

## 요청 정보
```json
{json.dumps(result.get('request', {}), ensure_ascii=False, indent=2)}
```

## 응답 정보
- **상태 코드**: {result.get('status_code', 0)}
- **응답 헤더**: 
```json
{json.dumps(result.get('response', {}).get('headers', {}), ensure_ascii=False, indent=2)}
```
- **응답 본문**: 
```
{result.get('response', {}).get('body', 'N/A')}
```

## 오류 정보
{result.get('error', 'N/A')}

## 상세 설명
{endpoint.get('description', 'N/A')}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(log_content)
    
    def run_batch_test(self, batch_number: int = 1) -> Dict:
        """배치 테스트 실행"""
        # master_list.json 로드
        with open('master_list.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        endpoints = master_data['endpoints']
        
        # 아직 테스트되지 않은 엔드포인트 찾기
        untested = [ep for ep in endpoints if not ep.get('tested', False)]
        
        if not untested:
            print("모든 엔드포인트가 이미 테스트되었습니다.")
            return {'tested': 0, 'remaining': 0}
        
        # 현재 배치 선택
        current_batch = untested[:self.batch_size]
        
        print(f"\n=== 배치 {batch_number} 테스트 시작 ({len(current_batch)}개 엔드포인트) ===")
        
        # 액세스 토큰 획득
        self.get_access_token()
        
        batch_results = []
        
        for i, endpoint in enumerate(current_batch, 1):
            print(f"\n[{i}/{len(current_batch)}] 테스트 중: {endpoint['method']} {endpoint['path']}")
            
            result = self.test_endpoint(endpoint, i)
            batch_results.append(result)
            
            # 결과 출력
            status = "[OK]" if result['success'] else "[FAIL]"
            print(f"  {status} {result['status_code']} ({result['duration_ms']}ms) - {result['classification']}")
            
            # 테스트 완료 표시
            endpoint['tested'] = True
            endpoint['test_result'] = result
            endpoint['test_timestamp'] = datetime.now().isoformat()
        
        # master_list.json 업데이트
        with open('master_list.json', 'w', encoding='utf-8') as f:
            json.dump(master_data, f, ensure_ascii=False, indent=2)
        
        # 배치 리포트 생성
        self.generate_batch_report(batch_number, current_batch, batch_results)
        
        # 누적 리포트 생성
        self.generate_cumulative_report()
        
        remaining = len(untested) - len(current_batch)
        
        print(f"\n=== 배치 {batch_number} 완료 ===")
        print(f"테스트 완료: {len(current_batch)}개")
        print(f"남은 엔드포인트: {remaining}개")
        
        return {
            'tested': len(current_batch),
            'remaining': remaining,
            'results': batch_results
        }
    
    def generate_batch_report(self, batch_number: int, endpoints: List[Dict], results: List[Dict]):
        """배치 리포트 생성"""
        success_count = sum(1 for r in results if r['success'])
        
        report_content = f"""# 배치 {batch_number} 테스트 리포트

## 요약
- **테스트 시간**: {datetime.now().isoformat()}
- **테스트 엔드포인트 수**: {len(endpoints)}
- **성공**: {success_count}개
- **실패**: {len(results) - success_count}개
- **성공률**: {(success_count / len(results) * 100):.1f}%

## 상세 결과

| 순번 | 메소드 | 경로 | 상태 | 소요시간 | 분류 |
|------|--------|------|------|----------|------|
"""
        
        for i, (endpoint, result) in enumerate(zip(endpoints, results), 1):
            status = "[OK]" if result['success'] else "[FAIL]"
            report_content += f"| {i} | {endpoint['method']} | {endpoint['path']} | {status} | {result['duration_ms']}ms | {result['classification']} |\n"
        
        report_content += f"\n## 분류별 통계\n\n"
        
        # 분류별 통계
        classifications = {}
        for result in results:
            cls = result['classification']
            classifications[cls] = classifications.get(cls, 0) + 1
        
        for cls, count in classifications.items():
            report_content += f"- **{cls}**: {count}개\n"
        
        with open(f'report_batch_{batch_number}.md', 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def generate_cumulative_report(self):
        """누적 리포트 생성"""
        with open('master_list.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        endpoints = master_data['endpoints']
        tested_endpoints = [ep for ep in endpoints if ep.get('tested', False)]
        
        if not tested_endpoints:
            return
        
        total_count = len(endpoints)
        tested_count = len(tested_endpoints)
        success_count = sum(1 for ep in tested_endpoints if ep.get('test_result', {}).get('success', False))
        
        report_content = f"""# 누적 테스트 리포트

## 전체 요약
- **생성 시간**: {datetime.now().isoformat()}
- **전체 엔드포인트**: {total_count}개
- **테스트 완료**: {tested_count}개
- **테스트 성공**: {success_count}개
- **테스트 진행률**: {(tested_count / total_count * 100):.1f}%
- **성공률**: {(success_count / tested_count * 100):.1f}% (테스트 완료 기준)

## 분류별 통계

"""
        
        # 분류별 통계
        classifications = {}
        for endpoint in tested_endpoints:
            result = endpoint.get('test_result', {})
            cls = result.get('classification', 'unknown')
            classifications[cls] = classifications.get(cls, 0) + 1
        
        for cls, count in classifications.items():
            percentage = (count / tested_count * 100) if tested_count > 0 else 0
            report_content += f"- **{cls}**: {count}개 ({percentage:.1f}%)\n"
        
        report_content += f"\n## 태그별 통계\n\n"
        
        # 태그별 통계
        tag_stats = {}
        for endpoint in tested_endpoints:
            tags = endpoint.get('tags', ['기타'])
            for tag in tags:
                if tag not in tag_stats:
                    tag_stats[tag] = {'total': 0, 'success': 0}
                tag_stats[tag]['total'] += 1
                if endpoint.get('test_result', {}).get('success', False):
                    tag_stats[tag]['success'] += 1
        
        for tag, stats in tag_stats.items():
            success_rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            report_content += f"- **{tag}**: {stats['success']}/{stats['total']} ({success_rate:.1f}%)\n"
        
        with open('report_all.md', 'w', encoding='utf-8') as f:
            f.write(report_content)

def main():
    """
    메인 함수
    """
    tester = APITester(batch_size=10)
    
    # 다음 배치 번호 계산
    with open('master_list.json', 'r', encoding='utf-8') as f:
        master_data = json.load(f)
    
    endpoints = master_data['endpoints']
    tested_count = sum(1 for ep in endpoints if ep.get('tested', False))
    batch_number = (tested_count // 10) + 1
    
    result = tester.run_batch_test(batch_number=batch_number)
    
    print(f"\nREMAINING={result['remaining']}")

if __name__ == "__main__":
    main()
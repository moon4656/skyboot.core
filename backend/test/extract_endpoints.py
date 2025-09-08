import json
import os
from datetime import datetime

def extract_endpoints_from_openapi():
    """OpenAPI JSON에서 모든 엔드포인트를 추출하여 master_list.json 생성"""
    
    # OpenAPI JSON 파일 읽기
    with open('openapi.json', 'r', encoding='utf-8') as f:
        openapi_data = json.load(f)
    
    endpoints = []
    paths = openapi_data.get('paths', {})
    
    # 각 경로와 메소드 추출
    for path, methods in paths.items():
        for method, details in methods.items():
            if method.lower() in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                endpoint = {
                    'method': method.upper(),
                    'path': path,
                    'summary': details.get('summary', ''),
                    'description': details.get('description', ''),
                    'tags': details.get('tags', []),
                    'operationId': details.get('operationId', ''),
                    'security': details.get('security', []),
                    'parameters': details.get('parameters', []),
                    'requestBody': details.get('requestBody', {}),
                    'responses': details.get('responses', {}),
                    'tested': False,
                    'test_result': None,
                    'test_timestamp': None
                }
                endpoints.append(endpoint)
    
    # master_list.json 생성
    master_list = {
        'generated_at': datetime.now().isoformat(),
        'total_endpoints': len(endpoints),
        'endpoints': endpoints
    }
    
    with open('master_list.json', 'w', encoding='utf-8') as f:
        json.dump(master_list, f, ensure_ascii=False, indent=2)
    
    print(f"총 {len(endpoints)}개의 엔드포인트를 추출했습니다.")
    print("master_list.json 파일이 생성되었습니다.")
    
    # 엔드포인트 목록 출력
    print("\n=== 추출된 엔드포인트 목록 ===")
    for i, endpoint in enumerate(endpoints, 1):
        print(f"{i:3d}. {endpoint['method']:6s} {endpoint['path']}")
    
    return endpoints

if __name__ == "__main__":
    endpoints = extract_endpoints_from_openapi()
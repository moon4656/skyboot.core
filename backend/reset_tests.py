#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
테스트 상태 리셋 스크립트
모든 엔드포인트의 tested 플래그를 false로 변경합니다.
"""

import json

def reset_test_status():
    """모든 엔드포인트의 테스트 상태를 리셋합니다."""
    try:
        # master_list.json 파일 읽기
        with open('master_list.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 모든 엔드포인트의 tested 플래그를 false로 변경
        reset_count = 0
        for endpoint in data['endpoints']:
            if endpoint.get('tested', False):
                endpoint['tested'] = False
                # test_result 필드도 제거
                if 'test_result' in endpoint:
                    del endpoint['test_result']
                reset_count += 1
        
        # 파일에 다시 저장
        with open('master_list.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"[SUCCESS] {reset_count}개 엔드포인트의 테스트 상태가 리셋되었습니다.")
        print(f"총 엔드포인트 수: {len(data['endpoints'])}")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {str(e)}")

if __name__ == "__main__":
    reset_test_status()
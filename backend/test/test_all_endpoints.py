#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전체 엔드포인트 테스트 실행 스크립트
"""

import json
import subprocess
import sys
import time
from datetime import datetime

def get_remaining_count():
    """남은 엔드포인트 수 확인"""
    try:
        with open('master_list.json', 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        endpoints = master_data['endpoints']
        remaining = sum(1 for ep in endpoints if not ep.get('tested', False))
        return remaining
    except FileNotFoundError:
        return 0

def run_single_batch():
    """단일 배치 테스트 실행"""
    try:
        # Windows 환경에서 한국어 출력 처리를 위해 cp949 인코딩 사용
        result = subprocess.run(
            [sys.executable, 'api_tester.py'],
            capture_output=True,
            text=True,
            encoding='cp949',
            errors='ignore'  # 디코딩 오류 무시
        )
        
        if result.returncode == 0:
            # REMAINING= 값 추출
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.startswith('REMAINING='):
                    return int(line.split('=')[1])
        else:
            # 에러 출력 표시 (디버깅용)
            if result.stderr:
                print(f"[WARNING] 배치 실행 경고: {result.stderr[:200]}...")
        
        return 0
    except UnicodeDecodeError as e:
        print(f"[ERROR] 인코딩 오류: {e}")
        # UTF-8로 재시도
        try:
            result = subprocess.run(
                [sys.executable, 'api_tester.py'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.startswith('REMAINING='):
                        return int(line.split('=')[1])
        except Exception:
            pass
        return 0
    except Exception as e:
        print(f"[ERROR] 배치 실행 중 오류: {e}")
        return 0

def main():
    """전체 엔드포인트 테스트 실행"""
    print("[START] 전체 엔드포인트 테스트 시작")
    print(f"[TIME] 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    batch_count = 0
    total_start_time = time.time()
    
    while True:
        remaining = get_remaining_count()
        
        if remaining == 0:
            print("\n[SUCCESS] 모든 엔드포인트 테스트가 완료되었습니다!")
            break
        
        batch_count += 1
        print(f"\n[BATCH] 배치 {batch_count} 실행 중... (남은 엔드포인트: {remaining}개)")
        
        batch_start_time = time.time()
        remaining_after = run_single_batch()
        batch_duration = time.time() - batch_start_time
        
        tested_in_batch = remaining - remaining_after
        print(f"   [OK] 배치 {batch_count} 완료: {tested_in_batch}개 테스트 ({batch_duration:.1f}초)")
        
        if remaining_after >= remaining:
            print("[ERROR] 더 이상 진행되지 않습니다. 테스트를 중단합니다.")
            break
        
        # 잠시 대기 (서버 부하 방지)
        time.sleep(1)
    
    total_duration = time.time() - total_start_time
    
    print("\n" + "=" * 60)
    print(f"[COMPLETE] 전체 테스트 완료!")
    print(f"[STATS] 총 배치 수: {batch_count}")
    print(f"[TIME] 총 소요 시간: {total_duration:.1f}초")
    print(f"[TIME] 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 최종 리포트 확인
    try:
        with open('report_all.md', 'r', encoding='utf-8') as f:
            content = f.read()
            # 성공률 추출
            for line in content.split('\n'):
                if '성공률' in line and '%' in line:
                    print(f"📈 {line.strip()}")
                    break
    except FileNotFoundError:
        print("📄 최종 리포트 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    main()
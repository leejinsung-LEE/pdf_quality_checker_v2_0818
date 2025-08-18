#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
워커 스레드 테스트 스크립트

PDF 처리 워커가 실제로 작동하는지 테스트합니다.
"""

import sys
import time
from pathlib import Path

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.processing.queue_manager import QueueManager, TaskType, TaskPriority
from src.utils.logger import setup_logger

def test_worker():
    """워커 테스트"""
    print("=== PDF Quality Checker Worker Test ===\n")
    
    # 로거 설정
    logger = setup_logger(Path("logs/test_worker.log"))
    
    # 큐 관리자 생성 (자동으로 워커 시작)
    print("1. 큐 관리자 초기화 중...")
    queue_manager = QueueManager(logger=logger, auto_start_workers=True, num_workers=2)
    print("   [OK] 큐 관리자 초기화 완료")
    
    # 워커 상태 확인
    worker_status = queue_manager.get_worker_status()
    if worker_status:
        print(f"   [OK] 워커 풀 시작됨: {worker_status['active_workers']}개 워커 활성화")
    else:
        print("   [ERROR] 워커 풀이 시작되지 않았습니다!")
        return
    
    # 테스트 PDF 파일 찾기
    print("\n2. 테스트 PDF 파일 찾기...")
    test_files = list(Path(".").glob("*.pdf"))
    if not test_files:
        test_files = list(Path("tests/fixtures").glob("*.pdf"))
    
    if test_files:
        test_file = test_files[0]
        print(f"   [OK] 테스트 파일: {test_file}")
    else:
        print("   [INFO] PDF 파일을 찾을 수 없습니다. 테스트용 PDF를 생성합니다...")
        # 간단한 테스트 PDF 생성
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        
        test_file = Path(__file__).parent.parent / "fixtures" / "test_sample.pdf"
        c = canvas.Canvas(str(test_file), pagesize=A4)
        c.drawString(100, 750, "Test PDF for Worker Testing")
        c.drawString(100, 700, "This is a sample PDF file")
        c.save()
        print(f"   [OK] 테스트 파일 생성: {test_file}")
    
    # 작업 추가
    print("\n3. 작업 큐에 작업 추가...")
    task_id = queue_manager.add_file_processing_task(
        file_path=test_file,
        profile="default",
        auto_fix=False,
        priority=TaskPriority.NORMAL
    )
    print(f"   [OK] 작업 추가됨: {task_id}")
    
    # 큐 상태 확인
    stats = queue_manager.get_statistics()
    print(f"   대기 중: {stats['pending']}, 처리 중: {stats['active']}")
    
    # 결과 대기
    print("\n4. 처리 결과 대기 중...")
    start_time = time.time()
    timeout = 30  # 30초 타임아웃
    
    while True:
        # 작업 상태 확인
        status = queue_manager.get_task_status(task_id)
        
        if status == 'completed':
            # 결과 가져오기
            result = queue_manager.get_task_result(task_id)
            processing_time = time.time() - start_time
            
            print(f"\n[SUCCESS] 작업 완료!")
            print(f"   처리 시간: {processing_time:.2f}초")
            print(f"   성공 여부: {result.success}")
            
            if result.success:
                print(f"   결과: {result.result}")
            else:
                print(f"   오류: {result.error}")
            
            break
        
        elif time.time() - start_time > timeout:
            print(f"\n[TIMEOUT] 타임아웃 ({timeout}초)")
            print(f"   작업 상태: {status}")
            break
        
        # 진행 상황 표시
        elapsed = time.time() - start_time
        print(f"\r   처리 중... ({elapsed:.1f}초) [상태: {status}]", end="")
        time.sleep(0.5)
    
    # 최종 통계
    print("\n\n5. 최종 통계:")
    final_stats = queue_manager.get_statistics()
    print(f"   총 작업: {final_stats['total_tasks']}")
    print(f"   완료: {final_stats['completed']}")
    print(f"   오류: {final_stats['errors']}")
    print(f"   성공률: {final_stats['success_rate']:.1f}%")
    
    worker_status = queue_manager.get_worker_status()
    if worker_status:
        print(f"\n   워커 상태:")
        for worker in worker_status['workers']:
            print(f"   - 워커 {worker['worker_id']}: 처리 {worker['processed_count']}개, 오류 {worker['error_count']}개")
    
    # 워커 중지
    print("\n6. 워커 중지...")
    queue_manager.stop_workers()
    print("   [OK] 워커 중지 완료")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    try:
        test_worker()
    except KeyboardInterrupt:
        print("\n\n테스트 중단됨")
    except Exception as e:
        print(f"\n\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
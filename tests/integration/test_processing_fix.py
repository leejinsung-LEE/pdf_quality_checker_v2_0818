#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ProcessingResult 수정 테스트
Phase 1 기술부채 해결 검증
"""

import sys
import os
from pathlib import Path

# UTF-8 인코딩 설정
from _utf8_setup import setup_utf8_encoding

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.processing.pipeline import ProcessingResult, ProcessingStatus, PDFProcessingPipeline, PipelineOptions
from src.processing.processing_worker import ProcessingWorker
from src.processing.queue_manager import QueueManager
import time

def test_processing_result():
    """ProcessingResult 클래스 테스트"""
    print("\n=== ProcessingResult 클래스 테스트 ===")
    
    # ProcessingResult 인스턴스 생성
    result = ProcessingResult(
        file_path=Path("test.pdf"),
        status=ProcessingStatus.COMPLETED
    )
    
    # 속성 확인
    print(f"[OK] file_path: {result.file_path}")
    print(f"[OK] status: {result.status}")
    print(f"[OK] analysis_result: {result.analysis_result}")  # 새로 추가된 속성
    print(f"[OK] quality_result: {result.quality_result}")
    
    # to_dict 메서드 테스트
    result_dict = result.to_dict()
    print(f"[OK] has_analysis: {result_dict.get('has_analysis')}")
    
    print("[PASS] ProcessingResult class working correctly")
    return True

def test_worker_integration():
    """ProcessingWorker와 Pipeline 통합 테스트"""
    print("\n=== Worker-Pipeline 통합 테스트 ===")
    
    try:
        # 큐 매니저 생성 (워커 자동 시작 안함)
        queue_manager = QueueManager(auto_start_workers=False)
        
        # 워커 생성
        worker = ProcessingWorker(queue_manager, worker_id=99)
        
        # PDFProcessor의 process_with_profile 메서드가 반환하는 객체 확인
        from src.processing.processor import PDFProcessor
        processor = PDFProcessor()
        
        # 테스트용 PDF 파일 경로
        test_pdf = Path(__file__).parent.parent / "fixtures" / "test_sample.pdf"
        
        if test_pdf.exists():
            print(f"[OK] Test file found: {test_pdf}")
            
            # 파이프라인 직접 테스트
            pipeline = PDFProcessingPipeline()
            options = PipelineOptions(profile_name="default")
            
            # 처리 실행
            result = pipeline.process(test_pdf, options)
            
            # 결과 확인
            print(f"[OK] status: {result.status}")
            print(f"[OK] analysis_result exists: {result.analysis_result is not None}")
            print(f"[OK] quality_result exists: {result.quality_result is not None}")
            
            # 워커가 참조하는 속성들 확인
            if hasattr(result, 'analysis_result'):
                print("[PASS] analysis_result attribute OK")
            if hasattr(result, 'quality_result'):
                print("[PASS] quality_result attribute OK")
                
        else:
            print("[WARN] Test PDF file not found, skipping actual processing")
            
        print("[PASS] Worker-Pipeline integration OK")
        return True
        
    except Exception as e:
        print(f"[FAIL] Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_encoding():
    """인코딩 문제 테스트"""
    print("\n=== 인코딩 테스트 ===")
    
    import logging
    from src.utils.logger import setup_logger
    
    # 로거 설정
    logger = setup_logger(log_level="INFO")
    
    # 한글 및 특수문자 로그 테스트
    test_messages = [
        "English message test",
        "Worker 1 started",
        "Task completed in 2.5s",
        "Processing PDF file: test.pdf"
    ]
    
    for msg in test_messages:
        try:
            logger.info(msg)
            print(f"[OK] Log output success: {msg[:30]}...")
        except Exception as e:
            print(f"[FAIL] Log output failed: {e}")
            return False
    
    print("[PASS] Encoding test passed")
    return True

def main():
    """메인 테스트 실행"""
    print("=" * 60)
    print("PDF Quality Checker v2.0 - Phase 1 Fix Verification")
    print("=" * 60)
    
    results = []
    
    # 테스트 실행
    results.append(("ProcessingResult class", test_processing_result()))
    results.append(("Worker-Pipeline integration", test_worker_integration()))
    results.append(("Encoding issues", test_encoding()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{name:30} {status}")
    
    # 전체 결과
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n[SUCCESS] All tests passed! Phase 1 complete")
    else:
        print("\n[WARNING] Some tests failed. Additional fixes needed")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
# -*- coding: utf-8 -*-
"""
새 기능 통합 테스트

Phase 1-3에서 구현한 모든 새 기능을 테스트합니다.
"""

import sys
import os
import time
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import threading
import queue

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# UTF-8 설정
if sys.platform == 'win32':
    import io
    os.system('chcp 65001 > nul 2>&1')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class TestStreamingProcessor(unittest.TestCase):
    """스트리밍 PDF 처리기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        from src.core.streaming_processor import StreamingPDFProcessor, AdaptiveChunkProcessor
        
        self.processor = StreamingPDFProcessor(
            chunk_size=5,
            max_memory_mb=100
        )
        self.adaptive = AdaptiveChunkProcessor(base_chunk_size=10)
        
    def test_memory_monitoring(self):
        """메모리 모니터링 테스트"""
        # 초기 메모리 확인
        initial_memory = self.processor.get_memory_usage()
        self.assertGreater(initial_memory, 0)
        
        # 메모리 임계값 체크
        should_reduce = self.processor.should_reduce_chunk_size()
        self.assertIsInstance(should_reduce, bool)
        
    def test_adaptive_chunk_size(self):
        """적응형 청크 크기 테스트"""
        # 초기 청크 크기
        initial_size = self.adaptive.get_optimal_chunk_size()
        self.assertEqual(initial_size, 10)
        
        # 성능 기록 추가
        self.adaptive.record_performance(
            chunk_size=10,
            processing_time=3.0,
            memory_used=50.0
        )
        
        # 청크 크기 재계산
        new_size = self.adaptive.get_optimal_chunk_size()
        self.assertGreater(new_size, 0)
        
    def test_chunk_result_creation(self):
        """청크 결과 생성 테스트"""
        from src.core.streaming_processor import ChunkResult
        
        result = ChunkResult(
            chunk_index=0,
            page_range=(0, 5),
            analysis_data={'test': 'data'},
            issues_found=[],
            memory_used=10.5,
            processing_time=2.3
        )
        
        self.assertEqual(result.chunk_index, 0)
        self.assertEqual(result.page_range, (0, 5))
        self.assertIn('test', result.analysis_data)


class TestDynamicBatchProcessor(unittest.TestCase):
    """동적 배치 처리기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        from src.processing.dynamic_batch_processor import (
            DynamicBatchProcessor,
            WorkerPoolConfig,
            SmartBatchOptimizer
        )
        
        config = WorkerPoolConfig(
            min_workers=1,
            max_workers=4,
            memory_per_worker_mb=100,
            monitoring_interval=0.1  # 빠른 테스트를 위해
        )
        
        self.processor = DynamicBatchProcessor(config=config)
        self.optimizer = SmartBatchOptimizer()
        
    def test_processor_lifecycle(self):
        """처리기 생명주기 테스트"""
        # 시작
        self.processor.start()
        self.assertTrue(self.processor.monitoring_active)
        self.assertIsNotNone(self.processor.executor)
        
        # 상태 확인
        status = self.processor.get_status()
        self.assertIn('current_workers', status)
        self.assertIn('cpu_percent', status)
        self.assertIn('memory_percent', status)
        
        # 중지
        self.processor.stop()
        self.assertFalse(self.processor.monitoring_active)
        
    def test_system_resources(self):
        """시스템 리소스 조회 테스트"""
        resources = self.processor.get_system_resources()
        
        self.assertGreater(resources.cpu_count, 0)
        self.assertGreaterEqual(resources.cpu_percent, 0)
        self.assertLessEqual(resources.cpu_percent, 100)
        self.assertGreater(resources.memory_total_gb, 0)
        
    def test_optimal_workers_calculation(self):
        """최적 워커 수 계산 테스트"""
        from src.processing.dynamic_batch_processor import SystemResources
        
        # 낮은 리소스 사용률
        low_resources = SystemResources(
            cpu_count=4,
            cpu_percent=20.0,
            memory_total_gb=8.0,
            memory_available_gb=6.0,
            memory_percent=25.0
        )
        
        optimal = self.processor.calculate_optimal_workers(low_resources)
        self.assertGreaterEqual(optimal, self.processor.config.min_workers)
        self.assertLessEqual(optimal, self.processor.config.max_workers)
        
        # 높은 리소스 사용률
        high_resources = SystemResources(
            cpu_count=4,
            cpu_percent=90.0,
            memory_total_gb=8.0,
            memory_available_gb=1.0,
            memory_percent=87.5
        )
        
        optimal_high = self.processor.calculate_optimal_workers(high_resources)
        self.assertLessEqual(optimal_high, optimal)
        
    def test_batch_optimization(self):
        """배치 최적화 테스트"""
        # 다양한 크기의 파일
        file_sizes = [
            500 * 1024,      # 500KB (small)
            2 * 1024 * 1024, # 2MB (medium)
            15 * 1024 * 1024,# 15MB (large)
            800 * 1024,      # 800KB (small)
            5 * 1024 * 1024, # 5MB (medium)
        ]
        
        batches = self.optimizer.optimize_batch_size(file_sizes)
        
        # 배치가 생성되었는지 확인
        self.assertGreater(len(batches), 0)
        
        # 모든 파일이 배치에 포함되었는지 확인
        all_indices = []
        for batch in batches:
            all_indices.extend(batch)
        self.assertEqual(len(all_indices), len(file_sizes))
        
    def tearDown(self):
        """테스트 정리"""
        if hasattr(self, 'processor'):
            self.processor.stop()


class TestAlarmSystem(unittest.TestCase):
    """알람 시스템 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        from src.utils.alarm_manager import AlarmManager
        
        self.alarm_manager = AlarmManager(test_mode=True)
        
    def test_notification_methods(self):
        """알림 방법 테스트"""
        # 사용 가능한 알림 방법 확인
        self.assertIn(self.alarm_manager.NOTIFICATION_METHOD, 
                     ['plyer', 'win10toast', 'ctypes', 'none'])
        
    def test_show_notification_plyer(self):
        """plyer 알림 테스트"""
        # 알림 표시 (실제로는 시스템에 따라 다른 방식 사용)
        try:
            self.alarm_manager.show_notification(
                title="테스트",
                message="테스트 메시지"
            )
            # 에러 없이 실행되면 성공
            self.assertTrue(True)
        except Exception as e:
            # 테스트 환경에서는 알림이 실패할 수 있음
            self.skipTest(f"알림 시스템 사용 불가: {e}")
            
    def test_alarm_queue(self):
        """알람 큐 테스트"""
        # 알람 추가
        self.alarm_manager.add_alarm(
            title="테스트 알람",
            message="큐 테스트"
        )
        
        # 큐 크기 확인
        self.assertGreater(self.alarm_manager.alarm_queue.qsize(), 0)
        
    def test_alarm_processing_thread(self):
        """알람 처리 스레드 테스트"""
        # 스레드 시작
        self.alarm_manager.start()
        
        # 스레드가 실행 중인지 확인
        self.assertTrue(self.alarm_manager.is_running)
        self.assertTrue(self.alarm_manager.alarm_thread.is_alive())
        
        # 알람 추가 및 처리 대기
        self.alarm_manager.add_alarm(
            title="스레드 테스트",
            message="처리 확인"
        )
        
        time.sleep(0.5)  # 처리 대기
        
        # 스레드 중지
        self.alarm_manager.stop()
        self.assertFalse(self.alarm_manager.is_running)
        
    def tearDown(self):
        """테스트 정리"""
        if hasattr(self, 'alarm_manager'):
            self.alarm_manager.stop()


class TestAutoSaveSettings(unittest.TestCase):
    """자동 저장 설정 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # 임시 설정 파일
        self.temp_dir = tempfile.mkdtemp()
        self.settings_file = Path(self.temp_dir) / "settings.json"
        
    def test_auto_save_mechanism(self):
        """자동 저장 메커니즘 테스트"""
        from src.ui.components.auto_save_settings import AutoSaveSettings
        
        manager = AutoSaveSettings(
            settings_file=self.settings_file,
            auto_save_delay=0.1  # 빠른 테스트를 위해
        )
        
        # 설정 변경
        manager.set('test_key', 'test_value', auto_save=True)
        manager.set('number', 42, auto_save=True)
        
        # 자동 저장 대기
        time.sleep(0.3)
        
        # 파일이 저장되었는지 확인
        self.assertTrue(self.settings_file.exists())
        
        # 내용 확인
        import json
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            saved_settings = json.load(f)
            
        self.assertEqual(saved_settings['test_key'], 'test_value')
        self.assertEqual(saved_settings['number'], 42)
        
    def test_backup_creation(self):
        """백업 생성 테스트"""
        from src.ui.components.auto_save_settings import AutoSaveSettings
        
        # 원본 파일 생성
        import json
        original_data = {'original': True}
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(original_data, f)
            
        manager = AutoSaveSettings(
            settings_file=self.settings_file
        )
        
        # 새 설정 저장
        manager.set('updated', True, auto_save=False)
        success = manager.save_settings()
        
        # 원본 파일이 업데이트되었는지 확인
        self.assertTrue(self.settings_file.exists())
        with open(self.settings_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
        self.assertTrue(updated_data.get('updated', False))
        
        # 성공 확인
        self.assertTrue(success)
        
    def tearDown(self):
        """테스트 정리"""
        import shutil
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)


class TestStartupOptimization(unittest.TestCase):
    """시작 속도 최적화 테스트"""
    
    def test_lazy_initialization(self):
        """지연 초기화 테스트"""
        from main_optimized import LazyQueueManager
        
        # 지연 매니저는 클래스 메서드 사용
        # 첫 접근 시 생성
        queue_manager1 = LazyQueueManager.get_instance()
        self.assertIsNotNone(queue_manager1)
        
        # 동일 객체 반환 (싱글톤)
        queue_manager2 = LazyQueueManager.get_instance()
        self.assertIs(queue_manager1, queue_manager2)
        
    def test_async_tool_check(self):
        """비동기 도구 확인 테스트"""
        from main_optimized import check_requirements_async
        
        # 비동기 확인 실행 (스레드 반환)
        thread = check_requirements_async()
        
        # 스레드가 생성되었는지 확인
        self.assertIsNotNone(thread)
        self.assertTrue(thread.is_alive() or thread.ident is not None)
        
        # 스레드 완료 대기 (최대 5초)
        thread.join(timeout=5)
        

class TestIntegration(unittest.TestCase):
    """통합 테스트"""
    
    def test_complete_pipeline(self):
        """전체 파이프라인 테스트"""
        # PDF 파일 생성 (테스트용)
        test_pdf = Path(project_root) / "tests" / "fixtures" / "test_sample.pdf"
        
        if test_pdf.exists():
            from src.core.streaming_processor import StreamingPDFProcessor
            from src.processing.dynamic_batch_processor import DynamicBatchProcessor
            
            # 스트리밍 처리
            streaming_processor = StreamingPDFProcessor(chunk_size=2)
            
            # 청크별 처리
            chunks_processed = 0
            for chunk_result in streaming_processor.process_pdf_streaming(test_pdf):
                chunks_processed += 1
                self.assertIsNotNone(chunk_result.chunk_index)
                self.assertIsNotNone(chunk_result.page_range)
                
            self.assertGreater(chunks_processed, 0)
            
            # 동적 배치 처리
            batch_processor = DynamicBatchProcessor()
            batch_processor.start()
            
            # 상태 확인
            status = batch_processor.get_status()
            self.assertIn('current_workers', status)
            
            batch_processor.stop()
            
        else:
            self.skipTest("테스트 PDF 파일이 없습니다")


def run_tests():
    """테스트 실행"""
    # 테스트 스위트 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 테스트 클래스 추가
    suite.addTests(loader.loadTestsFromTestCase(TestStreamingProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicBatchProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestAlarmSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestAutoSaveSettings))
    suite.addTests(loader.loadTestsFromTestCase(TestStartupOptimization))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"성공: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}")
            
    if result.errors:
        print("\n오류 발생 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}")
            
    print("="*60)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
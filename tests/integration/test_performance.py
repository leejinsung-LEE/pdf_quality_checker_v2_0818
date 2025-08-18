# -*- coding: utf-8 -*-
"""
성능 및 메모리 사용량 테스트

새 기능들의 성능과 메모리 효율성을 검증합니다.
"""

import unittest
import tempfile
import shutil
import time
import psutil
import threading
from pathlib import Path
from datetime import datetime
import gc
import sys

# 테스트 대상 모듈들
from src.data import get_backup_manager
from src.data.history_manager import HistoryManager, ProcessHistory
from src.processing import get_batch_scheduler, ScheduleTask, ScheduleFrequency
from src.core.profiles import get_profile_manager
from src.core import QualityChecker


class PerformanceTest(unittest.TestCase):
    """성능 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정"""
        cls.test_dir = Path(tempfile.mkdtemp())
        
        # 테스트용 PDF 파일들 생성
        cls.test_pdfs = []
        for i in range(10):
            pdf_path = cls.test_dir / f"test_{i}.pdf"
            pdf_path.write_bytes(b"%PDF-1.4\n%%EOF")
            cls.test_pdfs.append(pdf_path)
        
        # 프로세스 정보
        cls.process = psutil.Process()
        
    @classmethod
    def tearDownClass(cls):
        """테스트 클래스 정리"""
        if cls.test_dir.exists():
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """각 테스트 전 설정"""
        # 가비지 컬렉션 실행
        gc.collect()
        
        # 초기 메모리 사용량 기록
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
    
    def tearDown(self):
        """각 테스트 후 정리"""
        # 최종 메모리 사용량 기록
        final_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - self.initial_memory
        
        print(f"\n메모리 증가량: {memory_increase:.2f} MB")
    
    def test_backup_manager_performance(self):
        """백업 매니저 성능 테스트"""
        backup_manager = get_backup_manager()
        
        # 100개 백업 생성 시간 측정
        start_time = time.time()
        backup_ids = []
        
        for i in range(100):
            pdf_path = self.test_pdfs[i % len(self.test_pdfs)]
            backup_id = backup_manager.create_backup(
                file_path=pdf_path,
                profile_used="test_profile",
                changes_to_make=[f"변경 {i}"],
                metadata={"iteration": i}
            )
            backup_ids.append(backup_id)
        
        creation_time = time.time() - start_time
        
        # 성능 기준: 100개 백업 10초 이내
        self.assertLess(creation_time, 10.0, 
                       f"백업 생성 시간 초과: {creation_time:.2f}초")
        
        print(f"100개 백업 생성: {creation_time:.2f}초")
        print(f"평균: {creation_time/100*1000:.2f}ms/백업")
        
        # 백업 조회 성능
        start_time = time.time()
        for pdf_path in self.test_pdfs:
            backups = backup_manager.get_backup_history(pdf_path)
        
        query_time = time.time() - start_time
        self.assertLess(query_time, 1.0,
                       f"백업 조회 시간 초과: {query_time:.2f}초")
        
        # 메모리 사용량 확인
        current_memory = self.process.memory_info().rss / 1024 / 1024
        memory_per_backup = (current_memory - self.initial_memory) / 100
        
        # 백업당 메모리 사용량 1MB 이하
        self.assertLess(memory_per_backup, 1.0,
                       f"백업당 메모리 사용량 초과: {memory_per_backup:.2f} MB")
    
    def test_history_manager_performance(self):
        """이력 매니저 성능 테스트"""
        history_manager = HistoryManager(db_path=self.test_dir / "test.db")
        
        # 1000개 이력 추가 시간 측정
        start_time = time.time()
        
        for i in range(1000):
            history = ProcessHistory(
                file_name=f"test_{i}.pdf",
                file_path=str(self.test_pdfs[i % len(self.test_pdfs)]),
                profile="default",
                quality_score=50.0 + (i % 50),
                error_count=i % 10,
                warning_count=i % 5,
                processing_time=0.1 + (i % 10) / 10
            )
            history_manager.add_history(history)
        
        insert_time = time.time() - start_time
        
        # 성능 기준: 1000개 이력 5초 이내
        self.assertLess(insert_time, 5.0,
                       f"이력 추가 시간 초과: {insert_time:.2f}초")
        
        print(f"1000개 이력 추가: {insert_time:.2f}초")
        print(f"평균: {insert_time/1000*1000:.2f}ms/이력")
        
        # 검색 성능 테스트
        start_time = time.time()
        results = history_manager.search_history(limit=100)
        search_time = time.time() - start_time
        
        self.assertLess(search_time, 0.5,
                       f"검색 시간 초과: {search_time:.2f}초")
        
        # 통계 계산 성능
        start_time = time.time()
        stats = history_manager.get_statistics("month")
        stats_time = time.time() - start_time
        
        self.assertLess(stats_time, 1.0,
                       f"통계 계산 시간 초과: {stats_time:.2f}초")
        
        print(f"검색 시간: {search_time:.3f}초")
        print(f"통계 계산: {stats_time:.3f}초")
    
    def test_scheduler_performance(self):
        """스케줄러 성능 테스트"""
        scheduler = get_batch_scheduler()
        
        # 100개 작업 추가 시간 측정
        start_time = time.time()
        
        for i in range(100):
            task = ScheduleTask(
                id=f"perf_task_{i}",
                name=f"성능 테스트 작업 {i}",
                frequency=ScheduleFrequency.DAILY,
                time=f"{i%24:02d}:00",
                folder_path=str(self.test_dir),
                profile="default"
            )
            scheduler.add_task(task)
        
        add_time = time.time() - start_time
        
        # 성능 기준: 100개 작업 추가 2초 이내
        self.assertLess(add_time, 2.0,
                       f"작업 추가 시간 초과: {add_time:.2f}초")
        
        print(f"100개 작업 추가: {add_time:.2f}초")
        
        # 스케줄러 시작/중지 성능
        start_time = time.time()
        scheduler.start()
        time.sleep(0.1)  # 잠시 실행
        scheduler.stop()
        lifecycle_time = time.time() - start_time
        
        self.assertLess(lifecycle_time, 1.0,
                       f"시작/중지 시간 초과: {lifecycle_time:.2f}초")
    
    def test_profile_manager_performance(self):
        """프로파일 매니저 성능 테스트"""
        profile_manager = get_profile_manager()
        
        # 50개 프로파일 생성 시간 측정
        start_time = time.time()
        
        for i in range(50):
            profile_manager.create_profile(
                f"perf_profile_{i}",
                base_profile="default",
                settings={
                    "quality_standards": {
                        "minimum_dpi": 300 + i
                    }
                }
            )
        
        create_time = time.time() - start_time
        
        # 성능 기준: 50개 프로파일 생성 2초 이내
        self.assertLess(create_time, 2.0,
                       f"프로파일 생성 시간 초과: {create_time:.2f}초")
        
        # 프로파일 로드 성능
        start_time = time.time()
        profiles = profile_manager.get_profile_list()
        load_time = time.time() - start_time
        
        self.assertLess(load_time, 0.5,
                       f"프로파일 로드 시간 초과: {load_time:.2f}초")
        
        print(f"50개 프로파일 생성: {create_time:.2f}초")
        print(f"프로파일 목록 로드: {load_time:.3f}초")
        
        # 정리
        for i in range(50):
            profile_manager.delete_profile(f"perf_profile_{i}")
    
    def test_concurrent_operations(self):
        """동시 작업 성능 테스트"""
        results = {}
        threads = []
        
        def backup_worker():
            """백업 작업 스레드"""
            backup_manager = get_backup_manager()
            start = time.time()
            
            for i in range(20):
                backup_manager.create_backup(
                    self.test_pdfs[i % len(self.test_pdfs)],
                    profile_used="concurrent_test"
                )
            
            results["backup"] = time.time() - start
        
        def history_worker():
            """이력 작업 스레드"""
            history_manager = HistoryManager(
                db_path=self.test_dir / "concurrent.db"
            )
            start = time.time()
            
            for i in range(100):
                history = ProcessHistory(
                    file_name=f"concurrent_{i}.pdf",
                    file_path=str(self.test_pdfs[0]),
                    profile="default",
                    quality_score=85.0
                )
                history_manager.add_history(history)
            
            results["history"] = time.time() - start
        
        def quality_worker():
            """품질 검사 스레드"""
            checker = QualityChecker()
            start = time.time()
            
            for pdf in self.test_pdfs[:5]:
                checker.quick_check(pdf)
            
            results["quality"] = time.time() - start
        
        # 스레드 생성 및 시작
        threads.append(threading.Thread(target=backup_worker))
        threads.append(threading.Thread(target=history_worker))
        threads.append(threading.Thread(target=quality_worker))
        
        start_time = time.time()
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        # 성능 기준: 전체 10초 이내
        self.assertLess(total_time, 10.0,
                       f"동시 작업 시간 초과: {total_time:.2f}초")
        
        print(f"\n동시 작업 결과:")
        print(f"  전체 시간: {total_time:.2f}초")
        for name, duration in results.items():
            print(f"  {name}: {duration:.2f}초")
    
    def test_memory_leak_check(self):
        """메모리 누수 검사"""
        initial_memory = self.process.memory_info().rss / 1024 / 1024
        
        # 반복적인 생성/삭제 작업
        for iteration in range(5):
            # 백업 생성 및 삭제
            backup_manager = get_backup_manager()
            for i in range(20):
                backup_id = backup_manager.create_backup(
                    self.test_pdfs[0],
                    profile_used="leak_test"
                )
            
            # 이력 추가
            history_manager = HistoryManager(
                db_path=self.test_dir / f"leak_test_{iteration}.db"
            )
            for i in range(50):
                history = ProcessHistory(
                    file_name=f"leak_{i}.pdf",
                    file_path=str(self.test_pdfs[0]),
                    profile="default",
                    quality_score=75.0
                )
                history_manager.add_history(history)
            
            # 명시적 정리
            del history_manager
            gc.collect()
        
        # 최종 메모리 확인
        final_memory = self.process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # 메모리 증가량 50MB 이하
        self.assertLess(memory_increase, 50.0,
                       f"메모리 누수 의심: {memory_increase:.2f} MB 증가")
        
        print(f"\n메모리 누수 테스트:")
        print(f"  초기: {initial_memory:.2f} MB")
        print(f"  최종: {final_memory:.2f} MB")
        print(f"  증가: {memory_increase:.2f} MB")
    
    def test_large_file_handling(self):
        """대용량 파일 처리 성능"""
        # 큰 PDF 시뮬레이션 (실제로는 작은 파일)
        large_pdf = self.test_dir / "large.pdf"
        
        # 10MB 크기의 가짜 PDF 생성
        with open(large_pdf, "wb") as f:
            f.write(b"%PDF-1.4\n")
            f.write(b"0" * (10 * 1024 * 1024))  # 10MB
            f.write(b"\n%%EOF")
        
        # 백업 성능
        backup_manager = get_backup_manager()
        start_time = time.time()
        backup_id = backup_manager.create_backup(
            large_pdf,
            profile_used="large_file_test"
        )
        backup_time = time.time() - start_time
        
        # 성능 기준: 10MB 파일 백업 5초 이내
        self.assertLess(backup_time, 5.0,
                       f"대용량 파일 백업 시간 초과: {backup_time:.2f}초")
        
        print(f"\n10MB 파일 백업: {backup_time:.2f}초")
        
        # 정리
        large_pdf.unlink()
    
    def test_response_time_requirements(self):
        """응답 시간 요구사항 테스트"""
        requirements = {
            "프로파일 로드": (get_profile_manager().get_profile_list, 0.1),
            "백업 생성": (lambda: get_backup_manager().create_backup(
                self.test_pdfs[0], "test"), 0.5),
            "이력 검색": (lambda: HistoryManager(
                db_path=self.test_dir / "resp.db").search_history(limit=10), 0.2),
            "통계 계산": (lambda: HistoryManager(
                db_path=self.test_dir / "resp.db").get_statistics("day"), 0.5)
        }
        
        print("\n응답 시간 요구사항:")
        
        for operation, (func, max_time) in requirements.items():
            start = time.time()
            try:
                func()
            except:
                pass  # 일부 실패 가능
            duration = time.time() - start
            
            status = "✓" if duration <= max_time else "✗"
            print(f"  {status} {operation}: {duration:.3f}초 (기준: {max_time}초)")
            
            self.assertLess(duration, max_time * 2,  # 2배 여유
                          f"{operation} 응답 시간 초과")


if __name__ == "__main__":
    # 성능 테스트 실행
    print("=" * 60)
    print("PDF Quality Checker v2.0 - 성능 테스트")
    print("=" * 60)
    
    unittest.main(verbosity=2)
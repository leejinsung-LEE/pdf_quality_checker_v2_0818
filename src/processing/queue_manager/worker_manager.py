# src/processing/queue_manager/worker_manager.py
"""
워커 풀 관리
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
import logging
import atexit
import multiprocessing
import os

if TYPE_CHECKING:
    from ..processing_worker import WorkerPool


class WorkerManager:
    """워커 풀 관리자"""
    
    def __init__(self, 
                 queue_manager: Any,  # 순환 참조 방지를 위해 Any 사용
                 num_workers: Optional[int] = None,
                 auto_start: bool = True,
                 logger: Optional[logging.Logger] = None):
        """
        워커 관리자 초기화
        
        Args:
            queue_manager: 큐 관리자 인스턴스
            num_workers: 워커 수 (None이면 CPU 코어 기반 자동 설정)
            auto_start: 자동 시작 여부
            logger: 로거
        """
        self.queue_manager = queue_manager
        self.logger = logger or logging.getLogger(__name__)
        
        # 워커 수 결정 (CPU 코어 기반 동적 설정)
        if num_workers is None:
            # CPU 코어 수 확인
            cpu_count = multiprocessing.cpu_count()
            
            # 환경 변수로 오버라이드 가능
            if 'PDF_CHECKER_WORKERS' in os.environ:
                try:
                    num_workers = int(os.environ['PDF_CHECKER_WORKERS'])
                    self.logger.info(f"환경 변수에서 워커 수 설정: {num_workers}")
                except ValueError:
                    pass
            
            # 기본값: CPU 코어 수 - 1 (최소 2, 최대 8)
            if num_workers is None:
                num_workers = max(2, min(cpu_count - 1, 8))
                self.logger.info(f"CPU 코어 수 기반 워커 수 자동 설정: {num_workers} (CPU 코어: {cpu_count})")
        
        self.num_workers = num_workers
        
        # 워커 풀
        self.worker_pool: Optional['WorkerPool'] = None
        
        # 자동 시작
        if auto_start:
            self.start_workers()
            
            # atexit는 main.py에서 처리하므로 여기서는 등록하지 않음
            # 중복 정리 방지
    
    def start_workers(self):
        """워커 풀 시작"""
        if self.worker_pool is not None:
            self.logger.warning("워커 풀이 이미 실행 중입니다")
            return
        
        # WorkerPool import (순환 참조 방지를 위해 지연 import)
        from ..processing_worker import WorkerPool
        
        self.logger.info(f"워커 풀 시작 ({self.num_workers}개 워커)")
        self.worker_pool = WorkerPool(
            self.queue_manager, 
            self.num_workers, 
            self.logger
        )
        self.worker_pool.start()
    
    def stop_workers(self, timeout: float = 10.0):
        """워커 풀 중지"""
        if self.worker_pool is None:
            return
        
        self.logger.info("워커 풀 중지 중...")
        self.worker_pool.stop(timeout)
        self.worker_pool = None
        self.logger.info("워커 풀 중지됨")
    
    def get_worker_status(self) -> Optional[Dict[str, Any]]:
        """워커 풀 상태 조회"""
        if self.worker_pool:
            return self.worker_pool.get_status()
        return None
    
    def is_running(self) -> bool:
        """워커 풀 실행 중 여부"""
        return self.worker_pool is not None
    
    def restart_workers(self):
        """워커 풀 재시작"""
        self.stop_workers()
        self.start_workers()
        self.logger.info("워커 풀 재시작됨")
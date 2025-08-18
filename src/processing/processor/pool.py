# src/processing/processor/pool.py
"""
처리기 풀 - 다중 파일 동시 처리
"""

from typing import List, Optional, Callable
import threading
import logging

from .models import FileInfo
from .single_processor import PDFProcessor


class ProcessorPool:
    """
    처리기 풀 - 다중 파일 동시 처리용
    
    여러 개의 처리기를 관리하여 동시에 여러 파일을 처리합니다.
    """
    
    def __init__(self, max_workers: int = 3):
        """
        처리기 풀 초기화
        
        Args:
            max_workers: 최대 동시 처리 수
        """
        self.max_workers = max_workers
        self.processors: List[PDFProcessor] = []
        self.active_count = 0
        self.logger = logging.getLogger(__name__)
        
        # 프로세서 미리 생성
        for _ in range(max_workers):
            self.processors.append(PDFProcessor())
    
    def get_available_processor(self) -> Optional[PDFProcessor]:
        """
        사용 가능한 처리기 반환
        
        Returns:
            사용 가능한 처리기 또는 None
        """
        for processor in self.processors:
            if processor.get_processing_count() == 0:
                return processor
        return None
    
    def process_async(self,
                     file_info: FileInfo,
                     callback: Optional[Callable] = None):
        """
        비동기 처리 (스레드 사용)
        
        Args:
            file_info: 처리할 파일 정보
            callback: 완료 콜백 함수
            
        Raises:
            RuntimeError: 사용 가능한 처리기가 없을 때
        """
        processor = self.get_available_processor()
        if not processor:
            raise RuntimeError("사용 가능한 처리기가 없습니다")
        
        def process_thread():
            """처리 스레드 함수"""
            try:
                result = processor.process_file(
                    file_info.path,
                    file_info.file_id,
                    file_info.folder_config
                )
                if callback:
                    callback(file_info, result)
            except Exception as e:
                self.logger.error(f"처리 스레드 오류: {e}")
        
        thread = threading.Thread(target=process_thread, daemon=True)
        thread.start()
    
    def get_active_count(self) -> int:
        """
        활성 처리기 수 반환
        
        Returns:
            현재 파일을 처리 중인 처리기 수
        """
        return sum(1 for p in self.processors if p.get_processing_count() > 0)
    
    def wait_for_available(self, timeout: float = None) -> bool:
        """
        사용 가능한 처리기가 생길 때까지 대기
        
        Args:
            timeout: 최대 대기 시간 (초)
            
        Returns:
            사용 가능한 처리기가 있으면 True
        """
        import time
        start_time = time.time()
        
        while self.get_available_processor() is None:
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return True
    
    def get_processing_stats(self) -> dict:
        """
        처리 통계 반환
        
        Returns:
            처리기 풀 통계 정보
        """
        total_processing = sum(p.get_processing_count() for p in self.processors)
        available = sum(1 for p in self.processors if p.get_processing_count() == 0)
        
        return {
            'max_workers': self.max_workers,
            'active_workers': self.get_active_count(),
            'available_workers': available,
            'total_processing_files': total_processing
        }
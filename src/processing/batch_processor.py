# src/processing/batch_processor.py
"""
배치 처리 시스템

여러 PDF 파일을 효율적으로 일괄 처리하는 시스템
멀티스레드를 사용하여 동시에 여러 파일을 처리합니다.
"""

import threading
import queue
import time
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor, Future

from .processor import PDFProcessor, FileInfo
from .pipeline import ProcessingResult, ProcessingStatus, PipelineOptions
from ..core.profiles import get_profile_manager
from ..config import Config


# 커스텀 예외 클래스
class BatchProcessorError(Exception):
    """배치 처리 기본 예외"""
    pass


class BatchPreparationError(BatchProcessorError):
    """배치 준비 중 발생하는 예외"""
    pass


class WorkerPoolError(BatchProcessorError):
    """워커 풀 관련 예외"""
    pass


class BatchCancellationError(BatchProcessorError):
    """배치 취소 관련 예외"""
    pass


class BatchStatus(Enum):
    """배치 처리 상태"""
    IDLE = "idle"
    PREPARING = "preparing"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class ProcessingPriority(Enum):
    """처리 우선순위"""
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class BatchFile:
    """배치 처리 파일 정보"""
    file_id: str
    path: Path
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    folder_config: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 2
    
    def __lt__(self, other):
        """우선순위 비교 (큐 정렬용)"""
        return self.priority.value < other.priority.value


@dataclass
class BatchStatistics:
    """배치 처리 통계"""
    total_files: int = 0
    processed_files: int = 0
    success_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    auto_fixed_count: int = 0
    total_processing_time: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """성공률"""
        if self.processed_files == 0:
            return 0.0
        return (self.success_count / self.processed_files) * 100
    
    @property
    def average_time(self) -> float:
        """평균 처리 시간"""
        if self.processed_files == 0:
            return 0.0
        return self.total_processing_time / self.processed_files
    
    @property
    def elapsed_time(self) -> float:
        """경과 시간"""
        if not self.start_time:
            return 0.0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'total_files': self.total_files,
            'processed_files': self.processed_files,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'auto_fixed_count': self.auto_fixed_count,
            'success_rate': self.success_rate,
            'average_time': self.average_time,
            'elapsed_time': self.elapsed_time,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None
        }


class BatchProcessor:
    """
    배치 처리기
    
    여러 PDF 파일을 멀티스레드로 효율적으로 처리합니다.
    """
    
    def __init__(self, 
                 max_workers: int = 3,
                 logger: Optional[logging.Logger] = None):
        """
        배치 처리기 초기화
        
        Args:
            max_workers: 최대 워커 스레드 수
            logger: 로거
        """
        self.max_workers = max_workers
        self.logger = logger or logging.getLogger(__name__)
        
        # 큐 및 스레드 풀
        self.file_queue: queue.PriorityQueue = queue.PriorityQueue()
        self.result_queue: queue.Queue = queue.Queue()
        self.executor: Optional[ThreadPoolExecutor] = None
        
        # 상태 관리
        self.status = BatchStatus.IDLE
        self.statistics = BatchStatistics()
        self.current_files: Dict[str, BatchFile] = {}
        self.completed_files: Dict[str, ProcessingResult] = {}
        
        # 프로세서
        self.processor = PDFProcessor()
        
        # 콜백
        self.on_file_start: Optional[Callable] = None
        self.on_file_complete: Optional[Callable] = None
        self.on_file_error: Optional[Callable] = None
        self.on_progress: Optional[Callable] = None
        self.on_batch_complete: Optional[Callable] = None
        
        # 제어 플래그
        self._stop_flag = threading.Event()
        self._pause_flag = threading.Event()
    
    def set_callbacks(self,
                     on_file_start: Optional[Callable] = None,
                     on_file_complete: Optional[Callable] = None,
                     on_file_error: Optional[Callable] = None,
                     on_progress: Optional[Callable] = None,
                     on_batch_complete: Optional[Callable] = None):
        """
        콜백 함수 설정
        
        Args:
            on_file_start: 파일 처리 시작 (file_id, file_path)
            on_file_complete: 파일 처리 완료 (file_id, result)
            on_file_error: 파일 처리 오류 (file_id, error)
            on_progress: 진행률 업데이트 (file_id, status, progress, message)
            on_batch_complete: 배치 완료 (statistics)
        """
        self.on_file_start = on_file_start
        self.on_file_complete = on_file_complete
        self.on_file_error = on_file_error
        self.on_progress = on_progress
        self.on_batch_complete = on_batch_complete
        
        # 프로세서에 콜백 설정
        self.processor.set_callbacks(
            on_progress=self._handle_progress
        )
    
    def add_file(self, 
                file_path: Path,
                file_id: Optional[str] = None,
                priority: ProcessingPriority = ProcessingPriority.NORMAL,
                folder_config: Optional[Dict[str, Any]] = None):
        """
        처리할 파일 추가
        
        Args:
            file_path: PDF 파일 경로
            file_id: 파일 식별자
            priority: 처리 우선순위
            folder_config: 폴더 설정
        """
        if file_id is None:
            file_id = self._generate_file_id(file_path)
        
        batch_file = BatchFile(
            file_id=file_id,
            path=file_path,
            priority=priority,
            folder_config=folder_config
        )
        
        # 현재 파일 목록에 추가
        self.current_files[file_id] = batch_file
        
        # 큐에 추가
        self.file_queue.put(batch_file)
        self.statistics.total_files += 1
        
        self.logger.info(f"파일 추가: {file_path.name} (우선순위: {priority.name})")
    
    def add_files(self, 
                 file_paths: List[Path],
                 priority: ProcessingPriority = ProcessingPriority.NORMAL,
                 folder_config: Optional[Dict[str, Any]] = None):
        """여러 파일 추가"""
        for file_path in file_paths:
            self.add_file(file_path, priority=priority, folder_config=folder_config)
    
    def start(self):
        """배치 처리 시작"""
        if self.status != BatchStatus.IDLE:
            raise RuntimeError(f"이미 처리 중입니다: {self.status.value}")
        
        self.logger.info(f"배치 처리 시작: {self.statistics.total_files}개 파일")
        
        # 초기화
        self.status = BatchStatus.PROCESSING
        self.statistics.start_time = datetime.now()
        self._stop_flag.clear()
        self._pause_flag.clear()
        
        # 스레드 풀 생성
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        # 워커 스레드 시작
        for i in range(self.max_workers):
            future = self.executor.submit(self._worker, i)
            future.add_done_callback(self._worker_done)
    
    def pause(self):
        """일시 정지"""
        if self.status == BatchStatus.PROCESSING:
            self.status = BatchStatus.PAUSED
            self._pause_flag.set()
            self.logger.info("배치 처리 일시 정지")
    
    def resume(self):
        """재개"""
        if self.status == BatchStatus.PAUSED:
            self.status = BatchStatus.PROCESSING
            self._pause_flag.clear()
            self.logger.info("배치 처리 재개")
    
    def stop(self):
        """중지"""
        self._stop_flag.set()
        self.status = BatchStatus.CANCELLED
        
        # 스레드 풀 종료
        if self.executor:
            try:
                # Python 버전에 따라 다르게 처리
                import sys
                if sys.version_info >= (3, 9):
                    # Python 3.9+ 에서는 cancel_futures 사용 가능
                    self.executor.shutdown(wait=False, cancel_futures=True)
                else:
                    # Python 3.8 이하에서는 cancel_futures 사용 불가
                    self.executor.shutdown(wait=False)
            except TypeError as e:
                # cancel_futures 파라미터가 없는 경우
                self.logger.debug(f"Using fallback shutdown (Python < 3.9): {e}")
                try:
                    self.executor.shutdown(wait=False)
                except Exception as inner_e:
                    self.logger.debug(f"Executor shutdown error: {inner_e}")
            except Exception as e:
                self.logger.debug(f"Executor shutdown error (can be ignored): {e}")
            finally:
                self.executor = None
        
        # 큐 비우기
        while not self.file_queue.empty():
            try:
                self.file_queue.get_nowait()
            except queue.Empty:
                break
        
        self.logger.info("배치 처리 중지됨")
    
    def wait_completion(self, timeout: Optional[float] = None) -> bool:
        """
        처리 완료 대기
        
        Args:
            timeout: 대기 시간 제한
            
        Returns:
            bool: 완료 여부
        """
        if self.executor:
            try:
                # 안전한 종료 (Python 버전 무관)
                self.executor.shutdown(wait=True)
            except Exception as e:
                self.logger.debug(f"Executor shutdown error (can be ignored): {e}")
            finally:
                self.executor = None
            
        return self.status in [BatchStatus.COMPLETED, BatchStatus.CANCELLED]
    
    def _worker(self, worker_id: int):
        """워커 스레드"""
        self.logger.debug(f"워커 {worker_id} 시작")
        
        while not self._stop_flag.is_set():
            # 일시 정지 확인
            if self._pause_flag.is_set():
                time.sleep(0.1)
                continue
            
            try:
                # 큐에서 파일 가져오기
                batch_file = self.file_queue.get(timeout=1.0)
                
                # 처리
                self._process_file(batch_file, worker_id)
                
                # 큐 작업 완료
                self.file_queue.task_done()
                
            except queue.Empty:
                # 큐가 비었으면 처리 중인 파일이 있는지 확인
                with self.lock:
                    if self.file_queue.empty() and self.processing_count == 0:
                        break
            except Exception as e:
                self.logger.error(f"워커 {worker_id} 오류: {e}")
        
        self.logger.debug(f"워커 {worker_id} 종료")
    
    def _process_file(self, batch_file: BatchFile, worker_id: int):
        """파일 처리"""
        start_time = time.time()
        
        try:
            # 시작 콜백
            if self.on_file_start:
                self.on_file_start(batch_file.file_id, batch_file.path)
            
            self.logger.info(f"[워커 {worker_id}] 처리 시작: {batch_file.path.name}")
            
            # 처리 실행
            result = self.processor.process_file(
                batch_file.path,
                batch_file.file_id,
                batch_file.folder_config
            )
            
            # 통계 업데이트
            processing_time = time.time() - start_time
            self._update_statistics(result, processing_time)
            
            # 완료 파일 저장
            self.completed_files[batch_file.file_id] = result
            
            # 완료 콜백
            if self.on_file_complete:
                self.on_file_complete(batch_file.file_id, result)
            
            self.logger.info(
                f"[워커 {worker_id}] 처리 완료: {batch_file.path.name} "
                f"({processing_time:.1f}초)"
            )
            
        except Exception as e:
            # 재시도 확인
            if batch_file.retry_count < batch_file.max_retries:
                batch_file.retry_count += 1
                self.logger.warning(
                    f"처리 실패, 재시도 {batch_file.retry_count}/{batch_file.max_retries}: "
                    f"{batch_file.path.name}"
                )
                self.file_queue.put(batch_file)
            else:
                # 최종 실패
                self.statistics.error_count += 1
                self.statistics.processed_files += 1
                
                # 오류 콜백
                if self.on_file_error:
                    self.on_file_error(batch_file.file_id, str(e))
                
                self.logger.error(f"최종 처리 실패: {batch_file.path.name} - {e}")
    
    def _update_statistics(self, result: ProcessingResult, processing_time: float):
        """통계 업데이트"""
        self.statistics.processed_files += 1
        self.statistics.total_processing_time += processing_time
        
        if result.success:
            self.statistics.success_count += 1
        else:
            self.statistics.error_count += 1
        
        # 경고 카운트
        if result.has_warnings:
            self.statistics.warning_count += 1
        
        # 자동 수정 카운트
        if result.fix_result:
            self.statistics.auto_fixed_count += 1
    
    def _handle_progress(self, file_id: str, status: str, progress: int, message: str):
        """진행률 처리"""
        if self.on_progress:
            self.on_progress(file_id, status, progress, message)
    
    def _worker_done(self, future: Future):
        """워커 완료 처리"""
        try:
            future.result()
        except Exception as e:
            self.logger.error(f"워커 오류: {e}")
        
        # 모든 워커가 완료되었는지 확인
        if self.file_queue.empty() and self.statistics.processed_files >= self.statistics.total_files:
            self._complete_batch()
    
    def _complete_batch(self):
        """배치 처리 완료"""
        if self.status == BatchStatus.CANCELLED:
            return
        
        self.status = BatchStatus.COMPLETED
        self.statistics.end_time = datetime.now()
        
        self.logger.info(
            f"배치 처리 완료: "
            f"{self.statistics.success_count}/{self.statistics.total_files} 성공 "
            f"({self.statistics.elapsed_time:.1f}초)"
        )
        
        # 완료 콜백
        if self.on_batch_complete:
            self.on_batch_complete(self.statistics)
    
    def _generate_file_id(self, file_path: Path) -> str:
        """파일 ID 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        return f"{file_path.stem}_{timestamp}"
    
    def get_statistics(self) -> BatchStatistics:
        """현재 통계 반환"""
        return self.statistics
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            'status': self.status.value,
            'statistics': self.statistics.to_dict(),
            'queue_size': self.file_queue.qsize(),
            'processing_count': len(self.processor.processing_files),
            'completed_count': len(self.completed_files)
        }


class FilePriorityManager:
    """파일 우선순위 관리"""
    
    @staticmethod
    def sort_by_size_asc(files: List[Tuple[Path, Any]]) -> List[Tuple[Path, Any]]:
        """파일 크기 오름차순 (작은 파일 먼저)"""
        return sorted(files, key=lambda x: x[0].stat().st_size)
    
    @staticmethod
    def sort_by_size_desc(files: List[Tuple[Path, Any]]) -> List[Tuple[Path, Any]]:
        """파일 크기 내림차순 (큰 파일 먼저)"""
        return sorted(files, key=lambda x: x[0].stat().st_size, reverse=True)
    
    @staticmethod
    def sort_by_name(files: List[Tuple[Path, Any]]) -> List[Tuple[Path, Any]]:
        """파일명 순"""
        return sorted(files, key=lambda x: x[0].name)
    
    @staticmethod
    def sort_by_modified(files: List[Tuple[Path, Any]]) -> List[Tuple[Path, Any]]:
        """수정 시간 순"""
        return sorted(files, key=lambda x: x[0].stat().st_mtime)
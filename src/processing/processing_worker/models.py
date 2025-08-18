"""Data models for processing worker"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional


class WorkerState(Enum):
    """Worker state enumeration"""
    IDLE = "idle"
    PROCESSING = "processing"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class WorkerConfig:
    """Worker configuration"""
    worker_id: int
    max_retries: int = 3
    timeout: float = 300.0  # 5 minutes default
    log_level: str = "INFO"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'worker_id': self.worker_id,
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'log_level': self.log_level
        }


@dataclass
class WorkerStatus:
    """Worker status information"""
    worker_id: int
    state: WorkerState
    running: bool
    processing: bool
    current_task_id: Optional[str] = None
    processed_count: int = 0
    error_count: int = 0
    total_processing_time: float = 0.0
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time"""
        if self.processed_count == 0:
            return 0.0
        return self.total_processing_time / self.processed_count
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'worker_id': self.worker_id,
            'state': self.state.value,
            'running': self.running,
            'processing': self.processing,
            'current_task_id': self.current_task_id,
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'avg_processing_time': self.average_processing_time
        }


@dataclass
class PoolStatus:
    """Worker pool status"""
    num_workers: int
    active_workers: int
    processing_workers: int
    total_processed: int
    total_errors: int
    worker_statuses: list[WorkerStatus]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'num_workers': self.num_workers,
            'active_workers': self.active_workers,
            'processing_workers': self.processing_workers,
            'total_processed': self.total_processed,
            'total_errors': self.total_errors,
            'workers': [w.to_dict() for w in self.worker_statuses]
        }


@dataclass
class TaskContext:
    """Context for task processing"""
    task_id: str
    task_type: str
    data: Dict[str, Any]
    retry_count: int = 0
    priority: int = 0
    timeout: Optional[float] = None
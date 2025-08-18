"""Data models for dynamic batch processor"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class SystemResources:
    """System resource information"""
    cpu_count: int
    cpu_percent: float
    memory_total_gb: float
    memory_available_gb: float
    memory_percent: float
    
    def has_sufficient_resources(self, min_memory_gb: float = 1.0) -> bool:
        """Check if system has sufficient resources
        
        Args:
            min_memory_gb: Minimum required memory in GB
            
        Returns:
            True if resources are sufficient
        """
        return self.memory_available_gb >= min_memory_gb
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'cpu_count': self.cpu_count,
            'cpu_percent': self.cpu_percent,
            'memory_total_gb': self.memory_total_gb,
            'memory_available_gb': self.memory_available_gb,
            'memory_percent': self.memory_percent
        }


@dataclass
class WorkerPoolConfig:
    """Worker pool configuration"""
    min_workers: int = 1
    max_workers: Optional[int] = None  # None means CPU count
    memory_per_worker_mb: int = 500  # Memory per worker in MB
    cpu_threshold: float = 80.0  # CPU usage threshold
    memory_threshold: float = 80.0  # Memory usage threshold
    scale_up_threshold: float = 30.0  # Scale up threshold
    scale_down_threshold: float = 70.0  # Scale down threshold
    monitoring_interval: float = 5.0  # Monitoring interval in seconds
    
    def validate(self) -> bool:
        """Validate configuration
        
        Returns:
            True if configuration is valid
        """
        if self.min_workers < 1:
            return False
        if self.max_workers and self.max_workers < self.min_workers:
            return False
        if self.memory_per_worker_mb < 100:
            return False
        if not (0 <= self.cpu_threshold <= 100):
            return False
        if not (0 <= self.memory_threshold <= 100):
            return False
        if self.monitoring_interval < 1:
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'min_workers': self.min_workers,
            'max_workers': self.max_workers,
            'memory_per_worker_mb': self.memory_per_worker_mb,
            'cpu_threshold': self.cpu_threshold,
            'memory_threshold': self.memory_threshold,
            'scale_up_threshold': self.scale_up_threshold,
            'scale_down_threshold': self.scale_down_threshold,
            'monitoring_interval': self.monitoring_interval
        }


@dataclass
class PerformanceStats:
    """Performance statistics"""
    tasks_processed: int = 0
    average_time: float = 0.0
    worker_adjustments: int = 0
    peak_workers: int = 0
    total_processing_time: float = 0.0
    failed_tasks: int = 0
    
    def update_average_time(self, new_time: float):
        """Update average processing time
        
        Args:
            new_time: New processing time to include
        """
        if self.tasks_processed == 0:
            self.average_time = new_time
        else:
            total_time = self.average_time * self.tasks_processed + new_time
            self.average_time = total_time / (self.tasks_processed + 1)
        self.total_processing_time += new_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'tasks_processed': self.tasks_processed,
            'average_time': self.average_time,
            'worker_adjustments': self.worker_adjustments,
            'peak_workers': self.peak_workers,
            'total_processing_time': self.total_processing_time,
            'failed_tasks': self.failed_tasks,
            'success_rate': (self.tasks_processed - self.failed_tasks) / max(self.tasks_processed, 1)
        }


@dataclass
class BatchInfo:
    """Batch processing information"""
    batch_id: str
    total_files: int
    completed_files: int = 0
    failed_files: int = 0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage"""
        if self.total_files == 0:
            return 100.0
        return (self.completed_files / self.total_files) * 100
    
    @property
    def is_complete(self) -> bool:
        """Check if batch is complete"""
        return (self.completed_files + self.failed_files) >= self.total_files
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'batch_id': self.batch_id,
            'total_files': self.total_files,
            'completed_files': self.completed_files,
            'failed_files': self.failed_files,
            'progress_percent': self.progress_percent,
            'is_complete': self.is_complete,
            'start_time': self.start_time,
            'end_time': self.end_time
        }
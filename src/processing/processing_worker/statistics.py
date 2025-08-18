"""Statistics tracking for processing workers"""

import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class WorkerStatistics:
    """Track worker performance statistics"""
    
    processed_count: int = 0
    error_count: int = 0
    total_processing_time: float = 0.0
    start_time: Optional[float] = None
    last_task_time: Optional[float] = None
    
    # Task type statistics
    task_type_counts: Dict[str, int] = field(default_factory=dict)
    task_type_times: Dict[str, float] = field(default_factory=dict)
    
    # Error tracking
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def start_tracking(self):
        """Start statistics tracking"""
        self.start_time = time.time()
    
    def record_task_start(self):
        """Record task start time"""
        self.last_task_time = time.time()
    
    def record_task_complete(self, task_type: str, processing_time: float):
        """Record successful task completion
        
        Args:
            task_type: Type of task completed
            processing_time: Time taken to process
        """
        self.processed_count += 1
        self.total_processing_time += processing_time
        
        # Update task type statistics
        if task_type not in self.task_type_counts:
            self.task_type_counts[task_type] = 0
            self.task_type_times[task_type] = 0.0
        
        self.task_type_counts[task_type] += 1
        self.task_type_times[task_type] += processing_time
    
    def record_task_error(self, task_type: str, error: str):
        """Record task error
        
        Args:
            task_type: Type of task that failed
            error: Error message
        """
        self.error_count += 1
        
        # Categorize error
        error_type = self._categorize_error(error)
        if error_type not in self.error_types:
            self.error_types[error_type] = 0
        self.error_types[error_type] += 1
    
    def _categorize_error(self, error: str) -> str:
        """Categorize error type
        
        Args:
            error: Error message
            
        Returns:
            Error category
        """
        error_lower = error.lower()
        
        if 'file not found' in error_lower:
            return 'file_not_found'
        elif 'permission' in error_lower:
            return 'permission_denied'
        elif 'memory' in error_lower:
            return 'memory_error'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'format' in error_lower or 'pdf' in error_lower:
            return 'format_error'
        else:
            return 'other'
    
    @property
    def average_processing_time(self) -> float:
        """Calculate average processing time per task"""
        if self.processed_count == 0:
            return 0.0
        return self.total_processing_time / self.processed_count
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.processed_count + self.error_count
        if total == 0:
            return 0.0
        return self.processed_count / total
    
    @property
    def uptime(self) -> float:
        """Calculate uptime in seconds"""
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_task_type_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics by task type
        
        Returns:
            Dictionary of task type statistics
        """
        stats = {}
        for task_type in self.task_type_counts:
            count = self.task_type_counts[task_type]
            total_time = self.task_type_times.get(task_type, 0.0)
            
            stats[task_type] = {
                'count': count,
                'total_time': total_time,
                'avg_time': total_time / count if count > 0 else 0.0
            }
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary
        
        Returns:
            Dictionary representation
        """
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'success_rate': self.success_rate,
            'average_processing_time': self.average_processing_time,
            'total_processing_time': self.total_processing_time,
            'uptime': self.uptime,
            'task_type_stats': self.get_task_type_stats(),
            'error_types': dict(self.error_types)
        }
    
    def reset(self):
        """Reset statistics"""
        self.processed_count = 0
        self.error_count = 0
        self.total_processing_time = 0.0
        self.last_task_time = None
        self.task_type_counts.clear()
        self.task_type_times.clear()
        self.error_types.clear()
        # Don't reset start_time to maintain uptime


class PoolStatistics:
    """Track worker pool statistics"""
    
    def __init__(self, num_workers: int):
        """Initialize pool statistics
        
        Args:
            num_workers: Number of workers in pool
        """
        self.num_workers = num_workers
        self.worker_stats: Dict[int, WorkerStatistics] = {}
        
        # Initialize worker statistics
        for i in range(num_workers):
            self.worker_stats[i] = WorkerStatistics()
    
    def get_worker_stats(self, worker_id: int) -> WorkerStatistics:
        """Get statistics for specific worker
        
        Args:
            worker_id: Worker ID
            
        Returns:
            Worker statistics
        """
        if worker_id not in self.worker_stats:
            self.worker_stats[worker_id] = WorkerStatistics()
        return self.worker_stats[worker_id]
    
    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Get aggregate statistics across all workers
        
        Returns:
            Aggregate statistics dictionary
        """
        total_processed = sum(s.processed_count for s in self.worker_stats.values())
        total_errors = sum(s.error_count for s in self.worker_stats.values())
        total_time = sum(s.total_processing_time for s in self.worker_stats.values())
        
        # Aggregate task type stats
        task_type_totals = {}
        for stats in self.worker_stats.values():
            for task_type, count in stats.task_type_counts.items():
                if task_type not in task_type_totals:
                    task_type_totals[task_type] = {'count': 0, 'time': 0.0}
                task_type_totals[task_type]['count'] += count
                task_type_totals[task_type]['time'] += stats.task_type_times.get(task_type, 0.0)
        
        return {
            'total_processed': total_processed,
            'total_errors': total_errors,
            'overall_success_rate': total_processed / (total_processed + total_errors) if (total_processed + total_errors) > 0 else 0.0,
            'total_processing_time': total_time,
            'average_processing_time': total_time / total_processed if total_processed > 0 else 0.0,
            'task_type_totals': task_type_totals,
            'worker_count': self.num_workers
        }
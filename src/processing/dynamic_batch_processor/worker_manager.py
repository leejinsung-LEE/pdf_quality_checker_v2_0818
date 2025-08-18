"""Dynamic worker pool management"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any

from .models import WorkerPoolConfig, PerformanceStats


class DynamicWorkerManager:
    """Manage a dynamically sized worker pool"""
    
    def __init__(self,
                 config: Optional[WorkerPoolConfig] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize worker manager
        
        Args:
            config: Worker pool configuration
            logger: Logger instance
        """
        self.config = config or WorkerPoolConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Current worker count
        self.current_workers = self.config.min_workers
        
        # Worker pool
        self.executor: Optional[ThreadPoolExecutor] = None
        self.executor_lock = threading.Lock()
        
        # Task tracking
        self.active_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.task_lock = threading.Lock()
        
        # Performance statistics
        self.stats = PerformanceStats(peak_workers=self.current_workers)
    
    def start(self):
        """Start the worker pool"""
        with self.executor_lock:
            if self.executor is not None:
                self.logger.warning("Worker pool already started")
                return
            
            self.executor = ThreadPoolExecutor(max_workers=self.current_workers)
            self.logger.info(f"Worker pool started with {self.current_workers} workers")
    
    def stop(self, wait: bool = True, timeout: Optional[float] = None):
        """Stop the worker pool
        
        Args:
            wait: Whether to wait for pending tasks to complete
            timeout: Maximum time to wait
        """
        with self.executor_lock:
            if self.executor is None:
                return
            
            self.logger.info("Stopping worker pool...")
            self.executor.shutdown(wait=wait, timeout=timeout)
            self.executor = None
            self.logger.info("Worker pool stopped")
    
    def adjust_workers(self, new_worker_count: int):
        """Adjust the number of workers
        
        Args:
            new_worker_count: New number of workers
        """
        # Validate new count
        new_worker_count = max(
            self.config.min_workers,
            min(new_worker_count, self.config.max_workers or new_worker_count)
        )
        
        if new_worker_count == self.current_workers:
            return
        
        old_count = self.current_workers
        self.current_workers = new_worker_count
        
        with self.executor_lock:
            if self.executor is None:
                return
            
            # Create new executor with new worker count
            old_executor = self.executor
            self.executor = ThreadPoolExecutor(max_workers=new_worker_count)
            
            # Shutdown old executor in background (allows pending tasks to complete)
            def shutdown_old():
                try:
                    old_executor.shutdown(wait=True)
                except Exception as e:
                    self.logger.error(f"Error shutting down old executor: {e}")
            
            threading.Thread(target=shutdown_old, daemon=True).start()
        
        # Update statistics
        self.stats.worker_adjustments += 1
        self.stats.peak_workers = max(self.stats.peak_workers, new_worker_count)
        
        self.logger.info(f"Worker count adjusted: {old_count} -> {new_worker_count}")
    
    def submit_task(self, func, *args, **kwargs):
        """Submit a task to the worker pool
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Future object
        """
        with self.executor_lock:
            if self.executor is None:
                raise RuntimeError("Worker pool not started")
            
            with self.task_lock:
                self.active_tasks += 1
            
            future = self.executor.submit(self._wrapped_task, func, *args, **kwargs)
            return future
    
    def _wrapped_task(self, func, *args, **kwargs):
        """Wrapper for task execution with tracking
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Task result
        """
        try:
            result = func(*args, **kwargs)
            
            with self.task_lock:
                self.completed_tasks += 1
                self.active_tasks -= 1
            
            return result
            
        except Exception as e:
            with self.task_lock:
                self.failed_tasks += 1
                self.active_tasks -= 1
            
            self.logger.error(f"Task execution failed: {e}")
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get worker manager status
        
        Returns:
            Status dictionary
        """
        with self.task_lock:
            active = self.active_tasks
            completed = self.completed_tasks
            failed = self.failed_tasks
        
        return {
            'current_workers': self.current_workers,
            'active_tasks': active,
            'completed_tasks': completed,
            'failed_tasks': failed,
            'total_tasks': completed + failed,
            'pool_active': self.executor is not None
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics
        
        Returns:
            Statistics dictionary
        """
        status = self.get_status()
        stats_dict = self.stats.to_dict()
        stats_dict.update(status)
        return stats_dict
    
    def reset_statistics(self):
        """Reset performance statistics"""
        with self.task_lock:
            self.completed_tasks = 0
            self.failed_tasks = 0
        
        self.stats = PerformanceStats(peak_workers=self.current_workers)
        self.logger.info("Statistics reset")
    
    def is_idle(self) -> bool:
        """Check if worker pool is idle
        
        Returns:
            True if no active tasks
        """
        with self.task_lock:
            return self.active_tasks == 0
    
    def wait_for_tasks(self, timeout: Optional[float] = None) -> bool:
        """Wait for all active tasks to complete
        
        Args:
            timeout: Maximum time to wait
            
        Returns:
            True if all tasks completed within timeout
        """
        import time
        start_time = time.time()
        
        while not self.is_idle():
            if timeout and (time.time() - start_time) > timeout:
                return False
            time.sleep(0.1)
        
        return True
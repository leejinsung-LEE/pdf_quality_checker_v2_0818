"""Worker pool management"""

import logging
from typing import Optional, Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from .models import PoolStatus, WorkerConfig
from .worker import ProcessingWorker
from .statistics import PoolStatistics
from ..queue_manager import QueueManager


class WorkerPool:
    """Manages a pool of processing workers"""
    
    def __init__(self,
                 queue_manager: QueueManager,
                 num_workers: int = 2,
                 worker_config: Optional[WorkerConfig] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize worker pool
        
        Args:
            queue_manager: Queue manager instance
            num_workers: Number of workers in pool
            worker_config: Base configuration for workers
            logger: Logger instance
        """
        self.queue_manager = queue_manager
        self.num_workers = num_workers
        self.logger = logger or logging.getLogger(__name__)
        
        # Worker list
        self.workers: List[ProcessingWorker] = []
        
        # Statistics
        self.statistics = PoolStatistics(num_workers)
        
        # Thread pool for management operations
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        
        # Create workers
        for i in range(num_workers):
            config = worker_config or WorkerConfig(worker_id=i)
            config.worker_id = i  # Ensure unique ID
            
            worker = ProcessingWorker(
                queue_manager=queue_manager,
                worker_id=i,
                config=config,
                logger=self.logger
            )
            self.workers.append(worker)
    
    def start(self):
        """Start all workers in the pool"""
        self.logger.info(f"Starting worker pool with {self.num_workers} workers")
        
        for worker in self.workers:
            try:
                worker.start()
                # Link worker statistics
                self.statistics.worker_stats[worker.worker_id] = worker.statistics
            except Exception as e:
                self.logger.error(f"Failed to start worker {worker.worker_id}: {e}")
        
        active_count = sum(1 for w in self.workers if w.running)
        self.logger.info(f"Worker pool started: {active_count}/{self.num_workers} workers active")
    
    def stop(self, timeout: float = 10.0):
        """Stop all workers in the pool
        
        Args:
            timeout: Maximum time to wait for all workers to stop
        """
        self.logger.info("Stopping worker pool...")
        
        # Calculate per-worker timeout
        per_worker_timeout = timeout / max(self.num_workers, 1)
        
        # Stop workers in parallel
        futures = []
        for worker in self.workers:
            future = self.executor.submit(worker.stop, per_worker_timeout)
            futures.append(future)
        
        # Wait for all stops to complete
        for future in futures:
            try:
                future.result(timeout=per_worker_timeout)
            except Exception as e:
                self.logger.error(f"Error stopping worker: {e}")
        
        self.logger.info("Worker pool stopped")
    
    def restart_worker(self, worker_id: int):
        """Restart a specific worker
        
        Args:
            worker_id: ID of worker to restart
        """
        if worker_id >= len(self.workers):
            self.logger.error(f"Invalid worker ID: {worker_id}")
            return
        
        worker = self.workers[worker_id]
        self.logger.info(f"Restarting worker {worker_id}")
        
        # Stop the worker
        worker.stop(timeout=5.0)
        
        # Start it again
        worker.start()
    
    def scale(self, new_size: int):
        """Scale the worker pool to a new size
        
        Args:
            new_size: New number of workers
        """
        current_size = len(self.workers)
        
        if new_size == current_size:
            return
        
        if new_size > current_size:
            # Add new workers
            self.logger.info(f"Scaling up from {current_size} to {new_size} workers")
            
            for i in range(current_size, new_size):
                config = WorkerConfig(worker_id=i)
                worker = ProcessingWorker(
                    queue_manager=self.queue_manager,
                    worker_id=i,
                    config=config,
                    logger=self.logger
                )
                self.workers.append(worker)
                worker.start()
                self.statistics.worker_stats[i] = worker.statistics
        else:
            # Remove workers
            self.logger.info(f"Scaling down from {current_size} to {new_size} workers")
            
            # Stop and remove excess workers
            workers_to_remove = self.workers[new_size:]
            for worker in workers_to_remove:
                worker.stop(timeout=5.0)
                del self.statistics.worker_stats[worker.worker_id]
            
            self.workers = self.workers[:new_size]
        
        self.num_workers = new_size
    
    def get_status(self) -> PoolStatus:
        """Get pool status
        
        Returns:
            Pool status object
        """
        worker_statuses = [w.get_status() for w in self.workers]
        
        return PoolStatus(
            num_workers=self.num_workers,
            active_workers=sum(1 for w in worker_statuses if w.running),
            processing_workers=sum(1 for w in worker_statuses if w.processing),
            total_processed=sum(w.processed_count for w in worker_statuses),
            total_errors=sum(w.error_count for w in worker_statuses),
            worker_statuses=worker_statuses
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed pool statistics
        
        Returns:
            Statistics dictionary
        """
        aggregate = self.statistics.get_aggregate_stats()
        worker_stats = {
            f"worker_{i}": self.workers[i].get_statistics()
            for i in range(len(self.workers))
        }
        
        return {
            'aggregate': aggregate,
            'workers': worker_stats
        }
    
    def reset_statistics(self):
        """Reset statistics for all workers"""
        for worker in self.workers:
            worker.reset_statistics()
        self.logger.info("Pool statistics reset")
    
    def get_worker(self, worker_id: int) -> Optional[ProcessingWorker]:
        """Get specific worker by ID
        
        Args:
            worker_id: Worker ID
            
        Returns:
            Worker instance or None
        """
        if 0 <= worker_id < len(self.workers):
            return self.workers[worker_id]
        return None
    
    def is_active(self) -> bool:
        """Check if any workers are active
        
        Returns:
            True if at least one worker is running
        """
        return any(w.running for w in self.workers)
    
    def shutdown(self):
        """Shutdown the worker pool and cleanup resources"""
        self.stop(timeout=10.0)
        self.executor.shutdown(wait=True)
        self.logger.info("Worker pool shutdown complete")
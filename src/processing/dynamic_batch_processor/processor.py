"""Main dynamic batch processor"""

import queue
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import as_completed
import uuid

from .models import WorkerPoolConfig, SystemResources, BatchInfo
from .resource_monitor import ResourceMonitor
from .worker_manager import DynamicWorkerManager
from .batch_optimizer import SmartBatchOptimizer


class DynamicBatchProcessor:
    """Dynamic batch processor with adaptive worker management"""
    
    def __init__(self,
                 config: Optional[WorkerPoolConfig] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize dynamic batch processor
        
        Args:
            config: Worker pool configuration
            logger: Logger instance
        """
        self.config = config or WorkerPoolConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid worker pool configuration")
        
        # Initialize components
        self.resource_monitor = ResourceMonitor(config=self.config, logger=self.logger)
        self.worker_manager = DynamicWorkerManager(config=self.config, logger=self.logger)
        self.batch_optimizer = SmartBatchOptimizer(logger=self.logger)
        
        # Task queue
        self.task_queue: queue.Queue = queue.Queue()
        
        # Current batch info
        self.current_batch: Optional[BatchInfo] = None
        
        # Started flag
        self.started = False
    
    def start(self):
        """Start the batch processor"""
        if self.started:
            self.logger.warning("Batch processor already started")
            return
        
        # Start worker pool
        self.worker_manager.start()
        
        # Start resource monitoring with callback
        self.resource_monitor.start_monitoring(
            callback=self._on_resource_update
        )
        
        self.started = True
        self.logger.info("Dynamic batch processor started")
    
    def stop(self):
        """Stop the batch processor"""
        if not self.started:
            return
        
        # Stop resource monitoring
        self.resource_monitor.stop_monitoring()
        
        # Stop worker pool
        self.worker_manager.stop(wait=True)
        
        self.started = False
        self.logger.info("Dynamic batch processor stopped")
    
    def _on_resource_update(self, resources: SystemResources):
        """Handle resource update from monitor
        
        Args:
            resources: Updated system resources
        """
        # Calculate optimal worker count
        status = self.worker_manager.get_status()
        
        optimal_workers = self.resource_monitor.calculate_optimal_workers(
            resources=resources,
            current_workers=self.worker_manager.current_workers,
            queue_size=self.task_queue.qsize(),
            active_tasks=status['active_tasks']
        )
        
        # Adjust workers if needed
        if optimal_workers != self.worker_manager.current_workers:
            self.worker_manager.adjust_workers(optimal_workers)
    
    def process_batch(self,
                     files: List[Path],
                     process_func: Callable[[Path], Any],
                     progress_callback: Optional[Callable[[int, int], None]] = None,
                     optimize: bool = True) -> List[Any]:
        """Process a batch of files
        
        Args:
            files: List of files to process
            process_func: Function to process each file
            progress_callback: Optional progress callback
            optimize: Whether to optimize batch configuration
            
        Returns:
            List of processing results
        """
        if not self.started:
            self.start()
        
        # Create batch info
        batch_id = str(uuid.uuid4())[:8]
        self.current_batch = BatchInfo(
            batch_id=batch_id,
            total_files=len(files),
            start_time=time.time()
        )
        
        self.logger.info(f"Starting batch {batch_id} with {len(files)} files")
        
        # Optimize batch if requested
        if optimize:
            batches = self.batch_optimizer.optimize_by_paths(files)
            self.logger.info(f"Optimized into {len(batches)} sub-batches")
        else:
            # Process files individually
            batches = [[f] for f in files]
        
        # Process batches
        all_results = []
        completed_count = 0
        
        for batch_files in batches:
            batch_results = self._process_sub_batch(batch_files, process_func)
            all_results.extend(batch_results)
            
            # Update progress
            completed_count += len(batch_files)
            self.current_batch.completed_files = completed_count
            
            if progress_callback:
                progress_callback(completed_count, len(files))
        
        # Update batch info
        self.current_batch.end_time = time.time()
        
        # Update optimizer with results
        processing_results = []
        for i, result in enumerate(all_results):
            if isinstance(result, dict) and 'processing_time' in result:
                processing_results.append({
                    'file_size': files[i].stat().st_size if files[i].exists() else 0,
                    'processing_time': result['processing_time']
                })
        
        if processing_results:
            self.batch_optimizer.update_optimization_params(processing_results)
        
        # Update statistics
        stats = self.worker_manager.stats
        stats.tasks_processed += len(files)
        
        self.logger.info(
            f"Batch {batch_id} completed in "
            f"{self.current_batch.end_time - self.current_batch.start_time:.2f}s"
        )
        
        return all_results
    
    def _process_sub_batch(self,
                          files: List[Path],
                          process_func: Callable[[Path], Any]) -> List[Any]:
        """Process a sub-batch of files
        
        Args:
            files: Files in the sub-batch
            process_func: Processing function
            
        Returns:
            List of results
        """
        futures = []
        results = []
        
        # Submit tasks to worker pool
        for file_path in files:
            future = self.worker_manager.submit_task(
                self._process_file_wrapper,
                file_path,
                process_func
            )
            futures.append((file_path, future))
        
        # Collect results
        for file_path, future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                self.logger.error(f"Processing failed for {file_path}: {e}")
                results.append({
                    'error': str(e),
                    'file': str(file_path)
                })
                
                if self.current_batch:
                    self.current_batch.failed_files += 1
        
        return results
    
    def _process_file_wrapper(self,
                            file_path: Path,
                            process_func: Callable[[Path], Any]) -> Any:
        """Wrapper for file processing with timing
        
        Args:
            file_path: File to process
            process_func: Processing function
            
        Returns:
            Processing result
        """
        start_time = time.time()
        
        try:
            result = process_func(file_path)
            processing_time = time.time() - start_time
            
            # Add timing info if result is a dict
            if isinstance(result, dict):
                result['processing_time'] = processing_time
            
            # Update statistics
            self.worker_manager.stats.update_average_time(processing_time)
            
            return result
            
        except Exception as e:
            self.logger.error(f"File processing failed for {file_path}: {e}")
            self.worker_manager.stats.failed_tasks += 1
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get processor status
        
        Returns:
            Status dictionary
        """
        resources = self.resource_monitor.get_current_resources()
        worker_status = self.worker_manager.get_status()
        
        status = {
            'started': self.started,
            'current_workers': worker_status['current_workers'],
            'active_tasks': worker_status['active_tasks'],
            'completed_tasks': worker_status['completed_tasks'],
            'failed_tasks': worker_status['failed_tasks'],
            'queue_size': self.task_queue.qsize(),
            'cpu_percent': resources.cpu_percent,
            'memory_percent': resources.memory_percent,
            'performance_stats': self.worker_manager.stats.to_dict()
        }
        
        if self.current_batch:
            status['current_batch'] = self.current_batch.to_dict()
        
        return status
    
    def get_system_resources(self) -> SystemResources:
        """Get current system resources
        
        Returns:
            System resources
        """
        return self.resource_monitor.get_current_resources()
    
    def calculate_optimal_workers(self, resources: SystemResources) -> int:
        """Calculate optimal number of workers
        
        Args:
            resources: System resources
            
        Returns:
            Optimal worker count
        """
        status = self.worker_manager.get_status()
        
        return self.resource_monitor.calculate_optimal_workers(
            resources=resources,
            current_workers=self.worker_manager.current_workers,
            queue_size=self.task_queue.qsize(),
            active_tasks=status['active_tasks']
        )
    
    def adjust_worker_pool(self, new_worker_count: int):
        """Manually adjust worker pool size
        
        Args:
            new_worker_count: New number of workers
        """
        self.worker_manager.adjust_workers(new_worker_count)
"""Processing worker implementation"""

import threading
import logging
import time
from typing import Optional, Dict, Any
from pathlib import Path

from .models import WorkerConfig, WorkerStatus, WorkerState
from .task_handlers import TaskHandlers
from .statistics import WorkerStatistics
from ..queue_manager import QueueManager, TaskType, Task
from ..processor import PDFProcessor
from ...core.analyzers import PDFAnalyzer
from ...core.quality_checker import PDFQualityChecker


class ProcessingWorker:
    """Background processing worker for PDF tasks"""
    
    def __init__(self,
                 queue_manager: QueueManager,
                 worker_id: int = 0,
                 config: Optional[WorkerConfig] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize processing worker
        
        Args:
            queue_manager: Queue manager instance
            worker_id: Worker identifier
            config: Worker configuration
            logger: Logger instance
        """
        self.queue_manager = queue_manager
        self.worker_id = worker_id
        self.config = config or WorkerConfig(worker_id=worker_id)
        self.logger = logger or logging.getLogger(f"{__name__}.Worker{worker_id}")
        
        # Initialize components
        self.processor = PDFProcessor(logger=self.logger)
        self.analyzer = PDFAnalyzer()
        self.checker = PDFQualityChecker()
        
        # Task handlers
        self.task_handlers = TaskHandlers(
            processor=self.processor,
            analyzer=self.analyzer,
            checker=self.checker,
            logger=self.logger
        )
        
        # Worker state
        self.state = WorkerState.STOPPED
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        self.processing = False
        self.current_task_id: Optional[str] = None
        
        # Statistics
        self.statistics = WorkerStatistics()
    
    def start(self):
        """Start the worker"""
        if self.running:
            self.logger.warning(f"Worker {self.worker_id} already running")
            return
        
        self.running = True
        self.state = WorkerState.IDLE
        self.statistics.start_tracking()
        
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            name=f"PDFWorker-{self.worker_id}",
            daemon=True
        )
        self.worker_thread.start()
        self.logger.info(f"Worker {self.worker_id} started")
    
    def stop(self, timeout: float = 5.0):
        """Stop the worker
        
        Args:
            timeout: Maximum time to wait for worker to stop
        """
        if not self.running:
            return
        
        self.logger.info(f"Worker {self.worker_id} stopping...")
        self.running = False
        self.state = WorkerState.STOPPED
        
        if self.worker_thread:
            self.worker_thread.join(timeout)
            if self.worker_thread.is_alive():
                self.logger.warning(f"Worker {self.worker_id} force terminated")
        
        self.logger.info(f"Worker {self.worker_id} stopped")
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get next task from queue (with timeout)
                task = self.queue_manager.get_next_task(timeout=1.0)
                
                if task:
                    self.state = WorkerState.PROCESSING
                    self.processing = True
                    self.current_task_id = task.task_id
                    
                    self._process_task(task)
                    
                    self.processing = False
                    self.current_task_id = None
                    self.state = WorkerState.IDLE
                    
            except Exception as e:
                self.logger.error(f"Worker {self.worker_id} loop error: {e}")
                self.state = WorkerState.ERROR
                time.sleep(1)  # Wait before retrying
                self.state = WorkerState.IDLE
    
    def _process_task(self, task: Task):
        """Process a single task
        
        Args:
            task: Task to process
        """
        start_time = time.time()
        self.statistics.record_task_start()
        
        try:
            self.logger.info(f"Task started: {task.task_id} ({task.task_type.value})")
            
            # Route to appropriate handler
            result = self._route_task(task)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Mark task as complete
            self.queue_manager.complete_task(
                task.task_id,
                success=True,
                result=result,
                processing_time=processing_time
            )
            
            # Update statistics
            self.statistics.record_task_complete(
                task.task_type.value,
                processing_time
            )
            
            self.logger.info(
                f"Task completed: {task.task_id} ({processing_time:.2f}s)"
            )
            
        except Exception as e:
            # Handle task failure
            processing_time = time.time() - start_time
            
            self.queue_manager.complete_task(
                task.task_id,
                success=False,
                result=None,
                error=str(e),
                processing_time=processing_time
            )
            
            self.statistics.record_task_error(
                task.task_type.value,
                str(e)
            )
            
            self.logger.error(f"Task failed: {task.task_id} - {e}")
    
    def _route_task(self, task: Task) -> Dict[str, Any]:
        """Route task to appropriate handler
        
        Args:
            task: Task to route
            
        Returns:
            Task result
        """
        if task.task_type == TaskType.PROCESS_FILE:
            return self.task_handlers.handle_process_file(task)
        elif task.task_type == TaskType.BATCH_PROCESS:
            return self.task_handlers.handle_batch_process(task)
        elif task.task_type == TaskType.ANALYZE_ONLY:
            return self.task_handlers.handle_analyze_only(task)
        elif task.task_type == TaskType.CHECK_QUALITY:
            return self.task_handlers.handle_check_quality(task)
        elif task.task_type == TaskType.GENERATE_REPORT:
            return self.task_handlers.handle_generate_report(task)
        elif task.task_type == TaskType.AUTO_FIX:
            return self.task_handlers.handle_auto_fix(task)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    def get_status(self) -> WorkerStatus:
        """Get current worker status
        
        Returns:
            Worker status object
        """
        return WorkerStatus(
            worker_id=self.worker_id,
            state=self.state,
            running=self.running,
            processing=self.processing,
            current_task_id=self.current_task_id,
            processed_count=self.statistics.processed_count,
            error_count=self.statistics.error_count,
            total_processing_time=self.statistics.total_processing_time
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed worker statistics
        
        Returns:
            Statistics dictionary
        """
        return self.statistics.to_dict()
    
    def reset_statistics(self):
        """Reset worker statistics"""
        self.statistics.reset()
        self.logger.info(f"Worker {self.worker_id} statistics reset")
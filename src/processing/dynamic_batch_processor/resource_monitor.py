"""System resource monitoring"""

import os
import psutil
import logging
import threading
import time
from typing import Optional, Callable, Dict, Any

from .models import SystemResources, WorkerPoolConfig


class ResourceMonitor:
    """Monitor system resources and determine optimal worker count"""
    
    def __init__(self,
                 config: Optional[WorkerPoolConfig] = None,
                 logger: Optional[logging.Logger] = None):
        """Initialize resource monitor
        
        Args:
            config: Worker pool configuration
            logger: Logger instance
        """
        self.config = config or WorkerPoolConfig()
        self.logger = logger or logging.getLogger(__name__)
        
        # System information
        self.cpu_count = os.cpu_count() or 1
        if self.config.max_workers is None:
            self.config.max_workers = self.cpu_count
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.resource_callback: Optional[Callable[[SystemResources], None]] = None
        
        # Current resources cache
        self._current_resources: Optional[SystemResources] = None
        self._resources_lock = threading.Lock()
    
    def start_monitoring(self, callback: Optional[Callable[[SystemResources], None]] = None):
        """Start resource monitoring
        
        Args:
            callback: Callback function to call with resource updates
        """
        if self.monitoring_active:
            self.logger.warning("Resource monitoring already active")
            return
        
        self.resource_callback = callback
        self.monitoring_active = True
        
        self.monitoring_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="ResourceMonitor"
        )
        self.monitoring_thread.start()
        
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self, timeout: float = 5.0):
        """Stop resource monitoring
        
        Args:
            timeout: Maximum time to wait for monitoring to stop
        """
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout)
            if self.monitoring_thread.is_alive():
                self.logger.warning("Resource monitoring thread did not stop cleanly")
        
        self.logger.info("Resource monitoring stopped")
    
    def get_current_resources(self) -> SystemResources:
        """Get current system resources
        
        Returns:
            Current system resources
        """
        memory = psutil.virtual_memory()
        
        resources = SystemResources(
            cpu_count=self.cpu_count,
            cpu_percent=psutil.cpu_percent(interval=1),
            memory_total_gb=memory.total / (1024**3),
            memory_available_gb=memory.available / (1024**3),
            memory_percent=memory.percent
        )
        
        # Update cache
        with self._resources_lock:
            self._current_resources = resources
        
        return resources
    
    def get_cached_resources(self) -> Optional[SystemResources]:
        """Get cached resource information
        
        Returns:
            Cached resources or None if not available
        """
        with self._resources_lock:
            return self._current_resources
    
    def calculate_optimal_workers(self,
                                 resources: Optional[SystemResources] = None,
                                 current_workers: int = 1,
                                 queue_size: int = 0,
                                 active_tasks: int = 0) -> int:
        """Calculate optimal number of workers
        
        Args:
            resources: System resources (uses current if not provided)
            current_workers: Current number of workers
            queue_size: Current queue size
            active_tasks: Number of active tasks
            
        Returns:
            Optimal number of workers
        """
        if resources is None:
            resources = self.get_current_resources()
        
        # CPU-based calculation
        cpu_based = self.cpu_count
        if resources.cpu_percent > self.config.cpu_threshold:
            cpu_based = max(1, current_workers - 1)
        elif resources.cpu_percent < self.config.scale_up_threshold:
            cpu_based = min(self.config.max_workers, current_workers + 1)
        else:
            cpu_based = current_workers
        
        # Memory-based calculation
        available_memory_mb = resources.memory_available_gb * 1024
        memory_based = int(available_memory_mb / self.config.memory_per_worker_mb)
        memory_based = max(1, min(memory_based, self.config.max_workers))
        
        # Queue-based calculation
        if queue_size > current_workers * 2:
            # Many pending tasks, scale up
            queue_based = min(self.config.max_workers, current_workers + 1)
        elif queue_size == 0 and active_tasks == 0:
            # No work, scale down to minimum
            queue_based = self.config.min_workers
        else:
            queue_based = current_workers
        
        # Take the most conservative value
        optimal = min(cpu_based, memory_based, queue_based)
        
        # Apply bounds
        optimal = max(self.config.min_workers, min(optimal, self.config.max_workers))
        
        self.logger.debug(
            f"Worker calculation - CPU: {cpu_based}, Memory: {memory_based}, "
            f"Queue: {queue_based}, Final: {optimal}"
        )
        
        return optimal
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Get current resources
                resources = self.get_current_resources()
                
                # Call callback if provided
                if self.resource_callback:
                    self.resource_callback(resources)
                
                # Log resource status
                self.logger.debug(
                    f"Resources - CPU: {resources.cpu_percent:.1f}%, "
                    f"Memory: {resources.memory_percent:.1f}% "
                    f"({resources.memory_available_gb:.1f}GB available)"
                )
                
            except Exception as e:
                self.logger.error(f"Resource monitoring error: {e}")
            
            # Wait for next interval
            time.sleep(self.config.monitoring_interval)
    
    def get_resource_summary(self) -> Dict[str, Any]:
        """Get resource monitoring summary
        
        Returns:
            Dictionary with resource summary
        """
        resources = self.get_current_resources()
        
        return {
            'cpu': {
                'count': resources.cpu_count,
                'percent': resources.cpu_percent,
                'available': resources.cpu_percent < self.config.cpu_threshold
            },
            'memory': {
                'total_gb': resources.memory_total_gb,
                'available_gb': resources.memory_available_gb,
                'percent': resources.memory_percent,
                'available': resources.memory_percent < self.config.memory_threshold
            },
            'monitoring': {
                'active': self.monitoring_active,
                'interval': self.config.monitoring_interval
            }
        }
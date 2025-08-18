"""Memory monitoring utilities"""

import gc
import os
import psutil
from typing import Optional
import logging


class MemoryMonitor:
    """Monitor and manage memory usage during processing"""
    
    def __init__(self, 
                 max_memory_mb: int = 500,
                 logger: Optional[logging.Logger] = None):
        """Initialize memory monitor
        
        Args:
            max_memory_mb: Maximum memory usage in MB
            logger: Logger instance
        """
        self.max_memory_mb = max_memory_mb
        self.logger = logger or logging.getLogger(__name__)
        
        # Get process handle
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB
        
        Returns:
            Current memory usage in megabytes
        """
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_memory_delta(self) -> float:
        """Get memory usage change since initialization
        
        Returns:
            Memory delta in megabytes
        """
        return self.get_memory_usage() - self.initial_memory
    
    def is_memory_critical(self) -> bool:
        """Check if memory usage is critical
        
        Returns:
            True if memory usage exceeds 90% of max
        """
        return self.get_memory_delta() > self.max_memory_mb * 0.9
    
    def should_reduce_load(self) -> bool:
        """Check if processing load should be reduced
        
        Returns:
            True if memory usage exceeds 80% of max
        """
        return self.get_memory_delta() > self.max_memory_mb * 0.8
    
    def cleanup_memory(self):
        """Force garbage collection to free memory"""
        collected = gc.collect()
        self.logger.debug(f"Garbage collected {collected} objects")
        
    def get_memory_info(self) -> dict:
        """Get detailed memory information
        
        Returns:
            Dictionary with memory statistics
        """
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024,
            'delta_mb': self.get_memory_delta()
        }
    
    def adjust_chunk_size(self, current_size: int) -> int:
        """Adjust chunk size based on memory usage
        
        Args:
            current_size: Current chunk size
            
        Returns:
            Adjusted chunk size
        """
        if self.is_memory_critical():
            # Critical: reduce to minimum
            return max(1, current_size // 4)
        elif self.should_reduce_load():
            # High usage: reduce by half
            return max(1, current_size // 2)
        else:
            # Normal: maintain or slightly increase
            return min(current_size + 1, current_size * 2)
    
    def reset(self):
        """Reset initial memory baseline"""
        self.initial_memory = self.get_memory_usage()
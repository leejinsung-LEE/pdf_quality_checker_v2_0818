"""Batch optimization strategies"""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import logging


class SmartBatchOptimizer:
    """Optimize batch processing based on file characteristics"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize batch optimizer
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Optimization history for learning
        self.history: List[Dict[str, Any]] = []
        
        # Default batch sizes
        self.small_file_batch_size = 10
        self.medium_file_batch_size = 3
        self.large_file_batch_size = 1
        
        # File size thresholds (in MB)
        self.small_file_threshold = 1.0
        self.large_file_threshold = 10.0
    
    def optimize_batch_size(self, file_sizes: List[int]) -> List[List[int]]:
        """Optimize batch configuration based on file sizes
        
        Args:
            file_sizes: List of file sizes in bytes
            
        Returns:
            List of batches, each containing file indices
        """
        if not file_sizes:
            return []
        
        # Categorize files by size
        small_files = []
        medium_files = []
        large_files = []
        
        for i, size in enumerate(file_sizes):
            size_mb = size / (1024 * 1024)
            
            if size_mb < self.small_file_threshold:
                small_files.append(i)
            elif size_mb < self.large_file_threshold:
                medium_files.append(i)
            else:
                large_files.append(i)
        
        batches = []
        
        # Large files: process individually
        for idx in large_files:
            batches.append([idx])
        
        # Medium files: group in small batches
        for i in range(0, len(medium_files), self.medium_file_batch_size):
            batch = medium_files[i:i + self.medium_file_batch_size]
            batches.append(batch)
        
        # Small files: group in larger batches
        for i in range(0, len(small_files), self.small_file_batch_size):
            batch = small_files[i:i + self.small_file_batch_size]
            batches.append(batch)
        
        self.logger.info(
            f"Optimized {len(file_sizes)} files into {len(batches)} batches "
            f"(Large: {len(large_files)}, Medium: {len(medium_files)}, "
            f"Small: {len(small_files)})"
        )
        
        return batches
    
    def optimize_by_paths(self, file_paths: List[Path]) -> List[List[Path]]:
        """Optimize batch configuration based on file paths
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of batches, each containing file paths
        """
        # Get file sizes
        file_sizes = []
        valid_paths = []
        
        for path in file_paths:
            try:
                if path.exists():
                    file_sizes.append(path.stat().st_size)
                    valid_paths.append(path)
                else:
                    self.logger.warning(f"File not found: {path}")
            except Exception as e:
                self.logger.error(f"Error accessing file {path}: {e}")
        
        if not file_sizes:
            return []
        
        # Get optimized indices
        batch_indices = self.optimize_batch_size(file_sizes)
        
        # Convert indices to paths
        batches = []
        for indices in batch_indices:
            batch = [valid_paths[i] for i in indices]
            batches.append(batch)
        
        return batches
    
    def estimate_processing_time(self, 
                                file_sizes: List[int],
                                avg_speed_mbps: float = 10.0) -> Dict[str, float]:
        """Estimate processing time for files
        
        Args:
            file_sizes: List of file sizes in bytes
            avg_speed_mbps: Average processing speed in MB/second
            
        Returns:
            Dictionary with time estimates
        """
        if not file_sizes:
            return {'total_time': 0, 'avg_time': 0, 'batches': 0}
        
        total_size_mb = sum(file_sizes) / (1024 * 1024)
        batches = self.optimize_batch_size(file_sizes)
        
        # Estimate time for each batch (parallel processing within batch)
        batch_times = []
        for batch_indices in batches:
            batch_size_mb = sum(file_sizes[i] for i in batch_indices) / (1024 * 1024)
            batch_time = batch_size_mb / avg_speed_mbps
            batch_times.append(batch_time)
        
        # Assume batches are processed sequentially
        total_time = sum(batch_times)
        avg_time = total_time / len(batches) if batches else 0
        
        return {
            'total_time': total_time,
            'avg_time': avg_time,
            'total_size_mb': total_size_mb,
            'num_batches': len(batches),
            'estimated_speed_mbps': avg_speed_mbps
        }
    
    def update_optimization_params(self, processing_results: List[Dict[str, Any]]):
        """Update optimization parameters based on processing results
        
        Args:
            processing_results: List of processing results with timing info
        """
        if not processing_results:
            return
        
        # Analyze results to adjust batch sizes
        small_times = []
        medium_times = []
        large_times = []
        
        for result in processing_results:
            if 'file_size' not in result or 'processing_time' not in result:
                continue
            
            size_mb = result['file_size'] / (1024 * 1024)
            time = result['processing_time']
            
            if size_mb < self.small_file_threshold:
                small_times.append(time)
            elif size_mb < self.large_file_threshold:
                medium_times.append(time)
            else:
                large_times.append(time)
        
        # Adjust batch sizes based on average processing times
        target_batch_time = 5.0  # Target 5 seconds per batch
        
        if small_times:
            avg_small_time = sum(small_times) / len(small_times)
            if avg_small_time > 0:
                self.small_file_batch_size = max(1, int(target_batch_time / avg_small_time))
        
        if medium_times:
            avg_medium_time = sum(medium_times) / len(medium_times)
            if avg_medium_time > 0:
                self.medium_file_batch_size = max(1, int(target_batch_time / avg_medium_time))
        
        # Store in history for future learning
        self.history.extend(processing_results)
        
        # Keep history size manageable
        if len(self.history) > 1000:
            self.history = self.history[-500:]
        
        self.logger.info(
            f"Updated batch sizes - Small: {self.small_file_batch_size}, "
            f"Medium: {self.medium_file_batch_size}"
        )
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics
        
        Returns:
            Dictionary with optimization stats
        """
        return {
            'batch_sizes': {
                'small': self.small_file_batch_size,
                'medium': self.medium_file_batch_size,
                'large': self.large_file_batch_size
            },
            'thresholds': {
                'small_mb': self.small_file_threshold,
                'large_mb': self.large_file_threshold
            },
            'history_size': len(self.history)
        }
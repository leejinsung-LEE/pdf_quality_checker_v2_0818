"""Adaptive chunk processing"""

from typing import List, Dict, Any, Optional
from .models import PerformanceMetrics


class AdaptiveChunkProcessor:
    """Adaptive chunk size processor based on performance metrics"""
    
    def __init__(self, 
                 base_chunk_size: int = 10,
                 min_chunk_size: int = 1,
                 max_chunk_size: int = 50):
        """Initialize adaptive processor
        
        Args:
            base_chunk_size: Default chunk size
            min_chunk_size: Minimum allowed chunk size
            max_chunk_size: Maximum allowed chunk size
        """
        self.base_chunk_size = base_chunk_size
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.performance_history: List[PerformanceMetrics] = []
        self.current_chunk_size = base_chunk_size
        
    def get_optimal_chunk_size(self) -> int:
        """Calculate optimal chunk size based on performance history
        
        Returns:
            Optimal chunk size
        """
        if not self.performance_history:
            return self.base_chunk_size
        
        # Analyze recent performance (last 5 measurements)
        recent = self.performance_history[-5:]
        
        # Calculate averages
        avg_time_per_page = sum(p.time_per_page for p in recent) / len(recent)
        avg_memory_per_page = sum(p.memory_per_page for p in recent) / len(recent)
        
        # Target thresholds
        target_time_per_chunk = 5.0  # 5 seconds per chunk
        target_memory_per_chunk = 100.0  # 100 MB per chunk
        
        # Calculate size based on time constraint
        if avg_time_per_page > 0:
            time_based_size = int(target_time_per_chunk / avg_time_per_page)
        else:
            time_based_size = self.base_chunk_size
        
        # Calculate size based on memory constraint
        if avg_memory_per_page > 0:
            memory_based_size = int(target_memory_per_chunk / avg_memory_per_page)
        else:
            memory_based_size = self.base_chunk_size
        
        # Use the more conservative estimate
        optimal_size = min(time_based_size, memory_based_size)
        
        # Apply bounds
        optimal_size = max(self.min_chunk_size, min(optimal_size, self.max_chunk_size))
        
        # Gradual adjustment (avoid drastic changes)
        if abs(optimal_size - self.current_chunk_size) > self.current_chunk_size * 0.5:
            # Limit change to 50% increase/decrease
            if optimal_size > self.current_chunk_size:
                optimal_size = int(self.current_chunk_size * 1.5)
            else:
                optimal_size = int(self.current_chunk_size * 0.5)
        
        self.current_chunk_size = optimal_size
        return optimal_size
    
    def record_performance(self, 
                          chunk_size: int,
                          processing_time: float,
                          memory_used: float):
        """Record performance metrics for a processed chunk
        
        Args:
            chunk_size: Number of pages in chunk
            processing_time: Time taken to process chunk
            memory_used: Memory used during processing
        """
        if chunk_size <= 0:
            return
        
        metrics = PerformanceMetrics(
            chunk_size=chunk_size,
            time_per_page=processing_time / chunk_size,
            memory_per_page=memory_used / chunk_size,
            total_time=processing_time,
            total_memory=memory_used
        )
        
        self.performance_history.append(metrics)
        
        # Keep history size manageable
        if len(self.performance_history) > 100:
            self.performance_history.pop(0)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics
        
        Returns:
            Dictionary with performance statistics
        """
        if not self.performance_history:
            return {
                'samples': 0,
                'current_chunk_size': self.current_chunk_size,
                'avg_time_per_page': 0,
                'avg_memory_per_page': 0,
                'avg_efficiency': 0
            }
        
        recent = self.performance_history[-10:]
        
        return {
            'samples': len(self.performance_history),
            'current_chunk_size': self.current_chunk_size,
            'avg_time_per_page': sum(p.time_per_page for p in recent) / len(recent),
            'avg_memory_per_page': sum(p.memory_per_page for p in recent) / len(recent),
            'avg_efficiency': sum(p.efficiency_score() for p in recent) / len(recent)
        }
    
    def should_adjust(self) -> bool:
        """Check if chunk size should be adjusted
        
        Returns:
            True if adjustment is recommended
        """
        # Need at least 3 samples
        if len(self.performance_history) < 3:
            return False
        
        # Check recent efficiency scores
        recent = self.performance_history[-3:]
        recent_efficiency = sum(p.efficiency_score() for p in recent) / len(recent)
        
        # Adjust if efficiency is below threshold
        return recent_efficiency < 0.6
    
    def reset(self):
        """Reset performance history and chunk size"""
        self.performance_history.clear()
        self.current_chunk_size = self.base_chunk_size
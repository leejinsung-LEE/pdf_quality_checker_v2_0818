"""Data models for streaming processor"""

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple


@dataclass
class ChunkResult:
    """Result from processing a chunk of PDF pages"""
    chunk_index: int
    page_range: Tuple[int, int]
    analysis_data: Dict[str, Any]
    issues_found: List[Dict[str, Any]]
    memory_used: float
    processing_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'chunk_index': self.chunk_index,
            'page_range': self.page_range,
            'analysis_data': self.analysis_data,
            'issues_found': self.issues_found,
            'memory_used': self.memory_used,
            'processing_time': self.processing_time
        }
    
    @property
    def pages_processed(self) -> int:
        """Number of pages processed in this chunk"""
        return self.page_range[1] - self.page_range[0]
    
    @property
    def has_issues(self) -> bool:
        """Check if any issues were found"""
        return len(self.issues_found) > 0


@dataclass 
class ProcessingConfig:
    """Configuration for streaming processor"""
    chunk_size: int = 10
    max_memory_mb: int = 500
    enable_optimization: bool = True
    adaptive_chunking: bool = True
    cleanup_interval: int = 5


@dataclass
class PerformanceMetrics:
    """Performance metrics for chunk processing"""
    chunk_size: int
    time_per_page: float
    memory_per_page: float
    total_time: float
    total_memory: float
    
    def efficiency_score(self) -> float:
        """Calculate efficiency score (0-1)"""
        # Lower time and memory per page is better
        time_score = min(1.0, 1.0 / (self.time_per_page + 0.1))
        memory_score = min(1.0, 100.0 / (self.memory_per_page + 1))
        return (time_score + memory_score) / 2
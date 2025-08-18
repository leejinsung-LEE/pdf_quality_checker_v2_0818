"""Streaming PDF processor module - Public API"""

from .processor import StreamingPDFProcessor
from .adaptive import AdaptiveChunkProcessor
from .models import (
    ChunkResult,
    ProcessingConfig,
    PerformanceMetrics
)
from .memory_monitor import MemoryMonitor
from .page_processor import PageProcessor
from .chunk_handler import ChunkHandler
from .optimizer import PDFOptimizer

# Public exports
__all__ = [
    'StreamingPDFProcessor',
    'AdaptiveChunkProcessor',
    'ChunkResult',
    'ProcessingConfig',
    'PerformanceMetrics',
    'MemoryMonitor',
    'PageProcessor',
    'ChunkHandler',
    'PDFOptimizer'
]

# Version info
__version__ = '2.0.0'
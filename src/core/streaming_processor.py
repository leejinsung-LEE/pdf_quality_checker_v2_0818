"""
Streaming Processor - Modularized Wrapper

This file maintains backward compatibility while using the modularized components.
All functionality has been moved to the streaming_processor module.
"""

# Import all components from modularized module
from .streaming_processor import (
    StreamingPDFProcessor,
    AdaptiveChunkProcessor,
    ChunkResult,
    ProcessingConfig,
    PerformanceMetrics
)

# Re-export for backward compatibility
__all__ = [
    'StreamingPDFProcessor',
    'AdaptiveChunkProcessor',
    'ChunkResult',
    'ProcessingConfig',
    'PerformanceMetrics'
]
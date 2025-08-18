"""
Dynamic Batch Processor - Modularized Wrapper

This file maintains backward compatibility while using the modularized components.
All functionality has been moved to the dynamic_batch_processor module.
"""

# Import all components from modularized module
from .dynamic_batch_processor import (
    DynamicBatchProcessor,
    SmartBatchOptimizer,
    SystemResources,
    WorkerPoolConfig,
    PerformanceStats,
    BatchInfo
)

# Re-export for backward compatibility
__all__ = [
    'DynamicBatchProcessor',
    'SmartBatchOptimizer',
    'SystemResources',
    'WorkerPoolConfig',
    'PerformanceStats',
    'BatchInfo'
]
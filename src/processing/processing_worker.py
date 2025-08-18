"""
Processing Worker - Modularized Wrapper

This file maintains backward compatibility while using the modularized components.
All functionality has been moved to the processing_worker module.
"""

# Import all components from modularized module
from .processing_worker import (
    ProcessingWorker,
    WorkerPool,
    WorkerConfig,
    WorkerStatus,
    WorkerState,
    PoolStatus
)

# Re-export for backward compatibility
__all__ = [
    'ProcessingWorker',
    'WorkerPool',
    'WorkerConfig',
    'WorkerStatus',
    'WorkerState',
    'PoolStatus'
]
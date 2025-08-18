"""Dynamic batch processor module - Public API"""

from .processor import DynamicBatchProcessor
from .batch_optimizer import SmartBatchOptimizer
from .models import (
    SystemResources,
    WorkerPoolConfig,
    PerformanceStats,
    BatchInfo
)
from .resource_monitor import ResourceMonitor
from .worker_manager import DynamicWorkerManager

# Public exports
__all__ = [
    # Main classes
    'DynamicBatchProcessor',
    'SmartBatchOptimizer',
    
    # Models
    'SystemResources',
    'WorkerPoolConfig',
    'PerformanceStats',
    'BatchInfo',
    
    # Components
    'ResourceMonitor',
    'DynamicWorkerManager'
]

# Version info
__version__ = '2.0.0'
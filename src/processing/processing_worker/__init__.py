"""Processing worker module - Public API"""

from .worker import ProcessingWorker
from .pool import WorkerPool
from .models import (
    WorkerConfig,
    WorkerStatus,
    WorkerState,
    PoolStatus,
    TaskContext
)
from .task_handlers import TaskHandlers
from .statistics import WorkerStatistics, PoolStatistics

# Public exports
__all__ = [
    # Main classes
    'ProcessingWorker',
    'WorkerPool',
    
    # Models
    'WorkerConfig',
    'WorkerStatus',
    'WorkerState',
    'PoolStatus',
    'TaskContext',
    
    # Handlers and statistics
    'TaskHandlers',
    'WorkerStatistics',
    'PoolStatistics'
]

# Version info
__version__ = '2.0.0'
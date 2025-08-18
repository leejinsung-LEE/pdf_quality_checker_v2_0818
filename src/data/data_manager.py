"""
Data Manager - Modularized Wrapper

This file maintains backward compatibility while using the modularized components.
All functionality has been moved to the data_manager module.
"""

import threading
from typing import Optional

# Import from modularized components
from .data_manager import DataManager as ModularDataManager

# Re-export for backward compatibility
DataManager = ModularDataManager

# Singleton instance
_data_manager: Optional[DataManager] = None
_lock = threading.Lock()


def get_data_manager() -> DataManager:
    """
    Get singleton DataManager instance
    
    Returns:
        DataManager instance
    """
    global _data_manager
    
    if _data_manager is None:
        with _lock:
            if _data_manager is None:
                _data_manager = DataManager()
    
    return _data_manager


# Export public API
__all__ = [
    'DataManager',
    'get_data_manager'
]
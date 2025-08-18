"""Main DataManager class that orchestrates all modules"""

import threading
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import HistoryEntry, ProcessingStatus
from .models import HistoryFilter, StatisticsData
from .persistence import PersistenceHandler
from .cache_manager import CacheManager
from .history_handler import HistoryHandler
from .statistics import StatisticsGenerator


class DataManager:
    """Main data manager class that orchestrates all data operations"""
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize data manager
        
        Args:
            data_dir: Data storage directory
        """
        self.data_dir = data_dir or Path("data")
        
        # Initialize components
        self._persistence = PersistenceHandler(self.data_dir)
        self._cache = CacheManager()
        self._history = HistoryHandler()
        self._stats_gen = StatisticsGenerator()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Initialize
        self._initialize()
    
    def _initialize(self):
        """Initialize data manager components"""
        # Ensure directories exist
        self._persistence.ensure_directories()
        
        # Load history
        history_data = self._persistence.load_history()
        self._history.initialize(history_data.get('entries', []))
        
        # Load settings into cache
        settings = self._persistence.load_settings()
        for key, value in settings.items():
            self._cache.set(f"setting:{key}", value)
    
    def add_history(self, 
                   file_path: str,
                   status: ProcessingStatus = ProcessingStatus.PENDING,
                   profile: str = "default",
                   **kwargs) -> HistoryEntry:
        """Add processing history entry
        
        Args:
            file_path: File path
            status: Processing status
            profile: Profile used
            **kwargs: Additional fields
            
        Returns:
            Created HistoryEntry
        """
        with self._lock:
            entry = self._history.add_entry(file_path, status, profile, **kwargs)
            self._save_history()
            
            # Invalidate cache
            self._cache.delete("statistics")
            
            return entry
    
    def update_history(self, entry_id: int, **updates) -> bool:
        """Update history entry
        
        Args:
            entry_id: Entry ID
            **updates: Fields to update
            
        Returns:
            Success status
        """
        with self._lock:
            success = self._history.update_entry(entry_id, **updates)
            if success:
                self._save_history()
                self._cache.delete("statistics")
            return success
    
    def get_history(self, 
                   limit: Optional[int] = None,
                   offset: int = 0,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   filename_filter: Optional[str] = None,
                   status_filter: Optional[str] = None,
                   profile_filter: Optional[str] = None) -> List[HistoryEntry]:
        """Get filtered history entries
        
        Args:
            limit: Maximum entries
            offset: Starting position
            start_date: Start date filter
            end_date: End date filter
            filename_filter: Filename filter
            status_filter: Status filter
            profile_filter: Profile filter
            
        Returns:
            List of HistoryEntry objects
        """
        with self._lock:
            filter_params = HistoryFilter(
                limit=limit,
                offset=offset,
                start_date=start_date,
                end_date=end_date,
                filename_filter=filename_filter,
                status_filter=status_filter,
                profile_filter=profile_filter
            )
            return self._history.get_entries(filter_params)
    
    def get_history_by_id(self, entry_id: int) -> Optional[HistoryEntry]:
        """Get specific history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            HistoryEntry or None
        """
        with self._lock:
            return self._history.get_entry_by_id(entry_id)
    
    def get_history_count(self, 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         filename_filter: Optional[str] = None,
                         status_filter: Optional[str] = None,
                         profile_filter: Optional[str] = None) -> int:
        """Get count of filtered entries
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            filename_filter: Filename filter
            status_filter: Status filter
            profile_filter: Profile filter
            
        Returns:
            Count of matching entries
        """
        with self._lock:
            filter_params = HistoryFilter(
                start_date=start_date,
                end_date=end_date,
                filename_filter=filename_filter,
                status_filter=status_filter,
                profile_filter=profile_filter
            )
            return self._history.get_count(filter_params)
    
    def delete_history(self, entry_id: int) -> bool:
        """Delete history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Success status
        """
        with self._lock:
            success = self._history.delete_entry(entry_id)
            if success:
                self._save_history()
                self._cache.delete("statistics")
            return success
    
    def clear_history(self, older_than_days: Optional[int] = None):
        """Clear history entries
        
        Args:
            older_than_days: Delete entries older than this many days
        """
        with self._lock:
            self._history.clear_old_entries(older_than_days)
            self._save_history()
            self._cache.delete("statistics")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            # Check cache first
            cached = self._cache.get("statistics")
            if cached:
                return cached
            
            # Generate statistics
            entries = self._history.get_entries()
            stats = self._stats_gen.calculate(entries)
            result = stats.to_dict()
            
            # Cache for 5 minutes
            self._cache.set("statistics", result, ttl=300)
            
            return result
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get setting value
        
        Args:
            key: Setting key
            default: Default value
            
        Returns:
            Setting value or default
        """
        cached = self._cache.get(f"setting:{key}")
        return cached if cached is not None else default
    
    def set_setting(self, key: str, value: Any):
        """Set setting value
        
        Args:
            key: Setting key
            value: Setting value
        """
        self._cache.set(f"setting:{key}", value)
        
        # Save all settings
        settings = {}
        for cache_key in self._cache.get_keys():
            if cache_key.startswith("setting:"):
                setting_key = cache_key[8:]  # Remove "setting:" prefix
                settings[setting_key] = self._cache.get(cache_key)
        
        self._persistence.save_settings(settings)
    
    def get_recent_files(self, count: int = 10) -> List[str]:
        """Get recent file paths
        
        Args:
            count: Maximum number of files
            
        Returns:
            List of file paths
        """
        with self._lock:
            return self._history.get_recent_files(count)
    
    def _save_history(self):
        """Save history to file"""
        entries = self._history.export_entries()
        self._persistence.save_history(entries)
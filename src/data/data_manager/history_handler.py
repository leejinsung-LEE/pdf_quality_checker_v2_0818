"""History management operations"""

from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from ..models import HistoryEntry, ProcessingStatus
from .models import HistoryFilter


class HistoryHandler:
    """Handles history operations"""
    
    def __init__(self):
        """Initialize history handler"""
        self._history: List[HistoryEntry] = []
        self._next_id = 1
    
    def initialize(self, entries: List[Dict[str, Any]]):
        """Initialize history from loaded data
        
        Args:
            entries: List of history entry dictionaries
        """
        self._history = [
            HistoryEntry.from_dict(entry) for entry in entries
        ]
        
        if self._history:
            self._next_id = max(entry.id for entry in self._history) + 1
    
    def add_entry(self, 
                  file_path: str,
                  status: ProcessingStatus = ProcessingStatus.PENDING,
                  profile: str = "default",
                  **kwargs) -> HistoryEntry:
        """Add new history entry
        
        Args:
            file_path: File path
            status: Processing status
            profile: Profile used
            **kwargs: Additional fields
            
        Returns:
            Created HistoryEntry
        """
        path = Path(file_path)
        
        entry = HistoryEntry(
            id=self._next_id,
            file_path=str(path),
            file_name=path.name,
            file_size=path.stat().st_size if path.exists() else 0,
            processed_at=datetime.now(),
            status=status,
            profile_used=profile,
            **kwargs
        )
        
        self._history.append(entry)
        self._next_id += 1
        
        return entry
    
    def update_entry(self, entry_id: int, **updates) -> bool:
        """Update history entry
        
        Args:
            entry_id: Entry ID
            **updates: Fields to update
            
        Returns:
            Success status
        """
        for entry in self._history:
            if entry.id == entry_id:
                for key, value in updates.items():
                    if hasattr(entry, key):
                        setattr(entry, key, value)
                return True
        return False
    
    def get_entries(self, filter_params: Optional[HistoryFilter] = None) -> List[HistoryEntry]:
        """Get filtered history entries
        
        Args:
            filter_params: Filter parameters
            
        Returns:
            List of HistoryEntry objects
        """
        if filter_params is None:
            filter_params = HistoryFilter()
        
        # Apply filters
        filtered = self._history.copy()
        
        if filter_params.filename_filter:
            filtered = [
                e for e in filtered 
                if filter_params.filename_filter.lower() in e.file_name.lower()
            ]
        
        if filter_params.status_filter and filter_params.status_filter != "all":
            if filter_params.status_filter == "success":
                filtered = [e for e in filtered if e.status == ProcessingStatus.COMPLETED]
            elif filter_params.status_filter == "error":
                filtered = [e for e in filtered if e.status == ProcessingStatus.FAILED]
            elif filter_params.status_filter == "warning":
                filtered = [
                    e for e in filtered 
                    if e.status == ProcessingStatus.COMPLETED and e.warning_count > 0
                ]
        
        if filter_params.profile_filter and filter_params.profile_filter != "all":
            filtered = [e for e in filtered if e.profile_used == filter_params.profile_filter]
        
        if filter_params.start_date:
            filtered = [e for e in filtered if e.processed_at >= filter_params.start_date]
        
        if filter_params.end_date:
            filtered = [e for e in filtered if e.processed_at <= filter_params.end_date]
        
        # Sort by date (newest first)
        filtered.sort(key=lambda x: x.processed_at, reverse=True)
        
        # Apply pagination
        if filter_params.limit:
            start = filter_params.offset
            end = filter_params.offset + filter_params.limit
            return filtered[start:end]
        else:
            return filtered[filter_params.offset:]
    
    def get_entry_by_id(self, entry_id: int) -> Optional[HistoryEntry]:
        """Get specific history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            HistoryEntry or None
        """
        for entry in self._history:
            if entry.id == entry_id:
                return entry
        return None
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete history entry
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Success status
        """
        for i, entry in enumerate(self._history):
            if entry.id == entry_id:
                del self._history[i]
                return True
        return False
    
    def clear_old_entries(self, older_than_days: Optional[int] = None):
        """Clear old or all entries
        
        Args:
            older_than_days: Delete entries older than this many days
        """
        if older_than_days:
            cutoff_date = datetime.now() - timedelta(days=older_than_days)
            self._history = [
                e for e in self._history 
                if e.processed_at > cutoff_date
            ]
        else:
            self._history = []
    
    def get_recent_files(self, count: int = 10) -> List[str]:
        """Get recent unique file paths
        
        Args:
            count: Maximum number of files
            
        Returns:
            List of file paths
        """
        recent = []
        seen = set()
        
        for entry in sorted(self._history, 
                           key=lambda x: x.processed_at, 
                           reverse=True):
            if entry.file_path not in seen:
                recent.append(entry.file_path)
                seen.add(entry.file_path)
                
                if len(recent) >= count:
                    break
        
        return recent
    
    def get_count(self, filter_params: Optional[HistoryFilter] = None) -> int:
        """Get count of filtered entries
        
        Args:
            filter_params: Filter parameters
            
        Returns:
            Count of matching entries
        """
        if filter_params:
            # Use limit=None to get all matching entries
            temp_filter = HistoryFilter(**filter_params.__dict__)
            temp_filter.limit = None
            filtered = self.get_entries(temp_filter)
            return len(filtered)
        return len(self._history)
    
    def export_entries(self) -> List[Dict[str, Any]]:
        """Export all entries as dictionaries
        
        Returns:
            List of entry dictionaries
        """
        return [entry.to_dict() for entry in self._history]
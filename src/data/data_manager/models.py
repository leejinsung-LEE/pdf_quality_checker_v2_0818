"""Data management models"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


@dataclass
class HistoryFilter:
    """Filter criteria for history queries"""
    limit: Optional[int] = None
    offset: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    filename_filter: Optional[str] = None
    status_filter: Optional[str] = None
    profile_filter: Optional[str] = None


@dataclass
class CacheEntry:
    """Cache entry model"""
    key: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: Optional[int] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        elapsed = (datetime.now() - self.timestamp).total_seconds()
        return elapsed > self.ttl


@dataclass
class StatisticsData:
    """Data statistics model"""
    total: int = 0
    completed: int = 0
    failed: int = 0
    average_score: float = 0.0
    total_errors: int = 0
    total_warnings: int = 0
    total_processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'total': self.total,
            'completed': self.completed,
            'failed': self.failed,
            'average_score': self.average_score,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'total_processing_time': self.total_processing_time
        }


@dataclass  
class SettingsSchema:
    """Settings schema model"""
    last_cleanup: Optional[str] = None
    history_retention_days: int = 30
    cache_ttl: int = 3600
    max_cache_size: int = 100
    auto_save: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'last_cleanup': self.last_cleanup,
            'history_retention_days': self.history_retention_days,
            'cache_ttl': self.cache_ttl,
            'max_cache_size': self.max_cache_size,
            'auto_save': self.auto_save
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SettingsSchema':
        """Create from dictionary"""
        return cls(
            last_cleanup=data.get('last_cleanup'),
            history_retention_days=data.get('history_retention_days', 30),
            cache_ttl=data.get('cache_ttl', 3600),
            max_cache_size=data.get('max_cache_size', 100),
            auto_save=data.get('auto_save', True)
        )
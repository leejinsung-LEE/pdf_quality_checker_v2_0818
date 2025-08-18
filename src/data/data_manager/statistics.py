"""Statistics generation module"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..models import HistoryEntry, ProcessingStatus
from .models import StatisticsData


class StatisticsGenerator:
    """Generate statistics from history data"""
    
    @staticmethod
    def calculate(entries: List[HistoryEntry]) -> StatisticsData:
        """Calculate statistics from history entries
        
        Args:
            entries: List of history entries
            
        Returns:
            StatisticsData object
        """
        stats = StatisticsData()
        
        if not entries:
            return stats
        
        # Basic counts
        stats.total = len(entries)
        
        # Status counts
        completed_entries = [
            e for e in entries 
            if e.status == ProcessingStatus.COMPLETED
        ]
        failed_entries = [
            e for e in entries 
            if e.status == ProcessingStatus.FAILED
        ]
        
        stats.completed = len(completed_entries)
        stats.failed = len(failed_entries)
        
        # Calculate average score
        scores = [
            e.quality_score for e in completed_entries 
            if e.quality_score is not None
        ]
        if scores:
            stats.average_score = sum(scores) / len(scores)
        
        # Sum errors and warnings
        stats.total_errors = sum(e.error_count for e in entries)
        stats.total_warnings = sum(e.warning_count for e in entries)
        
        # Total processing time
        stats.total_processing_time = sum(
            e.processing_time for e in entries 
            if e.processing_time is not None
        )
        
        return stats
    
    @staticmethod
    def calculate_daily_stats(entries: List[HistoryEntry], days: int = 7) -> Dict[str, Any]:
        """Calculate daily statistics
        
        Args:
            entries: List of history entries
            days: Number of days to calculate
            
        Returns:
            Dictionary with daily statistics
        """
        daily_stats = {}
        today = datetime.now().date()
        
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.isoformat()
            
            # Filter entries for this day
            day_entries = [
                e for e in entries
                if e.processed_at.date() == date
            ]
            
            daily_stats[date_str] = {
                'total': len(day_entries),
                'completed': len([e for e in day_entries if e.status == ProcessingStatus.COMPLETED]),
                'failed': len([e for e in day_entries if e.status == ProcessingStatus.FAILED])
            }
        
        return daily_stats
    
    @staticmethod
    def calculate_profile_stats(entries: List[HistoryEntry]) -> Dict[str, Dict[str, Any]]:
        """Calculate statistics by profile
        
        Args:
            entries: List of history entries
            
        Returns:
            Dictionary with profile statistics
        """
        profile_stats = {}
        
        # Group by profile
        profiles = set(e.profile_used for e in entries)
        
        for profile in profiles:
            profile_entries = [e for e in entries if e.profile_used == profile]
            
            completed = [e for e in profile_entries if e.status == ProcessingStatus.COMPLETED]
            failed = [e for e in profile_entries if e.status == ProcessingStatus.FAILED]
            
            scores = [e.quality_score for e in completed if e.quality_score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            profile_stats[profile] = {
                'total': len(profile_entries),
                'completed': len(completed),
                'failed': len(failed),
                'average_score': avg_score,
                'success_rate': len(completed) / len(profile_entries) if profile_entries else 0
            }
        
        return profile_stats
    
    @staticmethod
    def calculate_error_distribution(entries: List[HistoryEntry]) -> Dict[str, int]:
        """Calculate error type distribution
        
        Args:
            entries: List of history entries
            
        Returns:
            Dictionary with error counts by type
        """
        error_dist = {
            'critical': 0,
            'major': 0,
            'minor': 0,
            'warning': 0
        }
        
        for entry in entries:
            # This is simplified - actual implementation would need error details
            if entry.error_count > 0:
                if entry.status == ProcessingStatus.FAILED:
                    error_dist['critical'] += entry.error_count
                else:
                    error_dist['major'] += entry.error_count
            
            if entry.warning_count > 0:
                error_dist['warning'] += entry.warning_count
        
        return error_dist
    
    @staticmethod
    def calculate_processing_time_stats(entries: List[HistoryEntry]) -> Dict[str, float]:
        """Calculate processing time statistics
        
        Args:
            entries: List of history entries
            
        Returns:
            Dictionary with time statistics
        """
        times = [e.processing_time for e in entries if e.processing_time is not None]
        
        if not times:
            return {
                'min': 0,
                'max': 0,
                'average': 0,
                'total': 0
            }
        
        return {
            'min': min(times),
            'max': max(times),
            'average': sum(times) / len(times),
            'total': sum(times)
        }
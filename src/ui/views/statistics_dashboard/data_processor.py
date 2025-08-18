"""
데이터 프로세서 - 통계 데이터 처리
"""

from typing import TYPE_CHECKING, Dict, Any
from datetime import datetime, timedelta
from functools import lru_cache
import hashlib

if TYPE_CHECKING:
    from .base import StatisticsDashboardView


class DataProcessor:
    """데이터 프로세서"""
    
    def __init__(self, view: 'StatisticsDashboardView'):
        self.view = view
        
    def get_statistics(self, period: str) -> Dict[str, Any]:
        """통계 데이터 가져오기 (캠싱 적용)"""
        # 캠시 키 생성 (날짜와 기간으로)
        cache_key = self._get_cache_key(period)
        
        # 캠시된 결과 사용
        return self._get_cached_statistics(cache_key, period)
    
    def _get_cache_key(self, period: str) -> str:
        """캠시 키 생성"""
        # 현재 시간을 분 단위로 잘라서 캠시 키 생성
        now = datetime.now()
        time_str = now.strftime("%Y%m%d%H%M")  # 분 단위 캠싱
        return hashlib.md5(f"{period}_{time_str}".encode()).hexdigest()
    
    @lru_cache(maxsize=32)
    def _get_cached_statistics(self, cache_key: str, period: str) -> Dict[str, Any]:
        """캠싱된 통계 데이터 가져오기"""
        # 기간별 날짜 범위 계산
        end_date = datetime.now()
        
        if period == "day":
            start_date = end_date - timedelta(days=7)
        elif period == "week":
            start_date = end_date - timedelta(weeks=4)
        elif period == "month":
            start_date = end_date - timedelta(days=365)
        else:  # year
            start_date = end_date - timedelta(days=365 * 5)
            
        # 히스토리 가져오기
        history_list = self.view.history_manager.search_history(
            start_date=start_date, end_date=end_date
        )
        
        # 통계 계산
        stats = self._calculate_statistics(history_list, period)
        
        return stats
        
    def _calculate_statistics(self, history_list, period: str) -> Dict[str, Any]:
        """통계 계산"""
        stats = {
            'total_files': len(history_list),
            'success_count': 0,
            'error_count': 0,
            'total_processing_time': 0,
            'avg_processing_time': 0,
            'success_rate': 0,
            'total_errors': 0,
            'daily_stats': {},
            'weekly_stats': {},
            'monthly_stats': {},
            'yearly_stats': {}
        }
        
        if not history_list:
            return stats
            
        # 기본 통계 계산
        for history in history_list:
            if history.status == "completed":
                stats['success_count'] += 1
            else:
                stats['error_count'] += 1
                
            if history.processing_time:
                stats['total_processing_time'] += history.processing_time
                
            if history.error_count:
                stats['total_errors'] += history.error_count
                
        # 평균 계산
        if stats['total_files'] > 0:
            stats['avg_processing_time'] = stats['total_processing_time'] / stats['total_files']
            stats['success_rate'] = (stats['success_count'] / stats['total_files']) * 100
            
        # 기간별 통계 계산
        if period == "day":
            stats['daily_stats'] = self._calculate_daily_stats(history_list)
        elif period == "week":
            stats['weekly_stats'] = self._calculate_weekly_stats(history_list)
        elif period == "month":
            stats['monthly_stats'] = self._calculate_monthly_stats(history_list)
        else:  # year
            stats['yearly_stats'] = self._calculate_yearly_stats(history_list)
            
        return stats
        
    def _calculate_daily_stats(self, history_list) -> Dict[str, int]:
        """일별 통계 계산"""
        daily_stats = {}
        today = datetime.now().date()
        
        # 최근 7일
        for i in range(7):
            day = today - timedelta(days=i)
            count = sum(1 for h in history_list 
                       if h.timestamp and h.timestamp.date() == day)
            daily_stats[f"day_{i}"] = count
            
        return daily_stats
        
    def _calculate_weekly_stats(self, history_list) -> Dict[str, int]:
        """주별 통계 계산"""
        weekly_stats = {}
        today = datetime.now().date()
        
        # 최근 4주
        for i in range(4):
            week_start = today - timedelta(weeks=i+1)
            week_end = today - timedelta(weeks=i)
            count = sum(1 for h in history_list 
                       if h.timestamp and week_start <= h.timestamp.date() < week_end)
            weekly_stats[f"week_{i}"] = count
            
        return weekly_stats
        
    def _calculate_monthly_stats(self, history_list) -> Dict[str, int]:
        """월별 통계 계산"""
        monthly_stats = {}
        
        # 12개월
        for i in range(12):
            count = sum(1 for h in history_list 
                       if h.timestamp and h.timestamp.month == i+1)
            monthly_stats[f"month_{i}"] = count
            
        return monthly_stats
        
    def _calculate_yearly_stats(self, history_list) -> Dict[str, int]:
        """연도별 통계 계산"""
        yearly_stats = {}
        current_year = datetime.now().year
        
        # 최근 5년
        for i in range(5):
            year = current_year - i
            count = sum(1 for h in history_list 
                       if h.timestamp and h.timestamp.year == year)
            yearly_stats[f"year_{i}"] = count
            
        return yearly_stats
        
    def get_date_range_text(self, period: str) -> str:
        """날짜 범위 텍스트 생성"""
        now = datetime.now()
        
        if period == "day":
            start = now - timedelta(days=7)
            return f"{start.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        elif period == "week":
            start = now - timedelta(weeks=4)
            return f"{start.strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        elif period == "month":
            return f"{now.year}년"
        else:  # year
            return f"{now.year - 4} ~ {now.year}"
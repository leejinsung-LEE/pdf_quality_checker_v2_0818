"""
처리 이력 필터 관리
기능: 필터링 및 검색 로직
최종 수정: 2025-01-12
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple, TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import HistoryView


class FilterManager:
    """필터 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'HistoryView'):
        self.view = view
        
    def apply_filters(self):
        """필터 적용"""
        # 날짜 범위 계산
        start_date, end_date = self.calculate_date_range()
        
        # 필터 값 변환
        status_map = {
            "전체": "all",
            "완료": "completed",
            "오류": "error",
            "취소": "cancelled"
        }
        status_filter = status_map.get(self.view.status_filter.get(), "all")
        
        profile_filter = self.view.profile_filter.get()
        if profile_filter == "전체":
            profile_filter = "all"
        
        # 전체 개수 조회
        self.view.total_items = self.view.data_manager.get_history_count(
            start_date=start_date,
            end_date=end_date,
            filename_filter=self.view.search_var.get(),
            status_filter=status_filter,
            profile_filter=profile_filter
        )
        
        # 페이지 계산
        total_pages = max(1, (self.view.total_items + self.view.items_per_page - 1) // self.view.items_per_page)
        if self.view.current_page > total_pages:
            self.view.current_page = total_pages
        
        # 이력 조회
        offset = (self.view.current_page - 1) * self.view.items_per_page
        self.view.current_entries = self.view.data_manager.get_history(
            start_date=start_date,
            end_date=end_date,
            filename_filter=self.view.search_var.get(),
            status_filter=status_filter,
            profile_filter=profile_filter,
            limit=self.view.items_per_page,
            offset=offset
        )
        
        # 테이블 업데이트
        if hasattr(self.view, 'list_manager'):
            self.view.list_manager.update_table()
        
        # UI 업데이트
        self.view.update_ui_state()
    
    def calculate_date_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """날짜 범위 계산"""
        date_range = self.view.date_range.get()
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_range == "all" or date_range == "전체":
            return None, None
        elif date_range == "today" or date_range == "오늘":
            return today, now
        elif date_range == "yesterday" or date_range == "어제":
            yesterday = today - timedelta(days=1)
            return yesterday, today
        elif date_range == "week" or date_range == "이번 주":
            start = today - timedelta(days=today.weekday())
            return start, now
        elif date_range == "month" or date_range == "이번 달":
            start = today.replace(day=1)
            return start, now
        elif date_range == "last_month" or date_range == "지난 달":
            last_month = today.replace(day=1) - timedelta(days=1)
            start = last_month.replace(day=1)
            end = today.replace(day=1) - timedelta(seconds=1)
            return start, end
        elif date_range == "custom" or date_range == "사용자 지정":
            # 사용자 지정 날짜 사용
            if self.view.custom_start_date and self.view.custom_end_date:
                start = datetime.combine(self.view.custom_start_date, datetime.min.time())
                end = datetime.combine(self.view.custom_end_date, datetime.max.time())
                return start, end
        
        return None, None
    
    def update_profile_filter(self):
        """프로파일 필터 옵션 업데이트"""
        # 고유한 프로파일 목록 가져오기 (간단한 방법)
        profiles = ["전체", "default", "strict", "quick", "web"]
        
        # 실제로는 데이터베이스에서 조회해야 하지만, 
        # 성능을 위해 하드코딩하거나 캐시 사용
        
        if 'profile_menu' in self.view.widgets:
            self.view.widgets['profile_menu'].configure(values=profiles)
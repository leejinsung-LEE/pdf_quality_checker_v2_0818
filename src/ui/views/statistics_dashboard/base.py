"""
통계 대시보드 베이스 클래스
"""

import customtkinter as ctk
from typing import Dict, Any

from ....data.history_manager import get_history_manager

from .ui_builder import UIBuilder
from .chart_manager import ChartManager
from .data_processor import DataProcessor
from .handlers import EventHandler


class StatisticsDashboardView(ctk.CTkFrame):
    """통계 대시보드 뷰"""
    
    def __init__(self, parent, **kwargs):
        """
        초기화
        
        Args:
            parent: 부모 위젯
        """
        super().__init__(parent, **kwargs)
        
        # 히스토리 매니저
        self.history_manager = get_history_manager()
        
        # 현재 선택된 기간
        self.current_period = "day"
        
        # UI 위젯 딕셔너리
        self.widgets = {}
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.chart_manager = ChartManager(self)
        self.data_processor = DataProcessor(self)
        self.event_handler = EventHandler(self)
        
        # UI 설정
        self._setup_ui()
        
        # 초기 데이터 로드
        self.refresh_data()
        
    def _setup_ui(self):
        """UI 구성"""
        # 메인 레이아웃
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # UI 빌더로 위임
        self.ui_builder.create_ui()
        
    def refresh_data(self):
        """데이터 새로고침"""
        # 통계 가져오기
        stats = self.data_processor.get_statistics(self.current_period)
        
        # UI 업데이트
        self._update_ui(stats)
        
    def _update_ui(self, stats: Dict[str, Any]):
        """UI 업데이트"""
        # 요약 카드 업데이트
        self.ui_builder.update_summary_cards(stats)
        
        # 차트 업데이트
        self.chart_manager.update_chart(stats)
        
        # 최근 목록 업데이트
        self.ui_builder.update_recent_list()
        
    def on_period_change(self, value):
        """기간 변경 이벤트"""
        period_map = {
            "일별": "day",
            "주별": "week",
            "월별": "month",
            "연별": "year"
        }
        self.current_period = period_map.get(value, "day")
        self.refresh_data()
        
        # 날짜 레이블 업데이트
        if 'date_label' in self.widgets:
            self.widgets['date_label'].configure(
                text=self.data_processor.get_date_range_text(self.current_period)
            )
    
    def export_statistics(self):
        """통계 내보내기"""
        self.event_handler.export_statistics()
    
    def show_more_history(self):
        """더 많은 이력 보기"""
        self.event_handler.show_more_history()
    
    def add_processed_file(self, file_item):
        """처리된 파일 추가 (외부에서 호출)"""
        # 차트 업데이트를 위해 새로고침
        self.refresh_data()
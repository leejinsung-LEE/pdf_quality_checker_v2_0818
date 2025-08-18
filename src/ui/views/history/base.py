"""
처리 이력 뷰 - 메인 클래스
기능: PDF 처리 이력 조회 및 관리
의존성: customtkinter, tkinter, data_manager
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: 처리 이력 조회, 필터링, 관리 UI 제공
- 입력: 필터 조건, 날짜 범위
- 출력: 이력 목록, CSV 파일
- 상태: 현재 페이지, 선택 항목, 필터 설정
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, date
from pathlib import Path

# 데이터 매니저
from ...controllers import FileController
from ....data import get_data_manager, HistoryEntry

# 헬퍼 클래스 import
from .ui_builder import UIBuilder
from .history_list import HistoryListManager
from .filters import FilterManager
from .handlers import EventHandler


class HistoryView(ctk.CTkFrame):
    """처리 이력 뷰 - PDF 처리 이력을 표시하고 관리"""
    
    def __init__(self, parent, controller: FileController, **kwargs):
        """
        뷰 초기화
        
        Args:
            parent: 부모 위젯
            controller: 파일 컨트롤러
            **kwargs: 추가 옵션
        """
        super().__init__(parent, **kwargs)
        
        self.controller = controller
        self.data_manager = get_data_manager()
        
        # UI 상태 및 위젯 참조
        self.widgets = {}  # 위젯 참조 저장
        self.selected_ids: Set[int] = set()
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        
        # 필터 변수
        self.search_var = tk.StringVar()
        self.status_filter = tk.StringVar(value="all")
        self.profile_filter = tk.StringVar(value="all")
        self.date_range = tk.StringVar(value="all")
        self.custom_start_date: Optional[date] = None
        self.custom_end_date: Optional[date] = None
        self.per_page_var = tk.StringVar(value="50")
        
        # 현재 표시 중인 이력
        self.current_entries: List[HistoryEntry] = []
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_card': '#2a2a2a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#667eea',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'border': '#404040'
        }
        
        # 헬퍼 초기화
        self.ui_builder = UIBuilder(self)
        self.list_manager = HistoryListManager(self)
        self.filter_manager = FilterManager(self)
        self.event_handler = EventHandler(self)
        
        # UI 생성
        self._create_ui()
        
        # 초기 데이터 로드
        self.refresh_data()
    
    def _create_ui(self):
        """UI 구성"""
        self.configure(fg_color=self.colors['bg_primary'])
        self.ui_builder.create_ui()
    
    def refresh_data(self):
        """데이터 새로고침"""
        self.current_page = 1
        self.apply_filters()
        self.filter_manager.update_profile_filter()
    
    def apply_filters(self):
        """필터 적용"""
        self.filter_manager.apply_filters()
        
    def update_ui_state(self):
        """UI 상태 업데이트"""
        self.list_manager.update_ui_state()
        
    def show_details(self, entry: HistoryEntry):
        """상세 정보 표시"""
        self.event_handler.show_details(entry)
        
    def prev_page(self):
        """이전 페이지"""
        self.event_handler.prev_page()
        
    def next_page(self):
        """다음 페이지"""
        self.event_handler.next_page()
        
    def delete_selected(self):
        """선택 항목 삭제"""
        self.event_handler.delete_selected()
        
    def export_to_csv(self):
        """CSV로 내보내기"""
        self.event_handler.export_to_csv()
        
    def clear_all_history(self):
        """전체 이력 삭제"""
        self.event_handler.clear_all_history()
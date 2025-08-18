"""
Process Monitor View 기본 클래스
기능: 뷰 초기화, 상태 관리, 기본 설정
의존성: customtkinter, FileController, DataManager
최종 수정: 2025-01-11
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional, Set
from datetime import date
from pathlib import Path

from ...controllers import FileController, FileStatus, FileItem
from ....data import get_data_manager, HistoryEntry
from .ui_builders import UIBuilder
from .tree_handlers import TreeHandler
from .event_handlers import EventHandler
from .actions import ActionHandler


class ProcessMonitorView(ctk.CTkFrame):
    """
    통합 처리 모니터 뷰 - 실시간 처리와 처리 이력을 통합 표시
    
    주요 기능:
    - 실시간 파일 처리 모니터링
    - 처리 이력 조회 및 관리
    - 필터링 및 검색
    - 보고서 생성 및 내보내기
    """
    
    # 상태별 아이콘
    STATUS_ICONS = {
        FileStatus.WAITING: '⏳',
        FileStatus.PROCESSING: '⚙️',
        FileStatus.COMPLETED: '✅',
        FileStatus.ERROR: '❌',
        FileStatus.CANCELLED: '🚫'
    }
    
    # 상태별 색상 태그
    STATUS_TAGS = {
        FileStatus.WAITING: 'waiting',
        FileStatus.PROCESSING: 'processing',
        FileStatus.COMPLETED: 'success',
        FileStatus.ERROR: 'error',
        FileStatus.CANCELLED: 'cancelled'
    }
    
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
        
        # UI 상태 - 실시간 처리
        self.selected_items: Set[str] = set()
        self.filter_status = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.folder_filter = tk.StringVar(value="all")
        
        # UI 상태 - 처리 이력
        self.selected_history_ids: Set[int] = set()
        self.current_page = 1
        self.items_per_page = 100  # 성능을 위해 100개로 제한
        self.total_items = 0
        
        # 필터 변수 (통합)
        self.date_range = tk.StringVar(value="today")
        self.profile_filter = tk.StringVar(value="all")
        self.custom_start_date: Optional[date] = None
        self.custom_end_date: Optional[date] = None
        
        # 현재 표시 중인 데이터
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
            'info': '#17a2b8',
            'border': '#404040'
        }
        
        # 상하 분할 비율
        self.split_ratio = 0.6  # 상단 60%, 하단 40%
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.tree_handler = TreeHandler(self)
        self.event_handler = EventHandler(self)
        self.action_handler = ActionHandler(self)
        
        # UI 위젯 참조 (헬퍼 클래스에서 설정)
        self.header_frame = None
        self.filter_frame = None
        self.paned_window = None
        self.realtime_tree = None
        self.history_tree = None
        self.realtime_stats_label = None
        self.history_stats_label = None
        self.page_label = None
        
        # UI 생성
        self._create_ui()
        
        # 컨트롤러 콜백 설정
        self._setup_controller_callbacks()
        
        # 초기 데이터 로드
        self.refresh_all()
    
    def _create_ui(self):
        """UI 구성"""
        self.ui_builder.create_ui()
    
    def _setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        self.controller.on_file_added = self.tree_handler.on_file_added
        self.controller.on_status_changed = self.tree_handler.on_status_changed
        self.controller.on_progress_updated = self.tree_handler.on_progress_updated
        self.controller.on_file_removed = self.tree_handler.on_file_removed
    
    def refresh_all(self):
        """전체 새로고침"""
        self.tree_handler.refresh()
        self.tree_handler.refresh_history()
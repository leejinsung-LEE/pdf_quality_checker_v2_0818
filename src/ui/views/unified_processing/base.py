"""
통합 처리 뷰 - 메인 클래스
기능: 실시간 처리와 이력을 통합 표시하는 뷰의 핵심 클래스
의존성: customtkinter, FileController, DataManager
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: 실시간 처리 항목과 처리 이력을 하나의 리스트에 통합 표시
- 입력: parent 위젯, FileController
- 출력: 통합 처리 뷰 위젯
- 상태: selected_items, filter_status, search_var, all_items
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, List, Optional, Set, Union
from pathlib import Path
from datetime import datetime, timedelta

from ...controllers import FileController, FileStatus, FileItem
from ....data import get_data_manager, HistoryEntry

# 헬퍼 클래스 import
from .ui_builder import UIBuilder
from .data_handler import DataHandler
from .event_handler import EventHandler
from .action_handler import ActionHandler


class UnifiedProcessingView(ctk.CTkFrame):
    """
    통합 처리 뷰 - 실시간 처리와 처리 이력을 하나의 리스트에 표시
    
    주요 기능:
    - 실시간 파일 처리 모니터링
    - 처리 이력 조회 및 관리
    - 필터링 및 검색
    - 보고서 생성 및 내보내기
    
    아키텍처:
    - MVC 패턴의 View 컴포넌트
    - 헬퍼 클래스를 통한 책임 분리
    - 컨트롤러와 느슨한 결합
    """
    
    # 상태별 아이콘
    STATUS_ICONS = {
        FileStatus.WAITING: '⏳',
        FileStatus.PROCESSING: '⚙️',
        FileStatus.COMPLETED: '✅',
        FileStatus.ERROR: '❌',
        FileStatus.CANCELLED: '🚫',
        # 이력용 추가 상태
        'history_completed': '✅',
        'history_error': '❌',
        'history_warning': '⚠️'
    }
    
    # 상태별 색상 태그
    STATUS_TAGS = {
        FileStatus.WAITING: 'waiting',
        FileStatus.PROCESSING: 'processing',
        FileStatus.COMPLETED: 'success',
        FileStatus.ERROR: 'error',
        FileStatus.CANCELLED: 'cancelled',
        # 이력용 태그
        'history': 'history'
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
        
        # UI 상태
        self.selected_items: Set[str] = set()
        self.filter_status = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.date_range = tk.StringVar(value="today")
        self.profile_filter = tk.StringVar(value="all")
        
        # 통합 데이터
        self.all_items: Dict[str, Union[FileItem, HistoryEntry]] = {}
        self.max_history_items = 100  # 표시할 최대 이력 수
        
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
            'border': '#404040',
            'history': '#6c757d'  # 이력 항목용 색상
        }
        
        # UI 위젯 저장소
        self.widgets = {}
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.data_handler = DataHandler(self)
        self.event_handler = EventHandler(self)
        self.action_handler = ActionHandler(self)
        
        # UI 생성
        self._create_ui()
        
        # 컨트롤러 콜백 설정
        self.event_handler.setup_controller_callbacks()
        
        # 트리뷰 스타일 설정
        self.ui_builder.setup_tree_style()
        
        # 초기 데이터 로드
        self.refresh()
    
    def _create_ui(self):
        """UI 생성"""
        self.ui_builder.create_ui()
    
    def refresh(self):
        """전체 데이터 새로고침"""
        self.data_handler.refresh()
    
    def get_state(self) -> Dict:
        """현재 상태 반환"""
        return {
            'selected_items': list(self.selected_items),
            'filter_status': self.filter_status.get(),
            'search': self.search_var.get(),
            'date_range': self.date_range.get(),
            'profile_filter': self.profile_filter.get()
        }
    
    def set_state(self, state: Dict):
        """상태 설정"""
        if 'filter_status' in state:
            self.filter_status.set(state['filter_status'])
        if 'search' in state:
            self.search_var.set(state['search'])
        if 'date_range' in state:
            self.date_range.set(state['date_range'])
        if 'profile_filter' in state:
            self.profile_filter.set(state['profile_filter'])
        self.refresh()
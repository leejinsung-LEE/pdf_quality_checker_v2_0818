"""
처리 화면 뷰 - 메인 클래스
기능: 파일 처리 상태를 표시하고 관리하는 메인 뷰
의존성: customtkinter, FileController
최종 수정: 2025-01-12

AI 친화적 문서화:
- 역할: 파일 처리 상태 모니터링 및 관리
- 입력: parent 위젯, FileController
- 출력: 처리 화면 뷰 위젯
- 상태: selected_items, filter_status, search_var, column_visibility
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, Set
from pathlib import Path

from ...controllers import FileController, FileStatus

# 헬퍼 클래스 import
from .ui_builder import UIBuilder
from .file_list import FileListManager
from .handlers import EventHandler


class ProcessingView(ctk.CTkFrame):
    """
    처리 화면 - 파일 처리 상태를 표시하는 메인 뷰
    
    주요 기능:
    - 파일 처리 상태 실시간 모니터링
    - 파일 추가/제거/재처리
    - 필터링 및 검색
    - 보고서 보기
    
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
        
        # UI 상태
        self.selected_items: Set[str] = set()
        self.filter_status = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.folder_filter = tk.StringVar(value="all")
        
        # 컬럼 표시 설정
        self.column_visibility = {
            'icon': True,
            'filename': True,
            'folder': True,
            'profile': True,
            'size': True,
            'pages': True,
            'issues': True,
            'score': True,
            'time': True,
            'status': True
        }
        
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
        
        # UI 위젯 저장소
        self.widgets = {}
        
        # 트리뷰 (나중에 초기화됨)
        self.tree = None
        
        # 컨텍스트 메뉴 (나중에 초기화됨)
        self.context_menu = None
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.file_list_manager = FileListManager(self)
        self.event_handler = EventHandler(self)
        
        # UI 생성
        self._create_ui()
        
        # 컨트롤러 콜백 설정
        self.event_handler.setup_controller_callbacks()
        
        # 트리뷰 스타일 설정
        self.ui_builder.setup_tree_style()
    
    def _create_ui(self):
        """UI 생성"""
        self.ui_builder.create_ui()
    
    def refresh(self):
        """화면 새로고침"""
        # 통계 업데이트
        self.file_list_manager.update_statistics()
        
        # 필터 재적용
        self.file_list_manager.apply_filters()
    
    def get_state(self) -> Dict:
        """현재 상태 반환"""
        return {
            'selected_items': list(self.selected_items),
            'filter_status': self.filter_status.get(),
            'search': self.search_var.get(),
            'folder_filter': self.folder_filter.get()
        }
    
    def set_state(self, state: Dict):
        """상태 설정"""
        if 'filter_status' in state:
            self.filter_status.set(state['filter_status'])
        if 'search' in state:
            self.search_var.set(state['search'])
        if 'folder_filter' in state:
            self.folder_filter.set(state['folder_filter'])
        self.refresh()
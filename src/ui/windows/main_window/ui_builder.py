"""
UI 빌더 - 메인 윈도우 UI 구성
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

from ...components import Sidebar, MenuBar, StatusBar

# 새로운 메뉴바 (선택적 사용)
try:
    from ...components.menubar_v2 import MenuBarV2
    MENUBAR_V2_AVAILABLE = True
except ImportError:
    MENUBAR_V2_AVAILABLE = False
from ...views import (
    UnifiedProcessingView, DashboardView,
    StatisticsDashboardView, ProfileSettingsView
)

if TYPE_CHECKING:
    from .base import MainWindow


class UIBuilder:
    """UI 빌더"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def create_ui(self):
        """UI 생성"""
        # 메뉴바
        self._create_menubar()
        
        # 메인 컨테이너
        self._create_main_container()
        
        # 사이드바
        self._create_sidebar()
        
        # 콘텐츠 영역
        self._create_content_area()
        
        # 탭 컨테이너
        self._create_tab_container()
        
        # 뷰 생성
        self._create_views()
        
        # 상태바
        self._create_statusbar()
        
        # 이벤트 바인딩
        self._bind_tab_events()
        
        # 초기 탭 선택
        self.window.notebook.select(0)
    
    def _create_menubar(self):
        """메뉴바 생성"""
        # 새 UI 사용 여부 확인 (dialog_manager와 동일한 로직)
        use_new_ui = self._check_use_new_ui()
        
        if use_new_ui and MENUBAR_V2_AVAILABLE:
            # 새로운 메뉴바 V2 사용
            self.window.menubar = MenuBarV2(self.window)
        else:
            # 기존 메뉴바 사용
            self.window.menubar = MenuBar(self.window)
        
        self.window.config(menu=self.window.menubar)
        self.window.widgets['menubar'] = self.window.menubar
    
    def _check_use_new_ui(self) -> bool:
        """새 UI 사용 여부 확인"""
        # 환경변수 확인
        import os
        if os.environ.get('USE_NEW_UI', '').lower() in ('true', '1', 'yes'):
            return True
        
        # 설정에서 확인 (가능한 경우)
        try:
            if hasattr(self.window, 'settings_controller'):
                settings = self.window.settings_controller.get_settings()
                if hasattr(settings, 'use_new_ui'):
                    return settings.use_new_ui
        except:
            pass
        
        # 기본값: 새 UI 사용 (테스트 목적)
        return True
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill='both', expand=True)
        self.window.widgets['main_container'] = main_container
    
    def _create_sidebar(self):
        """사이드바 생성"""
        main_container = self.window.widgets['main_container']
        self.window.sidebar = Sidebar(main_container)
        self.window.sidebar.pack(side='left', fill='y')
        self.window.widgets['sidebar'] = self.window.sidebar
    
    def _create_content_area(self):
        """콘텐츠 영역 생성"""
        main_container = self.window.widgets['main_container']
        content_container = ctk.CTkFrame(main_container)
        content_container.pack(side='left', fill='both', expand=True)
        self.window.widgets['content_container'] = content_container
    
    def _create_tab_container(self):
        """탭 컨테이너 생성"""
        content_container = self.window.widgets['content_container']
        
        # 탭 컨테이너 (v1 스타일)
        tab_container = ctk.CTkFrame(content_container, fg_color="transparent")
        tab_container.pack(fill='both', expand=True, padx=10, pady=10)
        self.window.widgets['tab_container'] = tab_container
        
        # Notebook 위젯 생성
        self.window.notebook = ttk.Notebook(tab_container)
        self.window.notebook.pack(fill='both', expand=True)
        self.window.widgets['notebook'] = self.window.notebook
        
        # 탭 스타일 설정
        self._setup_tab_style()
    
    def _setup_tab_style(self):
        """탭 스타일 설정"""
        style = ttk.Style()
        
        # 탭 색상과 폰트 설정
        style.configure('TNotebook',
            background='#1a1a1a',
            borderwidth=0
        )
        style.configure('TNotebook.Tab',
            background='#2a2a2a',
            foreground='#ffffff',
            padding=(20, 10),
            font=('맑은 고딕', 11)
        )
        style.map('TNotebook.Tab',
            background=[('selected', '#667eea')],
            foreground=[('selected', '#ffffff')]
        )
    
    def _create_views(self):
        """뷰 생성 (탭으로)"""
        notebook = self.window.notebook
        
        # 통합 처리 뷰
        self.window.views['unified_processing'] = UnifiedProcessingView(
            notebook,
            self.window.file_controller
        )
        notebook.add(self.window.views['unified_processing'], text="📁 처리 현황")
        
        # 대시보드 뷰
        self.window.views['dashboard'] = DashboardView(
            notebook,
            self.window.file_controller
        )
        notebook.add(self.window.views['dashboard'], text="📊 대시보드")
        
        # 통계 대시보드 뷰
        self.window.views['statistics'] = StatisticsDashboardView(notebook)
        notebook.add(self.window.views['statistics'], text="📈 통계 분석")
        
        # 프로파일 설정 뷰
        self.window.views['profile_settings'] = ProfileSettingsView(notebook)
        notebook.add(self.window.views['profile_settings'], text="⚙️ 프로파일 설정")
        
        # widgets 딕셔너리에 추가
        self.window.widgets['views'] = self.window.views
    
    def _create_statusbar(self):
        """상태바 생성"""
        content_container = self.window.widgets['content_container']
        self.window.statusbar = StatusBar(content_container)
        self.window.statusbar.pack(side='bottom', fill='x')
        self.window.widgets['statusbar'] = self.window.statusbar
    
    def _bind_tab_events(self):
        """탭 이벤트 바인딩"""
        self.window.notebook.bind('<<NotebookTabChanged>>', 
                                 self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """탭 변경 이벤트 처리"""
        selected_tab = self.window.notebook.index('current')
        
        # ViewManager에 위임
        if hasattr(self.window, 'view_manager'):
            self.window.view_manager.on_tab_changed(selected_tab)
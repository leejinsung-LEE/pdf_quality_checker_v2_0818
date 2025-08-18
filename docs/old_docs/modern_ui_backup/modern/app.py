# src/ui/modern/app.py
"""
Modern UI 애플리케이션

Flet 기반의 현대적인 UI 메인 애플리케이션
"""

import flet as ft
from typing import Optional, Dict, Any
import logging
from pathlib import Path

# 컨트롤러 (Classic과 공유)
from ..controllers import (
    FileController, SettingsController, ProfileController,
    get_file_controller, get_settings_controller, get_profile_controller
)

logger = logging.getLogger(__name__)


class ModernApp:
    """Modern UI 메인 애플리케이션"""
    
    def __init__(self):
        """초기화"""
        self.page: Optional[ft.Page] = None
        self.current_view = "dashboard"
        
        # 컨트롤러 초기화 (Classic과 동일)
        self.file_controller = get_file_controller()
        self.settings_controller = get_settings_controller()
        self.profile_controller = get_profile_controller()
        
        # 뷰 컨테이너
        self.views: Dict[str, ft.Control] = {}
        
        # 컴포넌트
        self.sidebar = None
        self.content_area = None
        self.statusbar = None
        
        logger.info("Modern UI initialized")
    
    def run(self):
        """애플리케이션 실행"""
        ft.app(target=self.main)
    
    def main(self, page: ft.Page):
        """메인 함수"""
        self.page = page
        self._setup_page()
        self._create_layout()
        self._load_initial_view()
        
    def _setup_page(self):
        """페이지 설정"""
        self.page.title = "PDF Quality Checker v2.0 - Modern UI"
        self.page.window_width = 1400
        self.page.window_height = 800
        self.page.window_min_width = 1200
        self.page.window_min_height = 600
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        
        # Material 3 테마
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#6750A4",
                primary_container="#EADDFF",
                secondary="#625B71",
                tertiary="#7D5260",
                surface="#1C1B1F",
                background="#1C1B1F",
                error="#F2B8B5",
            ),
            use_material3=True,
        )
        
        # 이벤트 핸들러
        self.page.on_resize = self._on_resize
        
    def _create_layout(self):
        """레이아웃 생성"""
        # 사이드바 생성
        self._create_sidebar()
        
        # 컨텐츠 영역 생성
        self._create_content_area()
        
        # 상태바 생성
        self._create_statusbar()
        
        # 전체 레이아웃 구성
        main_layout = ft.Column([
            # 메인 영역 (사이드바 + 컨텐츠)
            ft.Row([
                self.sidebar,
                ft.VerticalDivider(width=1, color="#444444"),
                self.content_area,
            ], expand=True),
            
            # 상태바
            ft.Divider(height=1, color="#444444"),
            self.statusbar,
        ], spacing=0, expand=True)
        
        self.page.add(main_layout)
        
    def _create_sidebar(self):
        """사이드바 생성"""
        from .components import ModernSidebar
        self.sidebar = ModernSidebar(self)
        
    def _create_content_area(self):
        """컨텐츠 영역 생성"""
        self.content_area = ft.Container(
            expand=True,
            bgcolor="#1C1B1F",
            padding=0,
        )
        
    def _create_statusbar(self):
        """상태바 생성"""
        from .components import ModernStatusBar
        self.statusbar = ModernStatusBar(self)
        
    def _load_initial_view(self):
        """초기 뷰 로드"""
        self.switch_view("dashboard")
        
    def switch_view(self, view_name: str):
        """뷰 전환"""
        logger.info(f"Switching to view: {view_name}")
        self.current_view = view_name
        
        # 기존 뷰가 없으면 생성
        if view_name not in self.views:
            self._create_view(view_name)
        
        # 컨텐츠 영역 업데이트
        if self.content_area and view_name in self.views:
            self.content_area.content = self.views[view_name]
            self.page.update()
    
    def _create_view(self, view_name: str):
        """뷰 생성"""
        if view_name == "dashboard":
            from .views import ModernDashboardView
            self.views[view_name] = ModernDashboardView(self)
            
        elif view_name == "processing":
            from .views import ModernProcessingView
            self.views[view_name] = ModernProcessingView(self)
            
        elif view_name == "history":
            from .views import ModernHistoryView
            self.views[view_name] = ModernHistoryView(self)
            
        elif view_name == "folders":
            from .views import ModernFolderView
            self.views[view_name] = ModernFolderView(self)
            
        elif view_name == "settings":
            from .views import ModernSettingsView
            self.views[view_name] = ModernSettingsView(self)
    
    def _on_resize(self, e):
        """창 크기 변경 이벤트"""
        logger.debug(f"Window resized: {self.page.window_width}x{self.page.window_height}")
    
    def show_message(self, title: str, message: str, type: str = "info"):
        """메시지 표시"""
        colors = {
            "info": "#2196F3",
            "success": "#4CAF50",
            "warning": "#FF9800",
            "error": "#F44336"
        }
        
        snack_bar = ft.SnackBar(
            content=ft.Text(f"{title}: {message}"),
            bgcolor=colors.get(type, "#2196F3"),
        )
        self.page.show_snack_bar(snack_bar)
    
    def update_status(self, message: str):
        """상태바 업데이트"""
        if self.statusbar:
            self.statusbar.update_status(message)
# src/ui/views/settings_v2/categories/general_category.py
"""
일반 설정 카테고리

테마, 시작 옵션, UI 설정을 관리
언어 설정은 제거됨 (한국어 전용)
"""

import customtkinter as ctk
from typing import Dict, Any
from ..base_category import BaseCategory


class GeneralCategory(BaseCategory):
    """
    일반 설정 카테고리
    
    - 테마 설정
    - 시작 옵션
    - UI 설정
    """
    
    def _create_ui(self):
        """UI 생성"""
        # 테마 설정 섹션
        self._create_theme_section()
        
        # 시작 옵션 섹션
        self._create_startup_section()
        
        # UI 설정 섹션
        self._create_ui_section()
    
    def _create_theme_section(self):
        """테마 설정 섹션"""
        section = self.create_section("테마 설정", "🎨")
        
        # 테마 선택
        self.create_option_row(
            section,
            "테마:",
            "combobox",
            "theme",
            values=["다크", "라이트", "시스템"]
        )
        
        # 색상 강조 (미래 기능을 위한 placeholder)
        accent_frame = ctk.CTkFrame(section, fg_color="transparent")
        accent_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            accent_frame,
            text="강조 색상:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        # 색상 프리뷰
        color_preview = ctk.CTkFrame(
            accent_frame,
            width=100,
            height=32,
            corner_radius=8,
            fg_color="#1976D2"
        )
        color_preview.pack(side='left')
        
        ctk.CTkLabel(
            accent_frame,
            text="(향후 업데이트 예정)",
            text_color=("gray50", "gray50")
        ).pack(side='left', padx=(10, 0))
    
    def _create_startup_section(self):
        """시작 옵션 섹션"""
        section = self.create_section("시작 옵션", "🚀")
        
        # 자동 폴더 감시
        self.create_option_row(
            section,
            "프로그램 시작 시 폴더 감시 자동 시작:",
            "switch",
            "auto_start_watching"
        )
        
        # 마지막 감시 폴더 복원
        self.create_option_row(
            section,
            "마지막 감시 폴더 자동 복원:",
            "switch",
            "watch_folders_on_startup"
        )
        
        # 트레이로 최소화
        self.create_option_row(
            section,
            "닫기 버튼 클릭 시 트레이로 최소화:",
            "switch",
            "minimize_to_tray"
        )
        
        # 윈도우 위치 기억
        self.create_option_row(
            section,
            "창 위치 및 크기 기억:",
            "switch",
            "remember_window_position"
        )
    
    def _create_ui_section(self):
        """UI 설정 섹션"""
        section = self.create_section("인터페이스", "🖥️")
        
        # 사이드바 너비
        sidebar_frame = ctk.CTkFrame(section, fg_color="transparent")
        sidebar_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            sidebar_frame,
            text="사이드바 너비:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        slider_container = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        slider_container.pack(side='left')
        
        self.sidebar_slider = ctk.CTkSlider(
            slider_container,
            from_=200,
            to=400,
            width=150,
            command=self._on_sidebar_width_change
        )
        self.sidebar_slider.pack(side='left')
        
        self.sidebar_label = ctk.CTkLabel(
            slider_container,
            text="250px",
            width=50
        )
        self.sidebar_label.pack(side='left', padx=(10, 0))
        
        self.widgets['sidebar_width'] = self.sidebar_slider
        
        # 알림 표시
        self.create_option_row(
            section,
            "처리 완료 알림 표시:",
            "switch",
            "show_notifications"
        )
        
        # 알림음
        self.create_option_row(
            section,
            "알림음 재생:",
            "switch",
            "notification_sound"
        )
        
        # 테이블 열 표시 설정
        self._create_column_visibility_settings(section)
    
    def _create_column_visibility_settings(self, parent):
        """테이블 열 표시 설정"""
        # 소제목
        ctk.CTkLabel(
            parent,
            text="테이블 열 표시:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(fill='x', pady=(15, 10))
        
        # 열 옵션들
        columns = [
            ("icon", "아이콘"),
            ("filename", "파일명"),
            ("folder", "폴더"),
            ("pagesize", "페이지 크기"),
            ("pages", "페이지 수"),
            ("issues", "문제점"),
            ("time", "처리 시간"),
            ("report", "보고서")
        ]
        
        # 2열로 배치
        columns_frame = ctk.CTkFrame(parent, fg_color="transparent")
        columns_frame.pack(fill='x')
        
        for i, (col_id, col_name) in enumerate(columns):
            row = i // 2
            col = i % 2
            
            # 행 프레임 생성 (필요시)
            if col == 0:
                row_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
                row_frame.pack(fill='x', pady=2)
            
            # 체크박스
            checkbox = ctk.CTkCheckBox(
                row_frame,
                text=col_name,
                width=150,
                command=lambda cid=col_id: self._on_column_visibility_change(cid)
            )
            checkbox.pack(side='left', padx=(0, 20))
            
            self.widgets[f'column_{col_id}'] = checkbox
    
    def _on_sidebar_width_change(self, value: float):
        """사이드바 너비 변경"""
        width = int(value)
        self.sidebar_label.configure(text=f"{width}px")
        self._on_widget_change("sidebar_width", width)
    
    def _on_column_visibility_change(self, column_id: str):
        """열 표시 설정 변경"""
        checkbox = self.widgets.get(f'column_{column_id}')
        if checkbox:
            # 전체 열 설정을 수집하여 전달
            visibility = {}
            for col_id in ["icon", "filename", "folder", "pagesize", "pages", "issues", "time", "report"]:
                col_widget = self.widgets.get(f'column_{col_id}')
                if col_widget:
                    visibility[col_id] = col_widget.get()
            
            self._on_widget_change("column_visibility", visibility)
    
    def load_settings(self, settings):
        """설정 로드"""
        # 테마
        theme_map = {"dark": "다크", "light": "라이트", "system": "시스템"}
        if hasattr(settings, 'theme'):
            theme = theme_map.get(settings.theme, "다크")
            self.widgets['theme'].set(theme)
        
        # 시작 옵션
        if hasattr(settings, 'auto_start_watching'):
            if settings.auto_start_watching:
                self.widgets['auto_start_watching'].select()
            else:
                self.widgets['auto_start_watching'].deselect()
        
        if hasattr(settings, 'watch_folders_on_startup'):
            if settings.watch_folders_on_startup:
                self.widgets['watch_folders_on_startup'].select()
            else:
                self.widgets['watch_folders_on_startup'].deselect()
        
        if hasattr(settings, 'minimize_to_tray'):
            if settings.minimize_to_tray:
                self.widgets['minimize_to_tray'].select()
            else:
                self.widgets['minimize_to_tray'].deselect()
        
        # 창 위치 기억 (새 옵션, 기본값 True)
        if 'remember_window_position' in self.widgets:
            self.widgets['remember_window_position'].select()
        
        # UI 설정
        if hasattr(settings, 'sidebar_width'):
            self.sidebar_slider.set(settings.sidebar_width)
            self.sidebar_label.configure(text=f"{settings.sidebar_width}px")
        
        if hasattr(settings, 'show_notifications'):
            if settings.show_notifications:
                self.widgets['show_notifications'].select()
            else:
                self.widgets['show_notifications'].deselect()
        
        if hasattr(settings, 'notification_sound'):
            if settings.notification_sound:
                self.widgets['notification_sound'].select()
            else:
                self.widgets['notification_sound'].deselect()
        
        # 열 표시 설정
        if hasattr(settings, 'column_visibility'):
            for col_id, visible in settings.column_visibility.items():
                widget = self.widgets.get(f'column_{col_id}')
                if widget:
                    if visible:
                        widget.select()
                    else:
                        widget.deselect()
    
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정 값 반환"""
        settings = {}
        
        # 테마
        theme_map = {"다크": "dark", "라이트": "light", "시스템": "system"}
        settings['theme'] = theme_map.get(self.widgets['theme'].get(), "dark")
        
        # 시작 옵션
        settings['auto_start_watching'] = self.widgets['auto_start_watching'].get()
        settings['watch_folders_on_startup'] = self.widgets['watch_folders_on_startup'].get()
        settings['minimize_to_tray'] = self.widgets['minimize_to_tray'].get()
        
        if 'remember_window_position' in self.widgets:
            settings['remember_window_position'] = self.widgets['remember_window_position'].get()
        
        # UI 설정
        settings['sidebar_width'] = int(self.sidebar_slider.get())
        settings['show_notifications'] = self.widgets['show_notifications'].get()
        settings['notification_sound'] = self.widgets['notification_sound'].get()
        
        # 열 표시 설정
        visibility = {}
        for col_id in ["icon", "filename", "folder", "pagesize", "pages", "issues", "time", "report"]:
            widget = self.widgets.get(f'column_{col_id}')
            if widget:
                visibility[col_id] = widget.get()
        settings['column_visibility'] = visibility
        
        return settings
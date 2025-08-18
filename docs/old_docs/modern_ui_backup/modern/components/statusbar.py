# src/ui/modern/components/statusbar.py
"""
Modern 상태바 컴포넌트
"""

import flet as ft
from typing import TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernStatusBar(ft.Container):
    """Modern 상태바"""
    
    def __init__(self, app: 'ModernApp'):
        self.app = app
        
        # 상태 메시지
        self.status_text = ft.Text(
            "준비됨",
            size=12,
            color="#888888"
        )
        
        # 진행 상황
        self.progress_bar = ft.ProgressBar(
            width=200,
            height=4,
            visible=False,
        )
        
        # 통계 정보
        self.stats_text = ft.Text(
            "파일: 0 | 성공: 0 | 실패: 0",
            size=12,
            color="#888888"
        )
        
        # 시간
        self.time_text = ft.Text(
            datetime.now().strftime("%H:%M:%S"),
            size=12,
            color="#888888"
        )
        
        super().__init__(
            height=30,
            bgcolor="#2B2930",
            padding=ft.padding.symmetric(horizontal=20, vertical=5),
            content=ft.Row([
                self.status_text,
                ft.Container(expand=True),
                self.progress_bar,
                ft.Container(expand=True),
                self.stats_text,
                ft.Container(width=20),
                self.time_text,
            ])
        )
        
    def update_status(self, message: str):
        """상태 메시지 업데이트"""
        self.status_text.value = message
        self.update()
    
    def show_progress(self, value: float = None):
        """진행 상황 표시"""
        self.progress_bar.visible = True
        if value is not None:
            self.progress_bar.value = value
        self.update()
    
    def hide_progress(self):
        """진행 상황 숨기기"""
        self.progress_bar.visible = False
        self.update()
    
    def update_stats(self, total: int, success: int, failed: int):
        """통계 업데이트"""
        self.stats_text.value = f"파일: {total} | 성공: {success} | 실패: {failed}"
        self.update()
    
    def update_time(self):
        """시간 업데이트"""
        self.time_text.value = datetime.now().strftime("%H:%M:%S")
        self.update()
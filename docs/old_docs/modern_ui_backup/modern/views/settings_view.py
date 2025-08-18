# src/ui/modern/views/settings_view.py
"""
Modern 설정 뷰
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernSettingsView(ft.Container):
    """Modern 설정 뷰"""
    
    def __init__(self, app: 'ModernApp'):
        self.app = app
        
        super().__init__(
            expand=True,
            padding=30,
            content=self._build_content()
        )
    
    def _build_content(self):
        """컨텐츠 생성"""
        header = ft.Container(
            content=ft.Text("설정", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            padding=ft.padding.only(bottom=20),
        )
        
        # 설정 항목들
        settings_list = ft.Column([
            ft.ListTile(
                leading=ft.Icon(name="dark_mode"),
                title=ft.Text("다크 모드"),
                subtitle=ft.Text("어두운 테마 사용"),
                trailing=ft.Switch(value=True),
            ),
            ft.ListTile(
                leading=ft.Icon(name="notifications"),
                title=ft.Text("알림"),
                subtitle=ft.Text("처리 완료 시 알림 받기"),
                trailing=ft.Switch(value=True),
            ),
            ft.ListTile(
                leading=ft.Icon(name="image"),
                title=ft.Text("이미지 품질"),
                subtitle=ft.Text("최소 DPI: 300"),
                trailing=ft.Slider(
                    min=150, max=600, value=300,
                ),
            ),
            ft.Divider(),
            ft.ListTile(
                leading=ft.Icon(name="swap_horiz"),
                title=ft.Text("UI 모드 변경"),
                subtitle=ft.Text("Classic UI로 전환"),
                trailing=ft.ElevatedButton(
                    "Classic으로 전환",
                    on_click=self._switch_to_classic,
                ),
            ),
        ])
        
        return ft.Column([
            header,
            settings_list,
        ])
    
    def _switch_to_classic(self, e):
        """Classic UI로 전환"""
        from src.config.ui_config import get_ui_config_manager
        ui_config = get_ui_config_manager()
        ui_config.set_ui_mode("classic")
        self.app.show_message("UI 모드 변경", "다음 실행 시 Classic UI로 시작됩니다.", "info")
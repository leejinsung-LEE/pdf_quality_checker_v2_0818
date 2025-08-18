# src/ui/modern/views/folder_view.py
"""
Modern 폴더 관리 뷰
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernFolderView(ft.Container):
    """Modern 폴더 관리 뷰"""
    
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
            content=ft.Text("폴더 관리", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            padding=ft.padding.only(bottom=20),
        )
        
        # 플레이스홀더
        placeholder = ft.Container(
            content=ft.Column([
                ft.Icon(name="folder_special", size=64, color="#444444"),
                ft.Text("폴더 감시 설정이 여기에 표시됩니다", size=16, color="#888888"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            expand=True,
            alignment=ft.alignment.center,
        )
        
        return ft.Column([
            header,
            placeholder,
        ])
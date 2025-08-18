# src/ui/modern/views/processing_view.py
"""
Modern 파일 처리 뷰
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernProcessingView(ft.Container):
    """Modern 파일 처리 뷰"""
    
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
            content=ft.Text("파일 처리", size=28, weight=ft.FontWeight.BOLD, color="#FFFFFF"),
            padding=ft.padding.only(bottom=20),
        )
        
        # 드래그 앤 드롭 영역
        drop_area = ft.Container(
            content=ft.Column([
                ft.Icon(name="cloud_upload", color="#2196F3", size=64),
                ft.Container(height=20),
                ft.Text("PDF 파일을 여기에 드래그하세요", size=18, color="#FFFFFF"),
                ft.Container(height=10),
                ft.Text("또는", size=14, color="#888888"),
                ft.Container(height=10),
                ft.ElevatedButton(
                    "파일 선택",
                    icon="folder_open",
                    bgcolor="#6750A4",
                    color="#FFFFFF",
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.border.all(2, "#2196F3"),
            border_radius=16,
            padding=60,
            bgcolor="#1E88E510",
            alignment=ft.alignment.center,
            height=300,
        )
        
        return ft.Column([
            header,
            drop_area,
        ])
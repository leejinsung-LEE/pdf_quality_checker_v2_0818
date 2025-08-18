# src/ui/modern/components/menubar.py
"""
Modern 메뉴바 컴포넌트 (플레이스홀더)
"""

import flet as ft
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import ModernApp


class ModernMenuBar(ft.Container):
    """Modern 메뉴바"""
    
    def __init__(self, app: 'ModernApp'):
        self.app = app
        
        super().__init__(
            height=40,
            bgcolor="#2B2930",
            content=ft.Text("메뉴바 (준비 중)", color="#888888")
        )
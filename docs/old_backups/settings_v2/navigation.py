# src/ui/views/settings_v2/navigation.py
"""
사이드바 네비게이션 컴포넌트

설정 카테고리를 선택할 수 있는 사이드바 네비게이션
"""

import customtkinter as ctk
from typing import List, Callable, Optional


class NavigationSidebar(ctk.CTkFrame):
    """
    사이드바 네비게이션
    
    카테고리 목록을 표시하고 선택할 수 있는 사이드바
    """
    
    def __init__(self, parent, categories: List, on_category_select: Callable, **kwargs):
        super().__init__(parent, width=200, **kwargs)
        
        self.categories = categories
        self.on_category_select = on_category_select
        self.current_category = categories[0].id if categories else None
        
        # 버튼 저장
        self.buttons = {}
        
        # UI 생성
        self._create_ui()
        
        # 첫 번째 카테고리 선택
        if self.current_category:
            self.select_category(self.current_category)
    
    def _create_ui(self):
        """UI 생성"""
        # 제목
        title_label = ctk.CTkLabel(
            self,
            text="설정 카테고리",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.pack(pady=(10, 20))
        
        # 카테고리 버튼들
        for category in self.categories:
            btn = self._create_category_button(category)
            btn.pack(fill='x', pady=2)
            self.buttons[category.id] = btn
    
    def _create_category_button(self, category) -> ctk.CTkButton:
        """카테고리 버튼 생성"""
        btn = ctk.CTkButton(
            self,
            text=f"{category.icon} {category.name}",
            anchor='w',
            height=40,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray10", "gray90"),
            command=lambda: self._on_button_click(category.id)
        )
        return btn
    
    def _on_button_click(self, category_id: str):
        """버튼 클릭 이벤트"""
        if category_id == self.current_category:
            return
        
        self.select_category(category_id)
        
        # 콜백 호출
        if self.on_category_select:
            self.on_category_select(category_id)
    
    def select_category(self, category_id: str):
        """카테고리 선택"""
        # 이전 선택 해제
        if self.current_category and self.current_category in self.buttons:
            self.buttons[self.current_category].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
        
        # 새 선택
        if category_id in self.buttons:
            self.buttons[category_id].configure(
                fg_color=("gray80", "gray30"),
                text_color=("gray10", "white")
            )
            self.current_category = category_id
    
    def get_current_category(self) -> Optional[str]:
        """현재 선택된 카테고리 반환"""
        return self.current_category
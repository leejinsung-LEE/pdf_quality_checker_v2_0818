# src/ui/views/settings_v2/search_bar.py
"""
설정 검색 바 컴포넌트

설정을 빠르게 찾을 수 있는 검색 기능
"""

import customtkinter as ctk
from typing import Callable, Optional


class SettingsSearchBar(ctk.CTkFrame):
    """
    설정 검색 바
    
    설정 항목을 검색할 수 있는 검색 입력 필드
    """
    
    def __init__(self, parent, on_search: Callable, placeholder: str = "검색...", **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.on_search = on_search
        self.placeholder = placeholder
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 생성"""
        # 검색 아이콘
        search_icon = ctk.CTkLabel(
            self,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        search_icon.pack(side='left', padx=(0, 5))
        
        # 검색 입력 필드
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text=self.placeholder,
            width=200,
            height=32,
            corner_radius=8
        )
        self.search_entry.pack(side='left')
        
        # 클리어 버튼
        self.clear_btn = ctk.CTkButton(
            self,
            text="✕",
            width=24,
            height=24,
            corner_radius=12,
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            command=self._clear_search
        )
        # 초기에는 숨김
        
        # 이벤트 바인딩
        self.search_entry.bind('<KeyRelease>', self._on_key_release)
        self.search_entry.bind('<Return>', self._on_enter)
    
    def _on_key_release(self, event):
        """키 입력 이벤트"""
        query = self.search_entry.get().strip()
        
        # 클리어 버튼 표시/숨김
        if query:
            self.clear_btn.pack(side='left', padx=(5, 0))
        else:
            self.clear_btn.pack_forget()
        
        # 검색 실행
        if self.on_search:
            self.on_search(query)
    
    def _on_enter(self, event):
        """엔터 키 이벤트"""
        query = self.search_entry.get().strip()
        if self.on_search:
            self.on_search(query)
    
    def _clear_search(self):
        """검색 내용 지우기"""
        self.search_entry.delete(0, 'end')
        self.clear_btn.pack_forget()
        
        # 빈 검색으로 콜백 호출
        if self.on_search:
            self.on_search("")
    
    def get_query(self) -> str:
        """현재 검색어 반환"""
        return self.search_entry.get().strip()
    
    def set_query(self, query: str):
        """검색어 설정"""
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, query)
        
        # 클리어 버튼 표시
        if query:
            self.clear_btn.pack(side='left', padx=(5, 0))
    
    def focus(self):
        """검색 필드에 포커스 설정"""
        self.search_entry.focus_set()
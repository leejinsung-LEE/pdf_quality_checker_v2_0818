# src/ui/components/sidebar/base.py
"""
사이드바 기본 클래스

Sidebar 컴포넌트의 핵심 구조와 기본 설정을 정의합니다.
"""

import customtkinter as ctk
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

from ...controllers import ProfileController, get_profile_controller


class SidebarBase(ctk.CTkFrame):
    """사이드바 기본 클래스"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_card': '#2a2a2a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#667eea',
            'success': '#28a745',
            'border': '#404040'
        }
        
        # 콜백
        self.on_view_change: Optional[Callable[[str], None]] = None
        self.on_files_dropped: Optional[Callable[[List[Path]], None]] = None
        self.on_profile_change: Optional[Callable[[str], None]] = None
        self.on_folder_select: Optional[Callable[[Path], None]] = None
        
        # 프로파일 컨트롤러
        self.profile_controller = get_profile_controller()
        
        # 현재 뷰
        self.current_view = "processing"
        
        # 폴더 목록 (폴더 감시용)
        self.folders = []
        
        # UI 위젯 참조 저장용 딕셔너리
        self.widgets = {}
    
    def _initialize(self):
        """초기화 (하위 클래스에서 호출)"""
        # 기본 UI 설정
        self.configure(fg_color=self.colors['bg_secondary'], width=260)
        
        # 스크롤 가능한 컨테이너
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scrollable_frame.pack(fill='both', expand=True, padx=0, pady=0)
    
    def set_callbacks(self,
                     on_view_change: Optional[Callable] = None,
                     on_files_dropped: Optional[Callable] = None,
                     on_profile_change: Optional[Callable] = None,
                     on_folder_select: Optional[Callable] = None):
        """콜백 설정"""
        if on_view_change:
            self.on_view_change = on_view_change
        if on_files_dropped:
            self.on_files_dropped = on_files_dropped
        if on_profile_change:
            self.on_profile_change = on_profile_change
        if on_folder_select:
            self.on_folder_select = on_folder_select
    
    def add_watch_folder(self, path: Path):
        """감시 폴더 추가"""
        folder_info = {
            'path': path,
            'name': path.name,
            'active': True,
            'file_count': 0,
            'last_processed': None
        }
        self.folders.append(folder_info)
    
    def remove_watch_folder(self, path: Path):
        """감시 폴더 제거"""
        self.folders = [f for f in self.folders if f['path'] != path]
    
    def update_folder_status(self, path: Path, active: bool):
        """폴더 활성화 상태 업데이트"""
        for folder in self.folders:
            if folder['path'] == path:
                folder['active'] = active
                break
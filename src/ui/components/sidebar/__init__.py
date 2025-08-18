# src/ui/components/sidebar/__init__.py
"""
사이드바 컴포넌트 모듈

모듈화된 사이드바 컴포넌트를 통합하고 외부에 Sidebar를 제공합니다.
기존 API 호환성을 유지하면서 내부 구조를 모듈화했습니다.

모듈 구조:
- base.py: 기본 클래스와 초기화 (SidebarBase)
- ui_builder.py: UI 구성 요소 생성 (UIBuilder)
- drag_drop.py: 드래그앤드롭 처리 (DragDropHandler)
- profile_selector.py: 프로파일 선택 관리 (ProfileSelector)
- folder_manager.py: 폴더 감시 관리 (FolderManager)
"""

import customtkinter as ctk
import tkinterdnd2 as tkdnd
from typing import List, Optional, Callable, Dict, Any
from pathlib import Path

from .base import SidebarBase
from .ui_builder import UIBuilder
from .drag_drop import DragDropHandler
from .profile_selector import ProfileSelector
from .folder_manager import FolderManager


class Sidebar(SidebarBase):
    """
    사이드바 컴포넌트 - 모듈화된 버전
    
    기존 API와 호환성을 유지하면서 내부를 모듈화한 사이드바입니다.
    각 기능별로 모듈이 분리되어 있어 유지보수가 용이합니다.
    """
    
    def __init__(self, parent, **kwargs):
        # 기본 클래스 초기화
        super().__init__(parent, **kwargs)
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder()
        self.drag_drop_handler = DragDropHandler(self)
        self.profile_selector = ProfileSelector(self)
        self.folder_manager = FolderManager(self)
        
        # 기본 초기화
        self._initialize()
        
        # UI 생성
        self._create_ui()
    
    def _create_ui(self):
        """UI 구성"""
        # 헤더
        header = self.ui_builder.create_header_section(self.scrollable_frame, self.colors)
        
        # 구분선
        self.ui_builder.create_separator(self.scrollable_frame, self.colors)
        
        # 폴더 감시 섹션
        folder_widgets = self.ui_builder.create_folder_watch_section(
            self.scrollable_frame, self.colors, self
        )
        self.widgets.update({
            'folder_section': folder_widgets['section'],
            'watch_toggle': folder_widgets['toggle_switch'],
            'folder_frame': folder_widgets['folder_frame'],
            'add_folder_button': folder_widgets['add_button']
        })
        
        # 구분선
        self.ui_builder.create_separator(self.scrollable_frame, self.colors)
        
        # 드래그앤드롭 영역
        drop_widgets = self.ui_builder.create_drop_zone(
            self.scrollable_frame, self.colors, self
        )
        self.widgets.update({
            'drop_section': drop_widgets['section'],
            'drop_zone': drop_widgets['drop_zone'],
            'drop_icon': drop_widgets['drop_icon'],
            'drop_text': drop_widgets['drop_text'],
            'file_button': drop_widgets['file_button']
        })
        
        # 드래그앤드롭 설정
        self.drag_drop_handler.setup_drag_drop(drop_widgets['drop_zone'])
        
        # 프로파일 선택
        profile_widgets = self.ui_builder.create_profile_selector(
            self.scrollable_frame, self.colors, self
        )
        self.widgets.update({
            'profile_section': profile_widgets['section'],
            'profile_title': profile_widgets['title_label'],
            'profile_dropdown': profile_widgets['profile_dropdown']
        })
        
        # 빠른 통계
        stats_widgets = self.ui_builder.create_quick_stats_section(
            self.scrollable_frame, self.colors
        )
        self.widgets.update({
            'stats_section': stats_widgets['section'],
            'stats_card': stats_widgets['stats_card']
        })
        self.widgets.update(stats_widgets['widgets'])
        
        # 하단 정보
        footer = self.ui_builder.create_footer_section(self.scrollable_frame, self.colors)
        self.widgets['footer'] = footer
        
        # 초기 폴더 목록 업데이트
        self.folder_manager._update_folder_list()
    
    # === 네비게이션 관련 메서드들 ===
    
    def _on_nav_click(self, view_id: str):
        """네비게이션 클릭 이벤트"""
        self.current_view = view_id
        self._update_nav_selection()
        
        if self.on_view_change:
            self.on_view_change(view_id)
    
    def _on_tab_select(self, tab_index: int):
        """탭 선택 이벤트"""
        view_mapping = {
            0: "processing",
            1: "dashboard", 
            2: "history",
            3: "settings"
        }
        
        if tab_index in view_mapping:
            self._on_nav_click(view_mapping[tab_index])
    
    def _update_nav_selection(self):
        """네비게이션 선택 상태 업데이트"""
        # 필요시 네비게이션 버튼 스타일 업데이트
        pass
    
    # === 파일 처리 관련 메서드들 (DragDropHandler에서 위임) ===
    
    def _on_file_select(self):
        """파일 선택 이벤트"""
        self.drag_drop_handler.handle_file_select()
    
    def _on_drop(self, event):
        """드롭 이벤트"""
        self.drag_drop_handler._on_drop(event)
    
    def _on_drag_enter(self, event):
        """드래그 진입 이벤트"""
        self.drag_drop_handler._on_drag_enter(event)
    
    def _on_drag_leave(self, event):
        """드래그 벗어남 이벤트"""
        self.drag_drop_handler._on_drag_leave(event)
    
    def _parse_drop_data(self, data: str) -> List[Path]:
        """드롭 데이터 파싱"""
        return self.drag_drop_handler._parse_drop_data(data)
    
    # === 프로파일 관련 메서드들 (ProfileSelector에서 위임) ===
    
    def _on_profile_select(self, profile_name: str):
        """프로파일 선택 이벤트"""
        self.profile_selector._on_profile_select(profile_name)
    
    def update_profile_dropdown(self):
        """프로파일 드롭다운 업데이트"""
        self.profile_selector.update_profile_dropdown()
    
    def set_profile(self, profile_name: str) -> bool:
        """프로파일 설정"""
        return self.profile_selector.set_profile(profile_name)
    
    def get_current_profile(self) -> str:
        """현재 프로파일 조회"""
        return self.profile_selector.get_current_profile()
    
    # === 폴더 관리 관련 메서드들 (FolderManager에서 위임) ===
    
    def _on_watch_toggle(self):
        """폴더 감시 토글"""
        self.folder_manager._on_watch_toggle()
    
    def _on_add_folder(self):
        """폴더 추가"""
        self.folder_manager._on_add_folder()
    
    def _update_folder_list(self):
        """폴더 목록 업데이트"""
        self.folder_manager._update_folder_list()
    
    def _create_folder_item(self, folder_info: Dict[str, Any]):
        """폴더 아이템 생성"""
        folder_frame = self.widgets.get('folder_frame')
        if folder_frame:
            self.folder_manager._create_folder_item(folder_frame, folder_info)
    
    def add_watch_folder(self, path: Path):
        """감시 폴더 추가"""
        super().add_watch_folder(path)
        self.folder_manager._update_folder_list()
    
    def remove_watch_folder(self, path: Path):
        """감시 폴더 제거"""
        super().remove_watch_folder(path)
        self.folder_manager._update_folder_list()
    
    def update_folder_status(self, path: Path, active: bool):
        """폴더 상태 업데이트"""
        super().update_folder_status(path, active)
        self.folder_manager._update_folder_list()
    
    # === 통계 업데이트 메서드들 ===
    
    def update_stats(self, stats: Dict[str, Any]):
        """통계 정보 업데이트"""
        stats_mapping = {
            'processed_count': stats.get('completed', 0),
            'error_count': stats.get('error', 0),
            'fixed_count': stats.get('fixed', 0),
            'processing_time': f"{stats.get('avg_time', 0):.1f}분"
        }
        
        for key, value in stats_mapping.items():
            label_widget = self.widgets.get(f'{key}_label')
            if label_widget:
                label_widget.configure(text=str(value))
    
    def update_quick_stats(self, 
                          processed: int = 0, 
                          errors: int = 0, 
                          fixed: int = 0, 
                          avg_time: float = 0.0):
        """빠른 통계 업데이트"""
        self.update_stats({
            'completed': processed,
            'error': errors,
            'fixed': fixed,
            'avg_time': avg_time
        })
    
    def update_watch_status(self, watch_count: int):
        """폴더 감시 상태 업데이트
        
        Args:
            watch_count: 현재 감시 중인 폴더 수
        """
        # 폴더 매니저가 있으면 폴더 목록 업데이트
        if hasattr(self, 'folder_manager'):
            self.folder_manager._update_folder_list()
        
        # 감시 중인 폴더 수 정보 업데이트 (필요시 UI에 표시)
        # 현재는 폴더 목록만 업데이트하고 추가 UI 업데이트는 필요시 구현
        pass
    
    # === 기존 호환성을 위한 메서드들 ===
    
    def _create_header(self):
        """헤더 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_separator(self):
        """구분선 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_folder_watch_section(self):
        """폴더 감시 섹션 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_quick_stats(self):
        """통계 섹션 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_drop_zone(self):
        """드롭 존 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_profile_selector(self):
        """프로파일 선택 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass
    
    def _create_footer(self):
        """푸터 생성 (기존 호환성)"""
        # 이미 _create_ui에서 처리됨
        pass


# 외부 사용을 위한 export
__all__ = ['Sidebar']
"""
폴더 관리 베이스 클래스
"""

import customtkinter as ctk
from typing import Optional

from ....processing.folder_watcher import FolderWatcher

from .ui_builder import UIBuilder
from .folder_list import FolderListManager
from .settings_manager import SettingsManager
from .handlers import EventHandler


class FolderManagerView(ctk.CTkToplevel):
    """폴더 관리 창"""
    
    def __init__(self, parent, folder_watcher: Optional[FolderWatcher] = None):
        """
        폴더 관리 창 초기화
        
        Args:
            parent: 부모 윈도우
            folder_watcher: 폴더 감시기 인스턴스
        """
        super().__init__(parent)
        
        self.folder_watcher = folder_watcher or FolderWatcher()
        self.selected_folder = None
        
        # 창 설정
        self.title("폴더 관리")
        self.geometry("900x600")
        self.resizable(True, True)
        
        # UI 위젯 딕셔너리
        self.widgets = {}
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.folder_list_manager = FolderListManager(self)
        self.settings_manager = SettingsManager(self)
        self.event_handler = EventHandler(self)
        
        # UI 생성
        self._create_ui()
        
        # 폴더 목록 로드
        self.folder_list_manager.load_folders()
        
        # 창 포커스
        self.focus()
        self.grab_set()
    
    def _create_ui(self):
        """UI 생성"""
        self.ui_builder.create_ui()
    
    def on_folder_select(self, folder_path: str):
        """폴더 선택 이벤트"""
        self.selected_folder = folder_path
        self.settings_manager.load_folder_settings(folder_path)
    
    def add_folder(self):
        """폴더 추가"""
        folder_path = self.event_handler.browse_folder()
        if folder_path:
            self.folder_list_manager.add_folder(folder_path)
    
    def remove_folder(self):
        """폴더 제거"""
        if self.selected_folder:
            self.folder_list_manager.remove_folder(self.selected_folder)
            self.selected_folder = None
            self.settings_manager.clear_settings()
    
    def save_settings(self):
        """설정 저장"""
        if self.selected_folder:
            settings = self.settings_manager.get_current_settings()
            self.event_handler.save_settings(self.selected_folder, settings)
    
    def browse_output_folder(self):
        """출력 폴더 선택"""
        folder_path = self.event_handler.browse_folder()
        if folder_path and 'output_folder' in self.widgets:
            self.widgets['output_folder'].set(folder_path)
    
    def toggle_report_formats(self):
        """리포트 형식 토글"""
        self.settings_manager.toggle_report_formats()
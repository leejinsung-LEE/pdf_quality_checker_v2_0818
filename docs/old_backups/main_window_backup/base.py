"""
메인 윈도우 베이스 클래스
"""

import customtkinter as ctk
import tkinterdnd2
from typing import Dict, List, Optional
from pathlib import Path
import json

from ...controllers import (
    get_file_controller, get_settings_controller, get_profile_controller
)
from ....processing import FolderWatcher

from .ui_builder import UIBuilder
from .view_manager import ViewManager
from .event_handler import EventHandler
from .file_manager import FileManager
from .folder_watcher_manager import FolderWatcherManager
from .dialog_manager import DialogManager


class MainWindow(tkinterdnd2.Tk):
    """
    메인 윈도우
    
    애플리케이션의 메인 윈도우로 모든 UI 컴포넌트를 통합합니다.
    """
    
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("PDF Quality Checker v2.0")
        self.geometry("1400x800")
        self.minsize(1200, 600)
        
        # 아이콘 설정 (있는 경우)
        try:
            self.iconbitmap("resources/icon.ico")
        except Exception:
            # 아이콘 파일이 없거나 설정 실패는 무시
            pass
        
        # CustomTkinter 설정
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 컨트롤러 초기화
        self.file_controller = get_file_controller()
        self.settings_controller = get_settings_controller()
        self.profile_controller = get_profile_controller()
        
        # 폴더 감시자
        self.folder_watchers: Dict[str, FolderWatcher] = {}
        
        # 현재 뷰
        self.current_view = "unified_processing"
        self.views: Dict[str, ctk.CTkFrame] = {}
        
        # 최근 파일
        self.recent_files: List[str] = []
        
        # UI 요소 딕셔너리 (호환성을 위해)
        self.widgets = {}
        
        # 헬퍼 클래스 초기화
        self.ui_builder = UIBuilder(self)
        self.view_manager = ViewManager(self)
        self.event_handler = EventHandler(self)
        self.file_manager = FileManager(self)
        self.folder_watcher_manager = FolderWatcherManager(self)
        self.dialog_manager = DialogManager(self)
        
        # 초기화
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        # 최근 파일 로드
        self.file_manager.load_recent_files()
        
        # UI 생성
        self.ui_builder.create_ui()
        
        # 이벤트 설정
        self.event_handler.setup_callbacks()
        
        # 초기 설정 적용
        self._apply_initial_settings()
        
        # 윈도우 이벤트
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 단축키 바인딩
        self.event_handler.bind_shortcuts()
    
    def _apply_initial_settings(self):
        """초기 설정 적용"""
        settings = self.settings_controller.get_settings()
        
        # 윈도우 크기/위치
        if settings.window_geometry:
            self.geometry(settings.window_geometry)
        
        # 사이드바 너비
        if hasattr(self, 'sidebar'):
            self.sidebar.configure(width=settings.sidebar_width)
        
        # 현재 프로파일
        current_profile = self.profile_controller.get_current_profile()[0]
        if hasattr(self, 'statusbar'):
            self.statusbar.set_current_profile(current_profile)
        
        # 폴더 감시 자동 시작
        if settings.auto_start_watching:
            self.folder_watcher_manager.start_all_watchers()
    
    def on_closing(self):
        """종료 처리"""
        # 설정 저장
        self._save_settings()
        
        # 폴더 감시 중지
        self.folder_watcher_manager.stop_all_watchers()
        
        # 창 닫기
        self.destroy()
    
    def _save_settings(self):
        """설정 저장"""
        settings = self.settings_controller.get_settings()
        
        # 윈도우 설정
        settings.window_geometry = self.geometry()
        if hasattr(self, 'sidebar'):
            settings.sidebar_width = self.sidebar.winfo_width()
        
        # 설정 저장
        self.settings_controller.save_settings()
        
        # 최근 파일 저장
        self.file_manager.save_recent_files()
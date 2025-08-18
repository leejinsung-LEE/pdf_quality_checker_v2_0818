"""
이벤트 핸들러 - 이벤트 처리 및 콜백 관리
"""

from typing import TYPE_CHECKING
from pathlib import Path

from ...controllers import FileStatus

if TYPE_CHECKING:
    from .base import MainWindow


class EventHandler:
    """이벤트 핸들러"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def setup_callbacks(self):
        """콜백 설정"""
        self._setup_menu_callbacks()
        self._setup_sidebar_callbacks()
        self._setup_controller_callbacks()
    
    def _setup_menu_callbacks(self):
        """메뉴 콜백 설정"""
        if hasattr(self.window, 'menubar'):
            # 파일 메뉴
            self.window.menubar.set_callback('open_files', self.window.file_manager.open_files)
            self.window.menubar.set_callback('open_folder', self.window.file_manager.open_folder)
            self.window.menubar.set_callback('recent_files', self.window.file_manager.open_recent_files)
            self.window.menubar.set_callback('exit', self.window.on_closing)
            
            # 편집 메뉴
            self.window.menubar.set_callback('preferences', self.window.dialog_manager.show_preferences)
            self.window.menubar.set_callback('profiles', self.window.dialog_manager.show_profile_manager)
            
            # 보기 메뉴
            self.window.menubar.set_callback('view_processing', lambda: self.window.notebook.select(0))
            self.window.menubar.set_callback('view_dashboard', lambda: self.window.notebook.select(1))
            self.window.menubar.set_callback('view_statistics', lambda: self.window.notebook.select(2))
            self.window.menubar.set_callback('view_profile_settings', lambda: self.window.notebook.select(3))
            self.window.menubar.set_callback('toggle_sidebar', self.window.view_manager.toggle_sidebar)
            self.window.menubar.set_callback('toggle_statusbar', self.window.view_manager.toggle_statusbar)
            
            # 도구 메뉴
            self.window.menubar.set_callback('batch_process', self.window.dialog_manager.show_batch_dialog)
            self.window.menubar.set_callback('folder_watch', self.window.dialog_manager.show_folder_watch_dialog)
            self.window.menubar.set_callback('batch_scheduler', self.window.dialog_manager.show_batch_scheduler_dialog)
            self.window.menubar.set_callback('backup_manager', self.window.dialog_manager.show_backup_manager_dialog)
            self.window.menubar.set_callback('export_report', self.window.dialog_manager.export_current_report)
    
    def _setup_sidebar_callbacks(self):
        """사이드바 콜백 설정"""
        if hasattr(self.window, 'sidebar'):
            self.window.sidebar.set_callbacks(
                on_view_change=self.window.view_manager.switch_tab,
                on_files_dropped=self.window.file_manager.process_files,
                on_profile_change=self.on_profile_change,
                on_folder_select=self.window.folder_watcher_manager.add_watch_folder
            )
    
    def _setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        # 파일 컨트롤러 콜백
        self.window.file_controller.set_ui_callbacks(
            on_file_status_changed=self.on_file_status_changed,
            on_file_progress=self.on_file_progress,
            on_file_completed=self.on_file_completed,
            on_file_error=self.on_file_error
        )
        
        # 프로파일 컨트롤러 콜백
        self.window.profile_controller.on_current_profile_changed = self.on_profile_change
    
    def bind_shortcuts(self):
        """단축키 바인딩"""
        # 파일 작업
        self.window.bind('<Control-o>', lambda e: self.window.file_manager.open_files())
        self.window.bind('<Control-Shift-O>', lambda e: self.window.file_manager.open_folder())
        self.window.bind('<Control-q>', lambda e: self.window.on_closing())
        
        # 설정
        self.window.bind('<Control-comma>', lambda e: self.window.dialog_manager.show_preferences())
        
        # 도구
        self.window.bind('<Control-b>', lambda e: self.window.dialog_manager.show_batch_dialog())
        
        # 뷰 전환
        self.window.bind('<F1>', lambda e: self.window.notebook.select(0))
        self.window.bind('<F2>', lambda e: self.window.notebook.select(1))
        self.window.bind('<F3>', lambda e: self.window.notebook.select(2))
        self.window.bind('<F4>', lambda e: self.window.notebook.select(3))
    
    # 이벤트 처리 메서드
    
    def on_file_status_changed(self, file_id: str, status):
        """파일 상태 변경 이벤트"""
        # 통합 처리 뷰 업데이트
        if 'unified_processing' in self.window.views:
            self.window.views['unified_processing'].update_file_status(file_id, status)
    
    def on_file_progress(self, file_id: str, progress: int, message: str):
        """파일 처리 진행률 이벤트"""
        # 통합 처리 뷰 업데이트
        if 'unified_processing' in self.window.views:
            self.window.views['unified_processing'].update_progress(file_id, progress, message)
    
    def on_file_completed(self, file_id: str, file_item):
        """파일 처리 완료 이벤트"""
        # 통합 처리 뷰 업데이트
        if 'unified_processing' in self.window.views:
            self.window.views['unified_processing'].update_file_status(file_id, FileStatus.COMPLETED)
        
        # 대시보드 업데이트
        if 'dashboard' in self.window.views:
            self.window.views['dashboard'].update_statistics()
        
        # 통계 대시보드 업데이트
        if 'statistics' in self.window.views:
            self.window.views['statistics'].add_processed_file(file_item)
        
        # 최근 파일 추가
        self.window.file_manager.add_recent_file(str(file_item.path))
    
    def on_file_error(self, file_id: str, error: str):
        """파일 처리 에러 이벤트"""
        if 'unified_processing' in self.window.views:
            self.window.views['unified_processing'].show_error(file_id, error)
    
    def on_profile_change(self, profile_name: str):
        """프로파일 변경 이벤트"""
        # 상태바 업데이트
        if hasattr(self.window, 'statusbar'):
            self.window.statusbar.set_current_profile(profile_name)
        
        # 사이드바 업데이트
        if hasattr(self.window, 'sidebar'):
            self.window.sidebar.update_profile_display(profile_name)
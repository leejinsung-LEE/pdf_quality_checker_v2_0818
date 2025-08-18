"""
폴더 감시 매니저 - 폴더 감시 관리
"""

from tkinter import messagebox
from typing import TYPE_CHECKING, Dict
from pathlib import Path

from ....processing import FolderWatcher, FolderConfig

if TYPE_CHECKING:
    from .base import MainWindow


class FolderWatcherManager:
    """폴더 감시 매니저"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
        self.watchers: Dict[str, FolderWatcher] = {}
    
    def add_watch_folder(self, folder_path: Path):
        """감시 폴더 추가"""
        folder_str = str(folder_path)
        
        # 이미 감시 중인지 확인
        if folder_str in self.window.folder_watchers:
            messagebox.showinfo("정보", f"이미 감시 중인 폴더입니다:\n{folder_str}")
            return
        
        # 폴더 설정
        folder_config = FolderConfig(
            path=folder_path,
            auto_process=True,
            profile_name=self.window.profile_controller.get_current_profile()[0]
        )
        
        # 감시자 생성
        watcher = FolderWatcher(
            folder_config=folder_config,
            on_pdf_found=self.on_watched_file_found
        )
        
        # 감시 시작
        watcher.start()
        self.window.folder_watchers[folder_str] = watcher
        
        # UI 업데이트
        self._update_folder_watch_status()
        
        messagebox.showinfo("성공", f"폴더 감시 시작:\n{folder_str}")
    
    def on_watched_file_found(self, pdf_path: Path, folder_config: FolderConfig):
        """감시 중인 폴더에서 PDF 발견"""
        # 파일 처리
        self.window.file_controller.add_file(
            str(pdf_path),
            profile_name=folder_config.profile_name
        )
        
        # 자동 처리
        if folder_config.auto_process:
            self.window.file_controller.start_processing()
    
    def start_all_watchers(self):
        """모든 폴더 감시 시작"""
        settings = self.window.settings_controller.get_settings()
        for folder_config in settings.watched_folders:
            if folder_config.enabled:
                self.add_watch_folder(folder_config.path)
    
    def stop_all_watchers(self):
        """모든 폴더 감시 중지"""
        for watcher in self.window.folder_watchers.values():
            watcher.stop()
        self.window.folder_watchers.clear()
        self._update_folder_watch_status()
    
    def stop_watcher(self, folder_path: str):
        """특정 폴더 감시 중지"""
        if folder_path in self.window.folder_watchers:
            self.window.folder_watchers[folder_path].stop()
            del self.window.folder_watchers[folder_path]
            self._update_folder_watch_status()
    
    def _update_folder_watch_status(self):
        """폴더 감시 상태 업데이트"""
        watch_count = len(self.window.folder_watchers)
        
        # 상태바 업데이트
        if hasattr(self.window, 'statusbar'):
            if watch_count > 0:
                self.window.statusbar.set_status(
                    f"폴더 감시 중: {watch_count}개",
                    "info"
                )
            else:
                self.window.statusbar.set_status("폴더 감시 중지", "normal")
        
        # 사이드바 업데이트
        if hasattr(self.window, 'sidebar'):
            self.window.sidebar.update_watch_status(watch_count)
    
    def get_watched_folders(self):
        """감시 중인 폴더 목록 반환"""
        return list(self.window.folder_watchers.keys())
    
    def is_watching(self, folder_path: str) -> bool:
        """폴더 감시 여부 확인"""
        return folder_path in self.window.folder_watchers
    
    def get_watcher_status(self, folder_path: str) -> dict:
        """감시자 상태 반환"""
        if folder_path in self.window.folder_watchers:
            watcher = self.window.folder_watchers[folder_path]
            return {
                'active': watcher.is_alive(),
                'config': watcher.folder_config,
                'files_found': getattr(watcher, 'files_found', 0)
            }
        return None
"""
윈도우 매니저들 통합
file_manager.py + folder_watcher_manager.py 통합
"""

import json
from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, List, Dict
from pathlib import Path

from ....processing import FolderWatcher, FolderConfig

if TYPE_CHECKING:
    from .main_window import MainWindow


class FileManager:
    """파일 매니저 - 파일 작업 관리"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def open_files(self):
        """파일 열기"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            pdf_files = [Path(f) for f in files if f.endswith('.pdf')]
            if pdf_files:
                self.process_files(pdf_files)
            else:
                messagebox.showwarning("경고", "PDF 파일을 선택해주세요.")
    
    def open_folder(self):
        """폴더 열기"""
        folder = filedialog.askdirectory(title="PDF 파일이 있는 폴더 선택")
        
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            if pdf_files:
                self.process_files(pdf_files)
            else:
                messagebox.showinfo("정보", "선택한 폴더에 PDF 파일이 없습니다.")
    
    def open_recent_files(self, files: List[Path]):
        """최근 파일 열기"""
        self.process_files(files)
    
    def process_files(self, files: List[Path]):
        """파일 처리"""
        if not files:
            return
        
        # 파일 컨트롤러로 처리
        for file_path in files:
            if file_path.exists() and file_path.suffix.lower() == '.pdf':
                self.window.file_controller.add_file(str(file_path))
                self.add_recent_file(str(file_path))
        
        # 통합 처리 뷰로 전환
        self.window.switch_tab('unified_processing')
        
        # 처리 시작
        self.window.file_controller.start_processing()
    
    def load_recent_files(self):
        """최근 파일 목록 로드"""
        try:
            recent_file = Path("data/recent_files.json")
            if recent_file.exists():
                with open(recent_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.window.recent_files = data.get('recent_files', [])
            else:
                self.window.recent_files = []
        except Exception as e:
            print(f"최근 파일 로드 실패: {e}")
            self.window.recent_files = []
    
    def save_recent_files(self):
        """최근 파일 목록 저장"""
        try:
            recent_file = Path("data/recent_files.json")
            recent_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(recent_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'recent_files': self.window.recent_files[:10]  # 최대 10개
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"최근 파일 저장 실패: {e}")
    
    def add_recent_file(self, file_path: str):
        """최근 파일 추가"""
        # 이미 있으면 제거
        if file_path in self.window.recent_files:
            self.window.recent_files.remove(file_path)
        
        # 맨 앞에 추가
        self.window.recent_files.insert(0, file_path)
        
        # 최대 10개 유지
        self.window.recent_files = self.window.recent_files[:10]
        
        # 메뉴 업데이트
        if hasattr(self.window, 'menubar'):
            self.window.menubar.update_recent_files(
                [Path(f) for f in self.window.recent_files if Path(f).exists()]
            )
        
        # 저장
        self.save_recent_files()
    
    def clear_recent_files(self):
        """최근 파일 목록 초기화"""
        self.window.recent_files = []
        self.save_recent_files()
        
        # 메뉴 업데이트
        if hasattr(self.window, 'menubar'):
            self.window.menubar.update_recent_files([])


class FolderWatcherManager:
    """폴더 감시 매니저 - 폴더 감시 관리"""
    
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
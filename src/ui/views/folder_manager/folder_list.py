"""
폴더 리스트 매니저 - 폴더 목록 관리
"""

from typing import TYPE_CHECKING, List
import json
from pathlib import Path

if TYPE_CHECKING:
    from .base import FolderManagerView


class FolderListManager:
    """폴더 리스트 매니저"""
    
    def __init__(self, view: 'FolderManagerView'):
        self.view = view
        self.folders: List[str] = []
    
    def load_folders(self):
        """폴더 목록 로드"""
        # 설정 파일에서 폴더 목록 로드
        try:
            config_file = Path("data/folder_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.folders = data.get('folders', [])
            else:
                self.folders = []
        except Exception as e:
            print(f"폴더 목록 로드 실패: {e}")
            self.folders = []
        
        # UI 업데이트
        self._update_folder_list()
    
    def _update_folder_list(self):
        """폴더 목록 UI 업데이트"""
        listbox = self.view.widgets.get('folder_listbox')
        if listbox:
            listbox.delete(0, 'end')
            for folder in self.folders:
                listbox.insert('end', folder)
    
    def add_folder(self, folder_path: str):
        """폴더 추가"""
        if folder_path and folder_path not in self.folders:
            self.folders.append(folder_path)
            self._update_folder_list()
            self._save_folders()
            
            # 추가된 폴더 선택
            listbox = self.view.widgets.get('folder_listbox')
            if listbox:
                listbox.selection_clear(0, 'end')
                listbox.selection_set(len(self.folders) - 1)
                self.view.on_folder_select(folder_path)
    
    def remove_folder(self, folder_path: str):
        """폴더 제거"""
        if folder_path in self.folders:
            self.folders.remove(folder_path)
            self._update_folder_list()
            self._save_folders()
            
            # 폴더 감시 중지
            if self.view.folder_watcher:
                self.view.folder_watcher.remove_folder(folder_path)
    
    def _save_folders(self):
        """폴더 목록 저장"""
        try:
            config_file = Path("data/folder_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({'folders': self.folders}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"폴더 목록 저장 실패: {e}")
    
    def get_selected_folder(self) -> str:
        """선택된 폴더 반환"""
        listbox = self.view.widgets.get('folder_listbox')
        if listbox:
            selection = listbox.curselection()
            if selection:
                return listbox.get(selection[0])
        return None
    
    def folder_exists(self, folder_path: str) -> bool:
        """폴더 존재 여부 확인"""
        return folder_path in self.folders
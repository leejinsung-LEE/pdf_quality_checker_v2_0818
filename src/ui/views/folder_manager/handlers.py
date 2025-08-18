"""
이벤트 핸들러 - 폴더 관리 이벤트 처리
"""

from tkinter import filedialog, messagebox
from typing import TYPE_CHECKING, Dict, Any
from pathlib import Path

if TYPE_CHECKING:
    from .base import FolderManagerView


class EventHandler:
    """이벤트 핸들러"""
    
    def __init__(self, view: 'FolderManagerView'):
        self.view = view
    
    def browse_folder(self) -> str:
        """폴더 선택 다이얼로그"""
        folder = filedialog.askdirectory(
            title="폴더 선택",
            parent=self.view
        )
        return folder
    
    def save_settings(self, folder_path: str, settings: Dict[str, Any]):
        """설정 저장"""
        try:
            # SettingsManager에서 저장 처리
            self.view.settings_manager.save_settings(folder_path, settings)
            
            # 폴더 감시 업데이트
            if self.view.folder_watcher and settings.get('enabled'):
                # 감시 시작/재시작
                self.view.folder_watcher.start_watching(folder_path)
            elif self.view.folder_watcher and not settings.get('enabled'):
                # 감시 중지
                self.view.folder_watcher.stop_watching(folder_path)
            
            messagebox.showinfo(
                "성공",
                f"폴더 설정이 저장되었습니다:\n{folder_path}",
                parent=self.view
            )
            
        except Exception as e:
            messagebox.showerror(
                "오류",
                f"설정 저장 실패:\n{str(e)}",
                parent=self.view
            )
    
    def confirm_remove_folder(self, folder_path: str) -> bool:
        """폴더 제거 확인"""
        result = messagebox.askyesno(
            "확인",
            f"이 폴더를 목록에서 제거하시겠습니까?\n{folder_path}",
            parent=self.view
        )
        return result
    
    def show_folder_info(self, folder_path: str):
        """폴더 정보 표시"""
        if not folder_path:
            return
        
        path = Path(folder_path)
        if path.exists():
            # PDF 파일 수 계산
            pdf_files = list(path.glob("*.pdf"))
            
            info = f"폴더: {folder_path}\n"
            info += f"PDF 파일 수: {len(pdf_files)}개\n"
            
            # 폴더 크기 계산
            total_size = sum(f.stat().st_size for f in pdf_files)
            size_mb = total_size / (1024 * 1024)
            info += f"총 크기: {size_mb:.1f} MB"
            
            messagebox.showinfo("폴더 정보", info, parent=self.view)
        else:
            messagebox.showwarning(
                "경고",
                f"폴더가 존재하지 않습니다:\n{folder_path}",
                parent=self.view
            )
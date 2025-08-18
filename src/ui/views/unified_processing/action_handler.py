"""
액션 처리 헬퍼 클래스
기능: 사용자 액션 및 명령 처리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, List, Optional
from tkinter import filedialog, messagebox
import webbrowser
import os

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import UnifiedProcessingView

from ...controllers import FileStatus, FileItem
from ....data import HistoryEntry


class ActionHandler:
    """
    사용자 액션 처리 헬퍼
    
    역할:
    - 파일 추가/제거
    - 처리 제어
    - 보고서 관리
    """
    
    def __init__(self, view: 'UnifiedProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            for file_path in files:
                self.view.controller.add_file(file_path)
    
    def toggle_pause(self):
        """처리 일시정지/재개"""
        is_paused = self.view.controller.toggle_pause()
        
        # UI 업데이트
        if is_paused:
            messagebox.showinfo("일시정지", "처리가 일시정지되었습니다.")
            # 버튼 텍스트 업데이트 (옵션)
            if hasattr(self.view, 'pause_button'):
                self.view.pause_button.configure(text="재개")
        else:
            messagebox.showinfo("재개", "처리가 재개되었습니다.")
            # 버튼 텍스트 업데이트 (옵션)
            if hasattr(self.view, 'pause_button'):
                self.view.pause_button.configure(text="일시정지")
        
        self.view.refresh()
    
    def clear_completed(self):
        """완료된 항목 제거"""
        # 실시간 항목 중 완료된 것들 제거
        completed_ids = [
            file_id for file_id, file_item in self.view.controller.file_items.items()
            if file_item.status in [FileStatus.COMPLETED, FileStatus.ERROR, FileStatus.CANCELLED]
        ]
        
        for file_id in completed_ids:
            self.view.controller.remove_file(file_id)
        
        self.view.refresh()
    
    def open_selected_file(self):
        """선택된 파일 열기"""
        if not hasattr(self.view, 'tree'):
            return
            
        selection = self.view.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id == 'separator':
            return
        
        item = self.view.all_items.get(item_id)
        if item:
            if isinstance(item, FileItem):
                if item.path.exists():
                    os.startfile(str(item.path))
            elif isinstance(item, HistoryEntry):
                if os.path.exists(item.file_path):
                    os.startfile(item.file_path)
    
    def view_report(self):
        """보고서 보기"""
        if not hasattr(self.view, 'tree'):
            return
            
        selection = self.view.tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        if item_id == 'separator':
            return
        
        item = self.view.all_items.get(item_id)
        if item:
            if isinstance(item, HistoryEntry):
                if item.report_path and os.path.exists(item.report_path):
                    webbrowser.open(item.report_path)
                else:
                    messagebox.showwarning("보고서 없음", "보고서를 찾을 수 없습니다.")
            else:
                messagebox.showinfo("보고서", "처리가 완료된 후 보고서를 확인할 수 있습니다.")
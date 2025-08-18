"""
이벤트 처리 헬퍼 클래스
기능: 컨트롤러 콜백 및 UI 이벤트 처리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING
from tkinter import filedialog, messagebox
from pathlib import Path
import webbrowser
import subprocess
import platform

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProcessingView

from ...controllers import FileStatus, FileItem


class EventHandler:
    """
    이벤트 처리 헬퍼
    
    역할:
    - 컨트롤러 콜백 설정
    - UI 이벤트 처리
    - 사용자 액션 처리
    """
    
    def __init__(self, view: 'ProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        if self.view.controller:
            self.view.controller.set_ui_callbacks(
                on_file_added=self._on_file_added,
                on_file_status_changed=self._on_file_status_changed,
                on_file_progress=self._on_file_progress,
                on_file_completed=self._on_file_completed,
                on_file_error=self._on_file_error
            )
    
    # 컨트롤러 콜백 메서드
    
    def _on_file_added(self, file_item: FileItem):
        """파일 추가 콜백"""
        self.view.file_list_manager.add_file(file_item)
    
    def _on_file_status_changed(self, file_id: str, status: FileStatus):
        """파일 상태 변경 콜백"""
        self.view.file_list_manager.update_file_status(file_id, status)
    
    def _on_file_progress(self, file_id: str, progress: int, message: str):
        """파일 진행률 콜백"""
        self.view.file_list_manager.update_file_progress(file_id, progress, message)
    
    def _on_file_completed(self, file_id: str, file_item: FileItem):
        """파일 완료 콜백"""
        self.view.file_list_manager.update_file_complete(file_id, file_item)
    
    def _on_file_error(self, file_id: str, error: str):
        """파일 오류 콜백"""
        if self.view.tree and self.view.tree.exists(file_id):
            values = list(self.view.tree.item(file_id)['values'])
            values[0] = self.view.STATUS_ICONS[FileStatus.ERROR]
            values[9] = f"오류: {error[:30]}..."
            self.view.tree.item(file_id, values=values, tags=('error',))
            
            # 통계 업데이트
            self.view.file_list_manager.update_statistics()
    
    # UI 이벤트 핸들러
    
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files and self.view.controller:
            file_paths = [Path(f) for f in files]
            self.view.controller.add_files(file_paths)
    
    def add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="PDF 파일이 있는 폴더 선택")
        
        if folder and self.view.controller:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            if pdf_files:
                self.view.controller.add_files(pdf_files)
                messagebox.showinfo("폴더 추가", 
                                  f"{len(pdf_files)}개의 PDF 파일을 추가했습니다.")
            else:
                messagebox.showwarning("폴더 추가", 
                                     "선택한 폴더에 PDF 파일이 없습니다.")
    
    def retry_selected(self):
        """선택 파일 재처리"""
        if self.view.controller:
            for file_id in self.view.selected_items:
                self.view.controller.retry_file(file_id)
    
    def cancel_selected(self):
        """선택 파일 취소"""
        if self.view.controller:
            for file_id in self.view.selected_items:
                self.view.controller.cancel_file(file_id)
    
    def remove_selected(self):
        """선택 파일 제거"""
        count = len(self.view.selected_items)
        if count > 0 and messagebox.askyesno("확인", f"{count}개 파일을 목록에서 제거하시겠습니까?"):
            if self.view.tree:
                for file_id in self.view.selected_items.copy():
                    self.view.tree.delete(file_id)
                    self.view.selected_items.discard(file_id)
                
                self.view.file_list_manager.update_statistics()
                self.view.file_list_manager.update_selection_info()
    
    def on_tree_click(self, event):
        """트리 클릭 이벤트"""
        if not self.view.tree:
            return
            
        # 체크박스 영역 클릭 확인
        region = self.view.tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.view.tree.identify_row(event.y)
            if item:
                # 체크박스 토글
                if item in self.view.selected_items:
                    self.view.selected_items.discard(item)
                    self.view.tree.item(item, text='☐')
                else:
                    self.view.selected_items.add(item)
                    self.view.tree.item(item, text='☑')
                
                self.view.file_list_manager.update_selection_info()
    
    def on_double_click(self, event):
        """더블클릭 이벤트"""
        if not self.view.tree:
            return
            
        item = self.view.tree.identify_row(event.y)
        if item:
            self._view_report_for_item(item)
    
    def show_context_menu(self, event):
        """컨텍스트 메뉴 표시"""
        if not self.view.tree or not self.view.context_menu:
            return
            
        item = self.view.tree.identify_row(event.y)
        if item:
            self.view.tree.selection_set(item)
            self.view.context_menu.post(event.x_root, event.y_root)
    
    def view_report(self):
        """보고서 보기"""
        if self.view.tree:
            selection = self.view.tree.selection()
            if selection:
                self._view_report_for_item(selection[0])
    
    def _view_report_for_item(self, file_id: str):
        """특정 아이템의 보고서 보기"""
        if self.view.controller:
            file_item = self.view.controller.get_file_item(file_id)
            if file_item and file_item.report_paths:
                # HTML 보고서 우선
                if 'html' in file_item.report_paths:
                    webbrowser.open(str(file_item.report_paths['html']))
    
    def show_in_folder(self):
        """폴더에서 보기"""
        if not self.view.tree or not self.view.controller:
            return
            
        selection = self.view.tree.selection()
        if selection:
            file_item = self.view.controller.get_file_item(selection[0])
            if file_item:
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', str(file_item.path)])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', str(file_item.path)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(file_item.path.parent)])
    
    def retry_file(self):
        """파일 재처리"""
        if self.view.tree and self.view.controller:
            selection = self.view.tree.selection()
            if selection:
                self.view.controller.retry_file(selection[0])
    
    def cancel_file(self):
        """파일 처리 취소"""
        if self.view.tree and self.view.controller:
            selection = self.view.tree.selection()
            if selection:
                self.view.controller.cancel_file(selection[0])
    
    def remove_file(self):
        """파일 제거"""
        if not self.view.tree:
            return
            
        selection = self.view.tree.selection()
        if selection and messagebox.askyesno("확인", "선택한 파일을 목록에서 제거하시겠습니까?"):
            for item in selection:
                self.view.tree.delete(item)
                self.view.selected_items.discard(item)
            
            self.view.file_list_manager.update_statistics()
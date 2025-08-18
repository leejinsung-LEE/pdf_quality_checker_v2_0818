"""
파일 리스트 관리 헬퍼 클래스
기능: 트리뷰 데이터 관리, 필터링, 업데이트
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, List
from tkinter import messagebox

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProcessingView

from ...controllers import FileStatus, FileItem


class FileListManager:
    """
    파일 리스트 관리 헬퍼
    
    역할:
    - 트리뷰 데이터 관리
    - 필터링 및 검색
    - 파일 상태 업데이트
    """
    
    def __init__(self, view: 'ProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def add_file(self, file_item: FileItem):
        """파일 추가"""
        if not self.view.tree:
            return
            
        # 상태 아이콘
        icon = self.view.STATUS_ICONS.get(file_item.status, '')
        
        # 트리에 아이템 추가
        values = self._create_tree_values(file_item)
        
        self.view.tree.insert('', 'end',
                             iid=file_item.file_id,
                             text='☐',
                             values=values,
                             tags=(self.view.STATUS_TAGS.get(file_item.status, ''),))
        
        # 폴더 필터 업데이트
        self.update_folder_filter(file_item)
        
        # 통계 업데이트
        self.update_statistics()
    
    def update_file_status(self, file_id: str, status: FileStatus):
        """파일 상태 업데이트"""
        if not self.view.tree or not self.view.tree.exists(file_id):
            return
        
        # 아이콘 업데이트
        values = list(self.view.tree.item(file_id)['values'])
        values[0] = self.view.STATUS_ICONS.get(status, '')
        values[9] = self._get_status_text(status)
        
        self.view.tree.item(file_id, values=values, 
                          tags=(self.view.STATUS_TAGS.get(status, ''),))
        
        # 통계 업데이트
        self.update_statistics()
    
    def update_file_progress(self, file_id: str, progress: int, message: str):
        """파일 진행률 업데이트"""
        if not self.view.tree or not self.view.tree.exists(file_id):
            return
        
        values = list(self.view.tree.item(file_id)['values'])
        values[9] = f"{message} ({progress}%)"
        self.view.tree.item(file_id, values=values)
    
    def update_file_complete(self, file_id: str, file_item: FileItem):
        """파일 처리 완료 업데이트"""
        if not self.view.tree or not self.view.tree.exists(file_id):
            return
        
        values = self._create_tree_values(file_item)
        self.view.tree.item(file_id, values=values, 
                          tags=(self.view.STATUS_TAGS.get(file_item.status, ''),))
        
        # 통계 업데이트
        self.update_statistics()
    
    def apply_filters(self):
        """필터 적용"""
        if not self.view.tree:
            return
            
        # 모든 아이템 가져오기
        all_items = self.view.tree.get_children()
        
        # 필터 조건
        status_filter = self.view.filter_status.get()
        search_text = self.view.search_var.get().lower()
        folder_filter = self.view.folder_filter.get()
        
        for item_id in all_items:
            file_item = self.view.controller.get_file_item(item_id)
            if not file_item:
                continue
            
            show = True
            
            # 상태 필터
            if status_filter != "all":
                if status_filter == "waiting" and file_item.status != FileStatus.WAITING:
                    show = False
                elif status_filter == "processing" and file_item.status != FileStatus.PROCESSING:
                    show = False
                elif status_filter == "completed" and file_item.status != FileStatus.COMPLETED:
                    show = False
                elif status_filter == "error" and file_item.status != FileStatus.ERROR:
                    show = False
            
            # 검색 필터
            if show and search_text:
                if search_text not in file_item.filename.lower():
                    show = False
            
            # 폴더 필터
            if show and folder_filter != "all":
                if file_item.folder_name != folder_filter:
                    show = False
            
            # 표시/숨김
            if show:
                self.view.tree.reattach(item_id, '', 'end')
            else:
                self.view.tree.detach(item_id)
    
    def reset_filters(self):
        """필터 초기화"""
        self.view.filter_status.set("all")
        self.view.search_var.set("")
        self.view.folder_filter.set("all")
        self.apply_filters()
    
    def clear_completed(self):
        """완료 항목 정리"""
        if not self.view.tree:
            return
            
        if messagebox.askyesno("확인", "완료된 항목을 모두 제거하시겠습니까?"):
            completed_items = []
            for item_id in self.view.tree.get_children():
                file_item = self.view.controller.get_file_item(item_id)
                if file_item and file_item.status == FileStatus.COMPLETED:
                    completed_items.append(item_id)
            
            for item_id in completed_items:
                self.view.tree.delete(item_id)
                self.view.selected_items.discard(item_id)
            
            self.view.controller.clear_completed()
            self.update_statistics()
    
    def update_folder_filter(self, file_item: FileItem):
        """폴더 필터 업데이트"""
        if file_item.folder_name and 'folder_menu' in self.view.widgets:
            folder_menu = self.view.widgets['folder_menu']
            current_values = list(folder_menu.cget("values"))
            if file_item.folder_name not in current_values:
                current_values.append(file_item.folder_name)
                folder_menu.configure(values=current_values)
    
    def update_statistics(self):
        """통계 업데이트"""
        if not self.view.controller:
            return
            
        stats = self.view.controller.get_statistics()
        
        waiting = stats.get('by_status', {}).get('waiting', 0)
        processing = stats.get('by_status', {}).get('processing', 0)
        completed = stats.get('by_status', {}).get('completed', 0)
        
        if 'stats_label' in self.view.widgets:
            self.view.widgets['stats_label'].configure(
                text=f"대기: {waiting} | 처리중: {processing} | 완료: {completed}"
            )
    
    def update_selection_info(self):
        """선택 정보 업데이트"""
        count = len(self.view.selected_items)
        if 'selection_label' in self.view.widgets:
            self.view.widgets['selection_label'].configure(text=f"선택: {count}개")
    
    # 유틸리티 메서드
    
    def _create_tree_values(self, file_item: FileItem) -> List[str]:
        """트리 아이템 값 생성"""
        return [
            self.view.STATUS_ICONS.get(file_item.status, ''),     # icon
            file_item.filename,                                     # filename
            file_item.folder_name or "-",                          # folder
            file_item.profile,                                     # profile
            f"{file_item.size_mb:.1f} MB",                        # size
            "-",                                                   # pages (TODO)
            self._format_issues(file_item),                        # issues
            f"{file_item.quality_score:.0f}" if file_item.quality_score > 0 else "-",  # score
            self._format_time(file_item),                          # time
            self._get_status_text(file_item.status)                # status
        ]
    
    def _format_issues(self, file_item: FileItem) -> str:
        """이슈 포맷팅"""
        if file_item.error_count > 0 or file_item.warning_count > 0:
            return f"오류:{file_item.error_count} 경고:{file_item.warning_count}"
        return "-"
    
    def _format_time(self, file_item: FileItem) -> str:
        """시간 포맷팅"""
        if file_item.processing_time > 0:
            return f"{file_item.processing_time:.1f}초"
        elif file_item.start_time:
            return file_item.start_time.strftime("%H:%M:%S")
        return "-"
    
    def _get_status_text(self, status: FileStatus) -> str:
        """상태 텍스트"""
        status_texts = {
            FileStatus.WAITING: "대기 중",
            FileStatus.PROCESSING: "처리 중",
            FileStatus.COMPLETED: "완료",
            FileStatus.ERROR: "오류",
            FileStatus.CANCELLED: "취소됨"
        }
        return status_texts.get(status, "-")
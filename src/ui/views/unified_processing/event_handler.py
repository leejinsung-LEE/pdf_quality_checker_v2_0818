"""
이벤트 처리 헬퍼 클래스
기능: 컨트롤러 콜백 및 UI 이벤트 처리
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Any

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import UnifiedProcessingView

from ...controllers import FileStatus, FileItem
from ....data import HistoryEntry


class EventHandler:
    """
    이벤트 처리 헬퍼
    
    역할:
    - 컨트롤러 콜백 설정
    - UI 이벤트 처리
    - 실시간 업데이트
    """
    
    def __init__(self, view: 'UnifiedProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        # 파일 추가 콜백
        self.view.controller.on_file_added = self._on_file_added
        # 상태 변경 콜백
        self.view.controller.on_status_changed = self._on_status_changed
        # 진행률 업데이트 콜백
        self.view.controller.on_progress_updated = self._on_progress_updated
        # 파일 제거 콜백
        self.view.controller.on_file_removed = self._on_file_removed
    
    def _on_file_added(self, file_item: FileItem):
        """파일 추가 이벤트"""
        if self.view.data_handler._should_show_realtime_item(file_item):
            # 실시간 항목은 항상 상단에 추가
            # 구분선이 있으면 그 위에, 없으면 맨 위에
            if hasattr(self.view, 'tree'):
                separator_exists = self.view.tree.exists('separator')
                if separator_exists:
                    self.view.tree.move(file_item.file_id, '', 0)  # 맨 위로
                else:
                    self.view.data_handler._add_realtime_to_tree(file_item)
                
                self.view.all_items[file_item.file_id] = file_item
                
                # 통계 업데이트
                realtime_count = len([i for i in self.view.all_items.values() 
                                    if isinstance(i, FileItem)])
                history_count = len([i for i in self.view.all_items.values() 
                                   if isinstance(i, HistoryEntry)])
                self.view.data_handler._update_statistics(realtime_count, history_count)
    
    def _on_status_changed(self, file_id: str, status: FileStatus):
        """상태 변경 이벤트"""
        if file_id in self.view.controller.file_items:
            file_item = self.view.controller.file_items[file_id]
            
            # 트리 업데이트
            if hasattr(self.view, 'tree') and self.view.tree.exists(file_id):
                self._update_realtime_in_tree(file_item)
            
            # 완료된 경우 잠시 후 새로고침 (이력에 추가되도록)
            if status in [FileStatus.COMPLETED, FileStatus.ERROR]:
                self.view.after(2000, self.view.refresh)  # 2초 후 새로고침
    
    def _on_progress_updated(self, file_id: str, progress: int):
        """진행률 업데이트 이벤트"""
        if file_id in self.view.controller.file_items:
            file_item = self.view.controller.file_items[file_id]
            if hasattr(self.view, 'tree') and self.view.tree.exists(file_id):
                self._update_realtime_in_tree(file_item)
    
    def _on_file_removed(self, file_id: str):
        """파일 제거 이벤트"""
        if hasattr(self.view, 'tree') and self.view.tree.exists(file_id):
            self.view.tree.delete(file_id)
            if file_id in self.view.all_items:
                del self.view.all_items[file_id]
    
    def _update_realtime_in_tree(self, file_item: FileItem):
        """실시간 항목 업데이트"""
        if not hasattr(self.view, 'tree') or not self.view.tree.exists(file_item.file_id):
            return
        
        # 아이콘
        icon = self.view.STATUS_ICONS.get(file_item.status, '')
        
        # 태그
        tag = self.view.STATUS_TAGS.get(file_item.status, '')
        
        # 문제 수
        issues = file_item.error_count + file_item.warning_count
        issues_str = f"⚠️ {issues}" if issues > 0 else "✅ 0"
        
        # 진행률
        if file_item.status == FileStatus.PROCESSING:
            progress_str = f"{file_item.progress}%"
        elif file_item.status == FileStatus.WAITING:
            progress_str = "대기중"
        else:
            progress_str = "완료"
        
        # 처리 시간
        if file_item.processing_time > 0:
            time_str = f"{file_item.processing_time:.1f}초"
        else:
            time_str = "-"
        
        # 파일 크기
        size_str = f"{file_item.size_mb:.1f} MB"
        
        values = (
            '실시간',
            file_item.status.value,
            file_item.filename,
            file_item.profile or 'Default',
            size_str,
            '-',
            issues_str,
            progress_str,
            time_str,
            '-'
        )
        
        self.view.tree.item(
            file_item.file_id,
            text=icon,
            values=values,
            tags=(tag,)
        )
    
    def on_double_click(self, event):
        """더블클릭 이벤트"""
        if hasattr(self.view, 'action_handler'):
            self.view.action_handler.open_selected_file()
    
    def on_selection(self, event):
        """선택 이벤트"""
        if hasattr(self.view, 'tree'):
            self.view.selected_items = set(self.view.tree.selection())
            # separator는 선택에서 제외
            self.view.selected_items.discard('separator')
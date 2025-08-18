"""
Process Monitor View 트리 핸들러 모듈
기능: 트리뷰 데이터 관리, 아이템 추가/업데이트/삭제
의존성: tkinter.ttk, FileItem, HistoryEntry
최종 수정: 2025-01-11
"""

from typing import TYPE_CHECKING, Optional, Tuple
from datetime import datetime, timedelta
import tkinter as tk

from ...controllers import FileStatus, FileItem
from ....data import HistoryEntry

if TYPE_CHECKING:
    from .base import ProcessMonitorView


class TreeHandler:
    """트리뷰 관리 헬퍼 클래스"""
    
    def __init__(self, view: 'ProcessMonitorView'):
        """
        초기화
        
        Args:
            view: ProcessMonitorView 인스턴스
        """
        self.view = view
    
    def on_file_added(self, file_item: FileItem):
        """파일 추가 콜백"""
        self._add_file_to_tree(file_item)
        self._update_realtime_stats()
    
    def on_status_changed(self, file_id: str, status: FileStatus):
        """상태 변경 콜백"""
        file_item = self.view.controller.get_file(file_id)
        if file_item:
            self._update_file_in_tree(file_item)
            self._update_realtime_stats()
            
            # 완료된 항목은 이력에도 추가
            if status == FileStatus.COMPLETED:
                self.view.after(1000, self.refresh_history)
    
    def on_progress_updated(self, file_id: str, progress: int):
        """진행률 업데이트 콜백"""
        file_item = self.view.controller.get_file(file_id)
        if file_item:
            self._update_file_progress(file_item, progress)
    
    def on_file_removed(self, file_id: str):
        """파일 제거 콜백"""
        # 트리에서 아이템 제거
        for item_id in self.view.realtime_tree.get_children():
            if self.view.realtime_tree.item(item_id)['tags'][0] == file_id:
                self.view.realtime_tree.delete(item_id)
                break
        self._update_realtime_stats()
    
    def _add_file_to_tree(self, file_item: FileItem):
        """트리에 파일 추가"""
        # 이미 있는지 확인
        for item_id in self.view.realtime_tree.get_children():
            if self.view.realtime_tree.item(item_id)['tags'][0] == file_item.id:
                return
        
        # 상태 아이콘
        status_icon = self.view.STATUS_ICONS.get(file_item.status, '❓')
        
        # 시간 포맷
        time_str = file_item.added_time.strftime("%H:%M:%S")
        
        # 진행률 텍스트
        if file_item.status == FileStatus.PROCESSING:
            progress_text = f"{file_item.progress}%"
        elif file_item.status == FileStatus.COMPLETED:
            progress_text = "100%"
        else:
            progress_text = "-"
        
        # 메시지
        message = ""
        if file_item.error_message:
            message = file_item.error_message[:50]
        elif file_item.status == FileStatus.PROCESSING:
            message = "처리 중..."
        elif file_item.status == FileStatus.COMPLETED:
            if file_item.result:
                message = f"오류: {file_item.result.error_count}, 경고: {file_item.result.warning_count}"
            else:
                message = "완료"
        
        # 트리에 추가
        values = (
            status_icon,
            file_item.filename,
            file_item.profile or "default",
            progress_text,
            time_str,
            message
        )
        
        item_id = self.view.realtime_tree.insert(
            '',
            'end',
            values=values,
            tags=(file_item.id, self.view.STATUS_TAGS[file_item.status])
        )
        
        # 선택 상태 복원
        if file_item.id in self.view.selected_items:
            self.view.realtime_tree.selection_add(item_id)
    
    def _update_file_in_tree(self, file_item: FileItem):
        """트리에서 파일 업데이트"""
        for item_id in self.view.realtime_tree.get_children():
            if self.view.realtime_tree.item(item_id)['tags'][0] == file_item.id:
                # 기존 값 가져오기
                values = list(self.view.realtime_tree.item(item_id)['values'])
                
                # 상태 아이콘 업데이트
                values[0] = self.view.STATUS_ICONS.get(file_item.status, '❓')
                
                # 진행률 업데이트
                if file_item.status == FileStatus.PROCESSING:
                    values[3] = f"{file_item.progress}%"
                elif file_item.status == FileStatus.COMPLETED:
                    values[3] = "100%"
                    # 처리 시간 추가
                    if file_item.end_time:
                        duration = file_item.end_time - file_item.added_time
                        values[4] = f"{values[4]} ({duration.seconds}초)"
                
                # 메시지 업데이트
                if file_item.error_message:
                    values[5] = file_item.error_message[:50]
                elif file_item.status == FileStatus.COMPLETED and file_item.result:
                    values[5] = f"오류: {file_item.result.error_count}, 경고: {file_item.result.warning_count}"
                elif file_item.status == FileStatus.PROCESSING:
                    values[5] = "처리 중..."
                
                # 트리 아이템 업데이트
                self.view.realtime_tree.item(
                    item_id,
                    values=values,
                    tags=(file_item.id, self.view.STATUS_TAGS[file_item.status])
                )
                break
    
    def _update_file_progress(self, file_item: FileItem, progress: int):
        """파일 진행률만 업데이트"""
        for item_id in self.view.realtime_tree.get_children():
            if self.view.realtime_tree.item(item_id)['tags'][0] == file_item.id:
                values = list(self.view.realtime_tree.item(item_id)['values'])
                values[3] = f"{progress}%"
                self.view.realtime_tree.item(item_id, values=values)
                break
    
    def _update_realtime_stats(self):
        """실시간 통계 업데이트"""
        files = self.view.controller.get_all_files()
        
        total = len(files)
        waiting = sum(1 for f in files if f.status == FileStatus.WAITING)
        processing = sum(1 for f in files if f.status == FileStatus.PROCESSING)
        completed = sum(1 for f in files if f.status == FileStatus.COMPLETED)
        errors = sum(1 for f in files if f.status == FileStatus.ERROR)
        
        stats_text = f"전체: {total} | 대기: {waiting} | 처리중: {processing} | 완료: {completed} | 오류: {errors}"
        self.view.realtime_stats_label.configure(text=stats_text)
    
    def refresh(self):
        """실시간 처리 목록 새로고침"""
        # 기존 항목 제거
        for item in self.view.realtime_tree.get_children():
            self.view.realtime_tree.delete(item)
        
        # 필터 적용하여 파일 목록 가져오기
        files = self.view.controller.get_all_files()
        
        # 필터링
        for file_item in files:
            if self._should_show_file(file_item):
                self._add_file_to_tree(file_item)
        
        # 통계 업데이트
        self._update_realtime_stats()
    
    def refresh_history(self):
        """처리 이력 새로고침"""
        # 기존 항목 제거
        for item in self.view.history_tree.get_children():
            self.view.history_tree.delete(item)
        
        # 날짜 범위 계산
        date_range = self._calculate_date_range()
        
        # 필터 조건
        filters = {
            'profile_filter': None if self.view.profile_filter.get() == 'all' else self.view.profile_filter.get(),
            'filename_filter': self.view.search_var.get() if self.view.search_var.get() else None
        }
        
        # 데이터 조회
        if date_range:
            start_date, end_date = date_range
            entries = self.view.data_manager.get_history(
                start_date=start_date,
                end_date=end_date,
                limit=self.view.items_per_page,
                offset=(self.view.current_page - 1) * self.view.items_per_page,
                **filters
            )
            
            # 전체 개수 조회
            self.view.total_items = self.view.data_manager.get_history_count(
                start_date=start_date,
                end_date=end_date,
                **filters
            )
        else:
            entries = self.view.data_manager.get_history(
                limit=self.view.items_per_page,
                offset=(self.view.current_page - 1) * self.view.items_per_page,
                **filters
            )
            self.view.total_items = self.view.data_manager.get_history_count(**filters)
        
        # 현재 항목 저장
        self.view.current_entries = entries
        
        # 트리에 추가
        for entry in entries:
            self._add_history_to_tree(entry)
        
        # 통계 및 페이지네이션 업데이트
        self._update_history_stats()
        self._update_pagination()
    
    def _add_history_to_tree(self, entry: HistoryEntry):
        """이력 트리에 항목 추가"""
        # 날짜 포맷
        date_str = entry.timestamp.strftime("%Y-%m-%d %H:%M")
        
        # 점수 계산 (오류와 경고 기반)
        if entry.error_count == 0 and entry.warning_count == 0:
            score = 100
        else:
            score = max(0, 100 - (entry.error_count * 10) - (entry.warning_count * 5))
        
        # 점수별 색상 태그
        if score >= 90:
            score_tag = 'success'
        elif score >= 70:
            score_tag = 'warning'
        else:
            score_tag = 'error'
        
        values = (
            date_str,
            entry.filename,
            entry.profile or "default",
            f"{entry.page_count}p" if entry.page_count else "-",
            str(entry.error_count),
            str(entry.warning_count),
            f"{score}점"
        )
        
        item_id = self.view.history_tree.insert(
            '',
            'end',
            values=values,
            tags=(str(entry.id), score_tag)
        )
        
        # 선택 상태 복원
        if entry.id in self.view.selected_history_ids:
            self.view.history_tree.selection_add(item_id)
    
    def _update_history_stats(self):
        """이력 통계 업데이트"""
        if self.view.current_entries:
            total_errors = sum(e.error_count for e in self.view.current_entries)
            total_warnings = sum(e.warning_count for e in self.view.current_entries)
            avg_score = sum(
                max(0, 100 - (e.error_count * 10) - (e.warning_count * 5))
                for e in self.view.current_entries
            ) // len(self.view.current_entries)
            
            stats_text = f"항목: {len(self.view.current_entries)} | 오류: {total_errors} | 경고: {total_warnings} | 평균: {avg_score}점"
        else:
            stats_text = "데이터 없음"
        
        self.view.history_stats_label.configure(text=stats_text)
    
    def _update_pagination(self):
        """페이지네이션 업데이트"""
        total_pages = (self.view.total_items + self.view.items_per_page - 1) // self.view.items_per_page
        total_pages = max(1, total_pages)
        
        page_text = f"페이지 {self.view.current_page} / {total_pages} (총 {self.view.total_items}개)"
        self.view.page_label.configure(text=page_text)
    
    def _calculate_date_range(self) -> Optional[Tuple[datetime, datetime]]:
        """날짜 범위 계산"""
        now = datetime.now()
        date_range_value = self.view.date_range.get()
        
        if date_range_value == "today":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = now
        elif date_range_value == "week":
            start = now - timedelta(days=7)
            end = now
        elif date_range_value == "month":
            start = now - timedelta(days=30)
            end = now
        elif date_range_value == "all":
            return None
        elif date_range_value == "custom":
            if self.view.custom_start_date and self.view.custom_end_date:
                start = datetime.combine(self.view.custom_start_date, datetime.min.time())
                end = datetime.combine(self.view.custom_end_date, datetime.max.time())
            else:
                return None
        else:
            return None
        
        return (start, end)
    
    def _should_show_file(self, file_item: FileItem) -> bool:
        """파일 표시 여부 판단"""
        # 상태 필터
        status_filter = self.view.filter_status.get()
        if status_filter != "all":
            status_map = {
                "waiting": FileStatus.WAITING,
                "processing": FileStatus.PROCESSING,
                "completed": FileStatus.COMPLETED,
                "error": FileStatus.ERROR
            }
            if file_item.status != status_map.get(status_filter):
                return False
        
        # 검색 필터
        search_text = self.view.search_var.get().lower()
        if search_text and search_text not in file_item.filename.lower():
            return False
        
        # 폴더 필터
        folder_filter = self.view.folder_filter.get()
        if folder_filter != "all" and str(file_item.filepath.parent) != folder_filter:
            return False
        
        return True
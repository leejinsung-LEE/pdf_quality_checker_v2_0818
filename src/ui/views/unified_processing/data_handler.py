"""
데이터 처리 헬퍼 클래스
기능: 실시간 처리 항목과 이력 데이터 관리, 필터링, 정렬
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import UnifiedProcessingView

from ...controllers import FileStatus, FileItem
from ....data import HistoryEntry


class DataHandler:
    """
    데이터 처리 및 관리 헬퍼
    
    역할:
    - 실시간/이력 데이터 로드
    - 필터링 및 검색
    - 트리뷰 데이터 업데이트
    """
    
    def __init__(self, view: 'UnifiedProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def refresh(self):
        """전체 데이터 새로고침"""
        # 트리 초기화
        if hasattr(self.view, 'tree'):
            for item in self.view.tree.get_children():
                self.view.tree.delete(item)
        
        # 데이터 초기화
        self.view.all_items.clear()
        
        # 실시간 처리 항목 추가
        realtime_count = self._add_realtime_items()
        
        # 구분선 추가 (실시간 항목이 있고 이력도 표시할 경우)
        if realtime_count > 0 and self.view.filter_status.get() != "processing":
            self._add_separator()
        
        # 처리 이력 추가
        history_count = self._add_history_items()
        
        # 통계 업데이트
        self._update_statistics(realtime_count, history_count)
    
    def _add_realtime_items(self) -> int:
        """실시간 처리 항목 추가"""
        count = 0
        
        # 컨트롤러의 현재 파일들 처리
        for file_item in self.view.controller.file_items.values():
            if self._should_show_realtime_item(file_item):
                self._add_realtime_to_tree(file_item)
                self.view.all_items[file_item.file_id] = file_item
                count += 1
        
        return count
    
    def _add_history_items(self) -> int:
        """처리 이력 항목 추가"""
        # history_only 필터가 아니고 실시간 처리만 보기일 때는 이력 표시 안함
        if self.view.filter_status.get() in ["processing", "waiting"]:
            return 0
        
        # 날짜 범위 계산
        date_range = self._calculate_date_range()
        
        # 이력 데이터 가져오기
        entries = self.view.data_manager.get_history(
            limit=self.view.max_history_items,
            offset=0,
            start_date=date_range[0] if date_range else None,
            end_date=date_range[1] if date_range else None,
            filename_filter=self.view.search_var.get() if self.view.search_var.get() else None,
            status_filter=None,  # 상태 필터는 직접 처리
            profile_filter=self.view.profile_filter.get() if self.view.profile_filter.get() != 'all' else None
        )
        
        count = 0
        for entry in entries:
            if self._should_show_history_item(entry):
                self._add_history_to_tree(entry)
                # 이력 항목은 'history_' 접두사를 붙여 저장
                self.view.all_items[f"history_{entry.id}"] = entry
                count += 1
        
        return count
    
    def _add_separator(self):
        """구분선 추가"""
        if hasattr(self.view, 'tree'):
            self.view.tree.insert(
                '',
                'end',
                iid='separator',
                text='',
                values=('', '━━━━━━', '━━━ 처리 이력 ━━━', '', '', '', '', '', '', ''),
                tags=('separator',)
            )
    
    def _add_realtime_to_tree(self, file_item: FileItem):
        """실시간 항목을 트리에 추가"""
        if not hasattr(self.view, 'tree'):
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
            '-',  # 페이지 수 (아직 모름)
            issues_str,
            progress_str,
            time_str,
            '-'  # 처리일시 (진행중)
        )
        
        self.view.tree.insert(
            '',
            'end',
            iid=file_item.file_id,
            text=icon,
            values=values,
            tags=(tag,)
        )
    
    def _add_history_to_tree(self, entry: HistoryEntry):
        """이력 항목을 트리에 추가"""
        if not hasattr(self.view, 'tree'):
            return
            
        # 상태별 아이콘
        if entry.status == 'completed':
            icon = '✅'
            tag = 'success'
        elif entry.status == 'error':
            icon = '❌'
            tag = 'error'
        else:
            icon = '⚠️'
            tag = 'warning'
        
        # 날짜 포맷
        date_str = entry.processed_at.strftime('%Y-%m-%d %H:%M')
        
        # 문제 수
        total_issues = entry.error_count + entry.warning_count
        if total_issues > 0:
            issues_str = f"⚠️ {total_issues}"
        else:
            issues_str = "✅ 0"
        
        # 파일 크기
        size_mb = entry.file_size / (1024 * 1024) if entry.file_size else 0
        size_str = f"{size_mb:.1f} MB"
        
        # 처리 시간
        time_str = f"{entry.processing_time:.1f}초" if entry.processing_time else "-"
        
        values = (
            '이력',
            entry.status_text,
            entry.file_name,
            entry.profile_used or 'Default',
            size_str,
            '-',  # 페이지 수
            issues_str,
            '100%' if entry.status == 'completed' else '-',
            time_str,
            date_str
        )
        
        # 이력 항목은 다른 색상으로 표시
        self.view.tree.insert(
            '',
            'end',
            iid=f"history_{entry.id}",
            text=icon,
            values=values,
            tags=('history', tag)
        )
    
    def _should_show_realtime_item(self, file_item: FileItem) -> bool:
        """실시간 항목 표시 여부 확인"""
        # 상태 필터
        status_filter = self.view.filter_status.get()
        if status_filter == "history_only":
            return False
        elif status_filter != "all":
            if status_filter == "processing" and file_item.status != FileStatus.PROCESSING:
                return False
            elif status_filter == "waiting" and file_item.status != FileStatus.WAITING:
                return False
            elif status_filter == "completed" and file_item.status != FileStatus.COMPLETED:
                return False
            elif status_filter == "error" and file_item.status != FileStatus.ERROR:
                return False
        
        # 프로파일 필터
        profile_filter = self.view.profile_filter.get()
        if profile_filter != 'all' and file_item.profile != profile_filter:
            return False
        
        # 검색 필터
        search_term = self.view.search_var.get().lower()
        if search_term and search_term not in file_item.filename.lower():
            return False
        
        return True
    
    def _should_show_history_item(self, entry: HistoryEntry) -> bool:
        """이력 항목 표시 여부 확인"""
        # 상태 필터
        status_filter = self.view.filter_status.get()
        if status_filter in ["processing", "waiting"]:
            return False
        
        # 프로파일 필터는 이미 데이터 가져올 때 적용됨
        # 검색 필터도 이미 적용됨
        
        return True
    
    def _calculate_date_range(self) -> Optional[Tuple[datetime, datetime]]:
        """날짜 범위 계산"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_range_value = self.view.date_range.get()
        
        if date_range_value == 'today':
            return (today, today + timedelta(days=1))
        elif date_range_value == 'week':
            start = today - timedelta(days=today.weekday())
            return (start, today + timedelta(days=1))
        elif date_range_value == 'month':
            start = today.replace(day=1)
            return (start, today + timedelta(days=1))
        else:  # all
            return None
    
    def _update_statistics(self, realtime_count: int, history_count: int):
        """통계 업데이트"""
        # 실시간 통계
        stats = self.view.controller.get_statistics()
        processing = stats.get('processing', 0)
        by_status = stats.get('by_status', {})
        waiting = by_status.get('waiting', 0)
        
        # 상태 요약
        summary_parts = []
        if realtime_count > 0:
            summary_parts.append(f"실시간: {realtime_count}개")
            if processing > 0:
                summary_parts.append(f"처리중: {processing}")
            if waiting > 0:
                summary_parts.append(f"대기: {waiting}")
        
        if history_count > 0:
            summary_parts.append(f"이력: {history_count}개")
        
        # 위젯 업데이트
        if 'status_summary_label' in self.view.widgets:
            self.view.widgets['status_summary_label'].configure(text=" | ".join(summary_parts))
        
        # 상세 통계
        stats_text = f"전체 {realtime_count + history_count}개 항목"
        if 'stats_label' in self.view.widgets:
            self.view.widgets['stats_label'].configure(text=stats_text)
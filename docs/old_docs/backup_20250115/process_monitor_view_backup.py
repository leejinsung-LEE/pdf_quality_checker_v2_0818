# src/ui/views/process_monitor_view.py
"""
통합 처리 모니터 뷰

실시간 처리 현황과 처리 이력을 한 화면에서 표시하는 통합 뷰입니다.
상단에는 현재 처리 중인 파일들을, 하단에는 처리 완료된 이력을 표시합니다.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Any, Set, Tuple
from pathlib import Path
from datetime import datetime, timedelta, date
import threading
import webbrowser
import os

from ..controllers import FileController, FileStatus, FileItem
from ...data import get_data_manager, HistoryEntry


class ProcessMonitorView(ctk.CTkFrame):
    """
    통합 처리 모니터 뷰 - 실시간 처리와 처리 이력을 통합 표시
    """
    
    # 상태별 아이콘
    STATUS_ICONS = {
        FileStatus.WAITING: '⏳',
        FileStatus.PROCESSING: '⚙️',
        FileStatus.COMPLETED: '✅',
        FileStatus.ERROR: '❌',
        FileStatus.CANCELLED: '🚫'
    }
    
    # 상태별 색상 태그
    STATUS_TAGS = {
        FileStatus.WAITING: 'waiting',
        FileStatus.PROCESSING: 'processing',
        FileStatus.COMPLETED: 'success',
        FileStatus.ERROR: 'error',
        FileStatus.CANCELLED: 'cancelled'
    }
    
    def __init__(self, parent, controller: FileController, **kwargs):
        """
        뷰 초기화
        
        Args:
            parent: 부모 위젯
            controller: 파일 컨트롤러
            **kwargs: 추가 옵션
        """
        super().__init__(parent, **kwargs)
        
        self.controller = controller
        self.data_manager = get_data_manager()
        
        # UI 상태 - 실시간 처리
        self.selected_items: Set[str] = set()
        self.filter_status = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.folder_filter = tk.StringVar(value="all")
        
        # UI 상태 - 처리 이력
        self.selected_history_ids: Set[int] = set()
        self.current_page = 1
        self.items_per_page = 100  # 성능을 위해 100개로 제한
        self.total_items = 0
        
        # 필터 변수 (통합)
        self.date_range = tk.StringVar(value="today")
        self.profile_filter = tk.StringVar(value="all")
        self.custom_start_date: Optional[date] = None
        self.custom_end_date: Optional[date] = None
        
        # 현재 표시 중인 데이터
        self.current_entries: List[HistoryEntry] = []
        
        # 색상 테마
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'bg_card': '#2a2a2a',
            'text_primary': '#ffffff',
            'text_secondary': '#b0b0b0',
            'accent': '#667eea',
            'success': '#28a745',
            'warning': '#ffc107',
            'error': '#dc3545',
            'info': '#17a2b8',
            'border': '#404040'
        }
        
        # 상하 분할 비율
        self.split_ratio = 0.6  # 상단 60%, 하단 40%
        
        # UI 생성
        self._create_ui()
        
        # 컨트롤러 콜백 설정
        self._setup_controller_callbacks()
        
        # 트리뷰 스타일 설정
        self._setup_tree_style()
        
        # 초기 데이터 로드
        self.refresh()
        self.refresh_history()
    
    def _create_ui(self):
        """UI 구성"""
        self.configure(fg_color=self.colors['bg_primary'])
        
        # 헤더
        header_frame = self._create_header()
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # 필터 영역
        filter_frame = self._create_filter_section()
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # PanedWindow로 상하 분할
        self.paned_window = tk.PanedWindow(
            self,
            orient='vertical',
            bg=self.colors['bg_primary'],
            sashwidth=8,
            sashrelief='flat',
            borderwidth=0
        )
        self.paned_window.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # 상단: 실시간 처리
        realtime_section = self._create_realtime_section()
        self.paned_window.add(realtime_section, minsize=200)
        
        # 하단: 처리 이력
        history_section = self._create_history_section()
        self.paned_window.add(history_section, minsize=150)
        
        # 초기 분할 비율 설정
        self.after(100, self._set_initial_sash_position)
    
    def _set_initial_sash_position(self):
        """초기 분할 위치 설정"""
        total_height = self.paned_window.winfo_height()
        if total_height > 100:
            position = int(total_height * self.split_ratio)
            self.paned_window.sash_place(0, 0, position)
    
    def _create_header(self) -> ctk.CTkFrame:
        """헤더 생성"""
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        
        # 제목
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            title_frame,
            text="📊 처리 모니터",
            font=('Arial', 24, 'bold')
        ).pack(side='left')
        
        ctk.CTkLabel(
            title_frame,
            text="실시간 처리 현황 및 처리 이력",
            font=('Arial', 12),
            text_color=self.colors['text_secondary']
        ).pack(side='left', padx=(20, 0))
        
        # 우측 버튼들
        button_frame = ctk.CTkFrame(header, fg_color="transparent")
        button_frame.pack(side='right', fill='y')
        
        # 기간 선택
        periods = [
            ("오늘", "today"),
            ("이번 주", "week"),
            ("이번 달", "month"),
            ("전체", "all")
        ]
        
        for text, value in periods:
            btn = ctk.CTkRadioButton(
                button_frame,
                text=text,
                variable=self.date_range,
                value=value,
                command=self._on_date_range_changed,
                width=80
            )
            btn.pack(side='left', padx=5)
        
        # 새로고침 버튼
        ctk.CTkButton(
            button_frame,
            text="🔄 새로고침",
            width=100,
            height=32,
            command=self.refresh_all
        ).pack(side='left', padx=(20, 0))
        
        # 내보내기 버튼
        ctk.CTkButton(
            button_frame,
            text="📄 내보내기",
            width=100,
            height=32,
            command=self.export_data,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=(10, 0))
        
        return header
    
    def _create_filter_section(self) -> ctk.CTkFrame:
        """필터 섹션 생성"""
        filter_container = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_card'],
            corner_radius=10,
            height=60
        )
        
        inner = ctk.CTkFrame(filter_container, fg_color="transparent")
        inner.pack(fill='both', expand=True, padx=20, pady=10)
        
        # 검색
        search_frame = ctk.CTkFrame(inner, fg_color="transparent")
        search_frame.pack(side='left', fill='y', padx=(0, 20))
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=('Arial', 16)
        ).pack(side='left', padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="파일명 검색...",
            textvariable=self.search_var,
            width=300
        )
        search_entry.pack(side='left')
        search_entry.bind('<Return>', lambda e: self.apply_filters())
        
        # 상태 필터
        status_frame = ctk.CTkFrame(inner, fg_color="transparent")
        status_frame.pack(side='left', fill='y', padx=(0, 20))
        
        ctk.CTkLabel(
            status_frame,
            text="상태:",
            font=('Arial', 12)
        ).pack(side='left', padx=(0, 5))
        
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.filter_status,
            values=["all", "waiting", "processing", "completed", "error"],
            command=lambda v: self.apply_filters(),
            width=120
        )
        status_menu.pack(side='left')
        
        # 프로파일 필터
        profile_frame = ctk.CTkFrame(inner, fg_color="transparent")
        profile_frame.pack(side='left', fill='y', padx=(0, 20))
        
        ctk.CTkLabel(
            profile_frame,
            text="프로파일:",
            font=('Arial', 12)
        ).pack(side='left', padx=(0, 5))
        
        # 프로파일 목록 가져오기
        profiles = ["all"] + list(self.controller.profile_manager.profiles.keys())
        
        profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.profile_filter,
            values=profiles,
            command=lambda v: self.apply_filters(),
            width=150
        )
        profile_menu.pack(side='left')
        
        # 필터 적용 버튼
        ctk.CTkButton(
            inner,
            text="필터 적용",
            width=100,
            height=32,
            command=self.apply_filters,
            fg_color=self.colors['accent']
        ).pack(side='right')
        
        # 필터 초기화 버튼
        ctk.CTkButton(
            inner,
            text="초기화",
            width=80,
            height=32,
            command=self.reset_filters,
            fg_color=self.colors['bg_secondary']
        ).pack(side='right', padx=(0, 10))
        
        return filter_container
    
    def _create_realtime_section(self) -> ctk.CTkFrame:
        """실시간 처리 섹션 생성"""
        section = ctk.CTkFrame(self, fg_color=self.colors['bg_card'], corner_radius=10)
        
        # 섹션 헤더
        header_frame = ctk.CTkFrame(section, fg_color="transparent", height=40)
        header_frame.pack(fill='x', padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="⚡ 실시간 처리",
            font=('Arial', 16, 'bold')
        ).pack(side='left')
        
        # 통계 표시
        self.realtime_stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.realtime_stats_label.pack(side='left', padx=(20, 0))
        
        # 액션 버튼들
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side='right')
        
        ctk.CTkButton(
            action_frame,
            text="➕ 파일 추가",
            width=100,
            height=28,
            command=self.add_files,
            fg_color=self.colors['success']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="⏸️ 일시정지",
            width=90,
            height=28,
            command=self.pause_processing,
            fg_color=self.colors['warning']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️ 지우기",
            width=80,
            height=28,
            command=self.clear_completed,
            fg_color=self.colors['error']
        ).pack(side='left', padx=2)
        
        # 트리뷰 프레임
        tree_frame = ctk.CTkFrame(section, fg_color="transparent")
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # 트리뷰 생성
        self.realtime_tree = self._create_treeview(tree_frame, 'realtime')
        
        return section
    
    def _create_history_section(self) -> ctk.CTkFrame:
        """처리 이력 섹션 생성"""
        section = ctk.CTkFrame(self, fg_color=self.colors['bg_card'], corner_radius=10)
        
        # 섹션 헤더
        header_frame = ctk.CTkFrame(section, fg_color="transparent", height=40)
        header_frame.pack(fill='x', padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 처리 이력",
            font=('Arial', 16, 'bold')
        ).pack(side='left')
        
        # 통계 표시
        self.history_stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.history_stats_label.pack(side='left', padx=(20, 0))
        
        # 액션 버튼들
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side='right')
        
        ctk.CTkButton(
            action_frame,
            text="📂 파일 열기",
            width=90,
            height=28,
            command=self.open_selected_file,
            fg_color=self.colors['info']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="📝 보고서",
            width=80,
            height=28,
            command=self.view_report,
            fg_color=self.colors['accent']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️ 삭제",
            width=70,
            height=28,
            command=self.delete_history,
            fg_color=self.colors['error']
        ).pack(side='left', padx=2)
        
        # 트리뷰 프레임
        tree_frame = ctk.CTkFrame(section, fg_color="transparent")
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # 트리뷰 생성
        self.history_tree = self._create_treeview(tree_frame, 'history')
        
        # 페이지네이션
        pagination_frame = ctk.CTkFrame(section, fg_color="transparent", height=40)
        pagination_frame.pack(fill='x', padx=15, pady=(0, 15))
        
        # 이전 페이지
        self.prev_btn = ctk.CTkButton(
            pagination_frame,
            text="◀ 이전",
            width=80,
            height=28,
            command=self.prev_page,
            state='disabled'
        )
        self.prev_btn.pack(side='left', padx=5)
        
        # 페이지 정보
        self.page_label = ctk.CTkLabel(
            pagination_frame,
            text="1 / 1",
            font=('Arial', 12)
        )
        self.page_label.pack(side='left', padx=20)
        
        # 다음 페이지
        self.next_btn = ctk.CTkButton(
            pagination_frame,
            text="다음 ▶",
            width=80,
            height=28,
            command=self.next_page,
            state='disabled'
        )
        self.next_btn.pack(side='left', padx=5)
        
        # 더 보기 버튼
        ctk.CTkButton(
            pagination_frame,
            text="더 보기 (100개)",
            width=120,
            height=28,
            command=self.load_more,
            fg_color=self.colors['bg_secondary']
        ).pack(side='right', padx=5)
        
        return section
    
    def _create_treeview(self, parent, tree_type: str) -> ttk.Treeview:
        """트리뷰 생성"""
        # 스크롤바
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side='right', fill='y')
        
        # 컬럼 정의
        if tree_type == 'realtime':
            columns = ('status', 'filename', 'profile', 'size', 'issues', 'progress', 'time')
            headings = {
                'status': '상태',
                'filename': '파일명',
                'profile': '프로파일',
                'size': '크기',
                'issues': '문제',
                'progress': '진행률',
                'time': '시간'
            }
        else:  # history
            columns = ('date', 'filename', 'profile', 'status', 'issues', 'score', 'time')
            headings = {
                'date': '처리일시',
                'filename': '파일명',
                'profile': '프로파일',
                'status': '결과',
                'issues': '문제',
                'score': '점수',
                'time': '소요시간'
            }
        
        # 트리뷰 생성
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='tree headings',
            selectmode='extended',
            height=8
        )
        tree.pack(side='left', fill='both', expand=True)
        
        # 스크롤바 연결
        scrollbar.config(command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)
        
        # 컬럼 설정
        tree.column('#0', width=50, stretch=False)  # 아이콘
        tree.heading('#0', text='')
        
        for col, heading in headings.items():
            if col == 'filename':
                tree.column(col, width=300, stretch=True)
            elif col in ['status', 'progress', 'score']:
                tree.column(col, width=100, stretch=False)
            elif col == 'date':
                tree.column(col, width=150, stretch=False)
            else:
                tree.column(col, width=120, stretch=False)
            tree.heading(col, text=heading)
        
        # 이벤트 바인딩
        if tree_type == 'realtime':
            tree.bind('<Double-Button-1>', self._on_realtime_double_click)
            tree.bind('<<TreeviewSelect>>', self._on_realtime_selection)
        else:
            tree.bind('<Double-Button-1>', self._on_history_double_click)
            tree.bind('<<TreeviewSelect>>', self._on_history_selection)
        
        return tree
    
    def _setup_tree_style(self):
        """트리뷰 스타일 설정"""
        style = ttk.Style()
        
        # 색상 설정
        style.configure("Treeview",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=0)
        style.map('Treeview',
                 background=[('selected', self.colors['accent'])])
        
        # 헤더 스타일
        style.configure("Treeview.Heading",
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0)
        style.map("Treeview.Heading",
                 background=[('active', self.colors['accent'])])
        
        # 태그 색상
        self.realtime_tree.tag_configure('waiting', foreground='#ffc107')
        self.realtime_tree.tag_configure('processing', foreground='#17a2b8')
        self.realtime_tree.tag_configure('success', foreground='#28a745')
        self.realtime_tree.tag_configure('error', foreground='#dc3545')
        self.realtime_tree.tag_configure('cancelled', foreground='#6c757d')
        
        self.history_tree.tag_configure('success', foreground='#28a745')
        self.history_tree.tag_configure('error', foreground='#dc3545')
        self.history_tree.tag_configure('warning', foreground='#ffc107')
    
    def _setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        # 파일 추가 콜백
        self.controller.on_file_added = self._on_file_added
        # 상태 변경 콜백
        self.controller.on_status_changed = self._on_status_changed
        # 진행률 업데이트 콜백
        self.controller.on_progress_updated = self._on_progress_updated
        # 파일 제거 콜백
        self.controller.on_file_removed = self._on_file_removed
    
    # === 실시간 처리 메서드 ===
    
    def _on_file_added(self, file_item: FileItem):
        """파일 추가 이벤트 처리"""
        self._add_file_to_tree(file_item)
        self._update_realtime_stats()
    
    def _on_status_changed(self, file_id: str, status: FileStatus):
        """상태 변경 이벤트 처리"""
        if file_id in self.controller.file_items:
            file_item = self.controller.file_items[file_id]
            self._update_file_in_tree(file_item)
            
            # 완료된 경우 이력에도 추가
            if status in [FileStatus.COMPLETED, FileStatus.ERROR]:
                self.refresh_history()
        self._update_realtime_stats()
    
    def _on_progress_updated(self, file_id: str, progress: int):
        """진행률 업데이트 이벤트 처리"""
        if file_id in self.controller.file_items:
            file_item = self.controller.file_items[file_id]
            self._update_file_in_tree(file_item)
    
    def _on_file_removed(self, file_id: str):
        """파일 제거 이벤트 처리"""
        try:
            self.realtime_tree.delete(file_id)
        except:
            pass
        self._update_realtime_stats()
    
    def _add_file_to_tree(self, file_item: FileItem):
        """트리뷰에 파일 추가"""
        # 아이콘
        icon = self.STATUS_ICONS.get(file_item.status, '')
        
        # 파일 크기
        size_mb = file_item.size_mb
        size_str = f"{size_mb:.1f} MB"
        
        # 문제 수
        issues = file_item.error_count + file_item.warning_count
        issues_str = f"⚠️ {issues}" if issues > 0 else "✅ 0"
        
        # 진행률
        progress_str = f"{file_item.progress}%" if file_item.status == FileStatus.PROCESSING else "-"
        
        # 처리 시간
        if file_item.processing_time > 0:
            time_str = f"{file_item.processing_time:.1f}초"
        else:
            time_str = "-"
        
        # 태그
        tag = self.STATUS_TAGS.get(file_item.status, '')
        
        # 트리에 추가
        values = (
            file_item.status.value,
            file_item.filename,
            file_item.profile or 'Default',
            size_str,
            issues_str,
            progress_str,
            time_str
        )
        
        try:
            self.realtime_tree.insert(
                '',
                'end',
                iid=file_item.file_id,
                text=icon,
                values=values,
                tags=(tag,)
            )
        except:
            # 이미 존재하는 경우 업데이트
            self._update_file_in_tree(file_item)
    
    def _update_file_in_tree(self, file_item: FileItem):
        """트리뷰의 파일 정보 업데이트"""
        try:
            # 아이콘
            icon = self.STATUS_ICONS.get(file_item.status, '')
            
            # 문제 수
            issues = file_item.error_count + file_item.warning_count
            issues_str = f"⚠️ {issues}" if issues > 0 else "✅ 0"
            
            # 진행률
            progress_str = f"{file_item.progress}%" if file_item.status == FileStatus.PROCESSING else "-"
            
            # 처리 시간
            if file_item.processing_time > 0:
                time_str = f"{file_item.processing_time:.1f}초"
            else:
                time_str = "-"
            
            # 파일 크기
            size_mb = file_item.size_mb
            size_str = f"{size_mb:.1f} MB"
            
            # 태그
            tag = self.STATUS_TAGS.get(file_item.status, '')
            
            values = (
                file_item.status.value,
                file_item.filename,
                file_item.profile or 'Default',
                size_str,
                issues_str,
                progress_str,
                time_str
            )
            
            self.realtime_tree.item(
                file_item.file_id,
                text=icon,
                values=values,
                tags=(tag,)
            )
        except:
            pass
    
    def _update_realtime_stats(self):
        """실시간 처리 통계 업데이트"""
        stats = self.controller.get_statistics()
        
        total = stats['total']
        processing = stats.get('processing', 0)
        
        # by_status에서 상태별 카운트 가져오기
        by_status = stats.get('by_status', {})
        completed = by_status.get('completed', 0)
        errors = by_status.get('error', 0)
        waiting = by_status.get('waiting', 0)
        
        stats_text = f"전체: {total} | 대기: {waiting} | 처리중: {processing} | 완료: {completed} | 오류: {errors}"
        self.realtime_stats_label.configure(text=stats_text)
    
    def _on_realtime_double_click(self, event):
        """실시간 트리 더블클릭 이벤트"""
        selection = self.realtime_tree.selection()
        if selection:
            file_id = selection[0]
            if file_id in self.controller.file_items:
                file_item = self.controller.file_items[file_id]
                self._show_file_details(file_item)
    
    def _on_realtime_selection(self, event):
        """실시간 트리 선택 이벤트"""
        self.selected_items = set(self.realtime_tree.selection())
    
    # === 처리 이력 메서드 ===
    
    def refresh_history(self):
        """처리 이력 새로고침"""
        # 날짜 범위 계산
        date_range = self._calculate_date_range()
        
        # 필터 조건
        filters = {
            'date_range': date_range,
            'status': self.filter_status.get() if self.filter_status.get() != 'all' else None,
            'profile': self.profile_filter.get() if self.profile_filter.get() != 'all' else None,
            'search': self.search_var.get() if self.search_var.get() else None
        }
        
        # 데이터 가져오기
        offset = (self.current_page - 1) * self.items_per_page
        entries = self.data_manager.get_history(
            limit=self.items_per_page,
            offset=offset,
            start_date=filters.get('date_range', (None, None))[0] if filters.get('date_range') else None,
            end_date=filters.get('date_range', (None, None))[1] if filters.get('date_range') else None,
            filename_filter=filters.get('search'),
            status_filter=filters.get('status'),
            profile_filter=filters.get('profile')
        )
        
        # 전체 개수 가져오기
        total = self.data_manager.get_history_count(
            start_date=filters.get('date_range', (None, None))[0] if filters.get('date_range') else None,
            end_date=filters.get('date_range', (None, None))[1] if filters.get('date_range') else None,
            filename_filter=filters.get('search'),
            status_filter=filters.get('status'),
            profile_filter=filters.get('profile')
        )
        
        self.current_entries = entries
        self.total_items = total
        
        # 트리 초기화
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # 데이터 추가
        for entry in entries:
            self._add_history_to_tree(entry)
        
        # 통계 및 페이지네이션 업데이트
        self._update_history_stats()
        self._update_pagination()
    
    def _add_history_to_tree(self, entry: HistoryEntry):
        """이력 트리에 항목 추가"""
        # 상태 아이콘
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
        
        # 점수
        score_str = f"{entry.quality_score:.0f}%" if entry.quality_score else "-"
        
        # 처리 시간
        time_str = f"{entry.processing_time:.1f}초" if entry.processing_time else "-"
        
        values = (
            date_str,
            entry.file_name,
            entry.profile_used or 'Default',
            entry.status,
            issues_str,
            score_str,
            time_str
        )
        
        self.history_tree.insert(
            '',
            'end',
            iid=str(entry.id),
            text=icon,
            values=values,
            tags=(tag,)
        )
    
    def _update_history_stats(self):
        """처리 이력 통계 업데이트"""
        if self.total_items > 0:
            stats_text = f"총 {self.total_items}개 기록"
            
            # 현재 페이지 범위
            start = (self.current_page - 1) * self.items_per_page + 1
            end = min(start + len(self.current_entries) - 1, self.total_items)
            stats_text += f" ({start}-{end}번째 표시중)"
        else:
            stats_text = "처리 이력 없음"
        
        self.history_stats_label.configure(text=stats_text)
    
    def _update_pagination(self):
        """페이지네이션 업데이트"""
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        total_pages = max(1, total_pages)
        
        # 페이지 라벨
        self.page_label.configure(text=f"{self.current_page} / {total_pages}")
        
        # 버튼 상태
        self.prev_btn.configure(state='normal' if self.current_page > 1 else 'disabled')
        self.next_btn.configure(state='normal' if self.current_page < total_pages else 'disabled')
    
    def _on_history_double_click(self, event):
        """이력 트리 더블클릭 이벤트"""
        selection = self.history_tree.selection()
        if selection:
            entry_id = int(selection[0])
            entry = next((e for e in self.current_entries if e.id == entry_id), None)
            if entry:
                self.view_report_for_entry(entry)
    
    def _on_history_selection(self, event):
        """이력 트리 선택 이벤트"""
        self.selected_history_ids = set(int(id) for id in self.history_tree.selection())
    
    # === 공통 메서드 ===
    
    def _calculate_date_range(self) -> Optional[Tuple[datetime, datetime]]:
        """날짜 범위 계산"""
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        date_range_value = self.date_range.get()
        
        if date_range_value == 'today':
            return (today, today + timedelta(days=1))
        elif date_range_value == 'week':
            start = today - timedelta(days=today.weekday())
            return (start, today + timedelta(days=1))
        elif date_range_value == 'month':
            start = today.replace(day=1)
            return (start, today + timedelta(days=1))
        elif date_range_value == 'custom' and self.custom_start_date and self.custom_end_date:
            start = datetime.combine(self.custom_start_date, datetime.min.time())
            end = datetime.combine(self.custom_end_date, datetime.max.time())
            return (start, end)
        else:  # all
            return None
    
    def _on_date_range_changed(self):
        """날짜 범위 변경 이벤트"""
        if self.date_range.get() == 'custom':
            # 커스텀 날짜 선택 다이얼로그 표시
            self._show_custom_date_dialog()
        else:
            self.refresh_history()
    
    def _show_custom_date_dialog(self):
        """커스텀 날짜 선택 다이얼로그"""
        # TODO: 날짜 선택 다이얼로그 구현
        pass
    
    def _show_file_details(self, file_item: FileItem):
        """파일 상세 정보 표시"""
        # TODO: 상세 정보 다이얼로그 구현
        pass
    
    def apply_filters(self):
        """필터 적용"""
        self.refresh()
        self.refresh_history()
    
    def reset_filters(self):
        """필터 초기화"""
        self.search_var.set("")
        self.filter_status.set("all")
        self.profile_filter.set("all")
        self.date_range.set("today")
        self.apply_filters()
    
    def refresh(self):
        """실시간 처리 새로고침"""
        # 트리 초기화
        for item in self.realtime_tree.get_children():
            self.realtime_tree.delete(item)
        
        # 현재 파일들 추가
        for file_item in self.controller.file_items.values():
            # 필터 적용
            if self._should_show_file(file_item):
                self._add_file_to_tree(file_item)
        
        self._update_realtime_stats()
    
    def refresh_all(self):
        """전체 새로고침"""
        self.refresh()
        self.refresh_history()
    
    def _should_show_file(self, file_item: FileItem) -> bool:
        """파일 표시 여부 확인"""
        # 상태 필터
        status_filter = self.filter_status.get()
        if status_filter != 'all':
            if status_filter == 'waiting' and file_item.status != FileStatus.WAITING:
                return False
            elif status_filter == 'processing' and file_item.status != FileStatus.PROCESSING:
                return False
            elif status_filter == 'completed' and file_item.status != FileStatus.COMPLETED:
                return False
            elif status_filter == 'error' and file_item.status != FileStatus.ERROR:
                return False
        
        # 프로파일 필터
        profile_filter = self.profile_filter.get()
        if profile_filter != 'all' and file_item.profile != profile_filter:
            return False
        
        # 검색 필터
        search_term = self.search_var.get().lower()
        if search_term and search_term not in file_item.filename.lower():
            return False
        
        return True
    
    # === 액션 메서드 ===
    
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            for file_path in files:
                self.controller.add_file(file_path)
    
    def pause_processing(self):
        """처리 일시정지/재개"""
        if self.controller.is_paused:
            self.controller.resume_processing()
            messagebox.showinfo("재개", "처리가 재개되었습니다.")
        else:
            self.controller.pause_processing()
            messagebox.showinfo("일시정지", "처리가 일시정지되었습니다.")
    
    def clear_completed(self):
        """완료된 항목 제거"""
        completed_ids = [
            file_id for file_id, file_item in self.controller.file_items.items()
            if file_item.status in [FileStatus.COMPLETED, FileStatus.ERROR, FileStatus.CANCELLED]
        ]
        
        for file_id in completed_ids:
            self.controller.remove_file(file_id)
    
    def open_selected_file(self):
        """선택된 파일 열기"""
        if self.selected_history_ids:
            entry_id = list(self.selected_history_ids)[0]
            entry = next((e for e in self.current_entries if e.id == entry_id), None)
            if entry and os.path.exists(entry.file_path):
                os.startfile(entry.file_path)
    
    def view_report(self):
        """선택된 항목의 보고서 보기"""
        if self.selected_history_ids:
            entry_id = list(self.selected_history_ids)[0]
            entry = next((e for e in self.current_entries if e.id == entry_id), None)
            if entry:
                self.view_report_for_entry(entry)
    
    def view_report_for_entry(self, entry: HistoryEntry):
        """특정 이력의 보고서 보기"""
        if entry.report_path and os.path.exists(entry.report_path):
            webbrowser.open(entry.report_path)
        else:
            messagebox.showwarning("보고서 없음", "해당 파일의 보고서를 찾을 수 없습니다.")
    
    def delete_history(self):
        """선택된 이력 삭제"""
        if not self.selected_history_ids:
            return
        
        if messagebox.askyesno("삭제 확인", f"{len(self.selected_history_ids)}개의 이력을 삭제하시겠습니까?"):
            for entry_id in self.selected_history_ids:
                self.data_manager.delete_history(entry_id)
            self.refresh_history()
    
    def export_data(self):
        """데이터 내보내기"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("JSON 파일", "*.json"), ("모든 파일", "*.*")],
            initialfile=f"process_monitor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            # TODO: 데이터 내보내기 구현
            messagebox.showinfo("내보내기", f"데이터를 {filename}로 내보냈습니다.")
    
    def load_more(self):
        """더 많은 이력 로드"""
        self.items_per_page += 100
        self.refresh_history()
    
    def prev_page(self):
        """이전 페이지"""
        if self.current_page > 1:
            self.current_page -= 1
            self.refresh_history()
    
    def next_page(self):
        """다음 페이지"""
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.refresh_history()
"""
Process Monitor View UI 빌더 모듈
기능: UI 컴포넌트 생성 및 레이아웃 구성
의존성: customtkinter, tkinter.ttk
최종 수정: 2025-01-11
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import ProcessMonitorView


class UIBuilder:
    """UI 생성 헬퍼 클래스"""
    
    def __init__(self, view: 'ProcessMonitorView'):
        """
        초기화
        
        Args:
            view: ProcessMonitorView 인스턴스
        """
        self.view = view
    
    def create_ui(self):
        """전체 UI 생성"""
        # 메인 컨테이너
        main_container = ctk.CTkFrame(
            self.view,
            fg_color=self.view.colors['bg_primary']
        )
        main_container.pack(fill='both', expand=True)
        
        # 헤더
        self.view.header_frame = self._create_header(main_container)
        self.view.header_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # 필터 섹션
        self.view.filter_frame = self._create_filter_section(main_container)
        self.view.filter_frame.pack(fill='x', padx=10, pady=5)
        
        # PanedWindow로 상하 분할
        self.view.paned_window = tk.PanedWindow(
            main_container,
            orient=tk.VERTICAL,
            bg=self.view.colors['bg_primary'],
            sashwidth=8,
            sashrelief=tk.FLAT,
            borderwidth=0
        )
        self.view.paned_window.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 실시간 처리 섹션 (상단)
        realtime_section = self._create_realtime_section()
        self.view.paned_window.add(realtime_section, stretch="always")
        
        # 처리 이력 섹션 (하단)
        history_section = self._create_history_section()
        self.view.paned_window.add(history_section, stretch="always")
        
        # 초기 sash 위치 설정
        self.view.after(100, self._set_initial_sash_position)
        
        # 스타일 설정
        self._setup_tree_style()
    
    def _create_header(self, parent) -> ctk.CTkFrame:
        """헤더 생성"""
        header = ctk.CTkFrame(parent, fg_color='transparent', height=50)
        
        # 제목
        title_label = ctk.CTkLabel(
            header,
            text="📊 통합 처리 모니터",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.view.colors['text_primary']
        )
        title_label.pack(side='left', padx=10)
        
        # 액션 버튼들
        action_frame = ctk.CTkFrame(header, fg_color='transparent')
        action_frame.pack(side='right', padx=10)
        
        # 파일 추가 버튼
        add_btn = ctk.CTkButton(
            action_frame,
            text="📁 파일 추가",
            command=self.view.action_handler.add_files,
            width=100,
            height=32,
            fg_color=self.view.colors['accent']
        )
        add_btn.pack(side='left', padx=5)
        
        # 일시정지/재개 버튼
        pause_btn = ctk.CTkButton(
            action_frame,
            text="⏸️ 일시정지",
            command=self.view.action_handler.pause_processing,
            width=100,
            height=32,
            fg_color=self.view.colors['warning']
        )
        pause_btn.pack(side='left', padx=5)
        
        # 완료 항목 제거 버튼
        clear_btn = ctk.CTkButton(
            action_frame,
            text="🧹 완료 제거",
            command=self.view.action_handler.clear_completed,
            width=100,
            height=32,
            fg_color=self.view.colors['bg_card']
        )
        clear_btn.pack(side='left', padx=5)
        
        return header
    
    def _create_filter_section(self, parent) -> ctk.CTkFrame:
        """필터 섹션 생성"""
        filter_frame = ctk.CTkFrame(
            parent,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10,
            height=60
        )
        
        # 검색 필드
        search_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        search_frame.pack(side='left', padx=10, pady=10)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=ctk.CTkFont(size=16)
        ).pack(side='left', padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.view.search_var,
            placeholder_text="파일명 검색...",
            width=200
        )
        search_entry.pack(side='left')
        
        # 상태 필터
        status_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        status_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(
            status_frame,
            text="상태:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 5))
        
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.view.filter_status,
            values=["all", "waiting", "processing", "completed", "error"],
            command=lambda _: self.view.event_handler.apply_filters(),
            width=120
        )
        status_menu.pack(side='left')
        
        # 날짜 범위 필터
        date_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        date_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(
            date_frame,
            text="기간:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 5))
        
        date_menu = ctk.CTkOptionMenu(
            date_frame,
            variable=self.view.date_range,
            values=["today", "week", "month", "all", "custom"],
            command=lambda _: self.view.event_handler.on_date_range_changed(),
            width=100
        )
        date_menu.pack(side='left')
        
        # 프로파일 필터
        profile_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        profile_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(
            profile_frame,
            text="프로파일:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 5))
        
        profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.view.profile_filter,
            values=["all", "default", "strict", "custom"],
            command=lambda _: self.view.event_handler.apply_filters(),
            width=100
        )
        profile_menu.pack(side='left')
        
        # 필터 버튼들
        button_frame = ctk.CTkFrame(filter_frame, fg_color='transparent')
        button_frame.pack(side='right', padx=10)
        
        apply_btn = ctk.CTkButton(
            button_frame,
            text="적용",
            command=self.view.event_handler.apply_filters,
            width=60,
            height=28
        )
        apply_btn.pack(side='left', padx=2)
        
        reset_btn = ctk.CTkButton(
            button_frame,
            text="초기화",
            command=self.view.event_handler.reset_filters,
            width=60,
            height=28,
            fg_color=self.view.colors['bg_secondary']
        )
        reset_btn.pack(side='left', padx=2)
        
        return filter_frame
    
    def _create_realtime_section(self) -> ctk.CTkFrame:
        """실시간 처리 섹션 생성"""
        section = ctk.CTkFrame(
            self.view.paned_window,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10
        )
        
        # 섹션 헤더
        header = ctk.CTkFrame(section, fg_color='transparent', height=40)
        header.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="⚡ 실시간 처리",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.view.colors['text_primary']
        ).pack(side='left')
        
        self.view.realtime_stats_label = ctk.CTkLabel(
            header,
            text="",
            text_color=self.view.colors['text_secondary']
        )
        self.view.realtime_stats_label.pack(side='right')
        
        # 트리뷰
        tree_frame = ctk.CTkFrame(section, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.view.realtime_tree = self._create_treeview(tree_frame, 'realtime')
        
        return section
    
    def _create_history_section(self) -> ctk.CTkFrame:
        """처리 이력 섹션 생성"""
        section = ctk.CTkFrame(
            self.view.paned_window,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10
        )
        
        # 섹션 헤더
        header = ctk.CTkFrame(section, fg_color='transparent', height=40)
        header.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header,
            text="📋 처리 이력",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.view.colors['text_primary']
        ).pack(side='left')
        
        self.view.history_stats_label = ctk.CTkLabel(
            header,
            text="",
            text_color=self.view.colors['text_secondary']
        )
        self.view.history_stats_label.pack(side='right')
        
        # 트리뷰
        tree_frame = ctk.CTkFrame(section, fg_color='transparent')
        tree_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.view.history_tree = self._create_treeview(tree_frame, 'history')
        
        # 페이지네이션
        self._create_pagination(section)
        
        return section
    
    def _create_treeview(self, parent, tree_type: str) -> ttk.Treeview:
        """트리뷰 생성"""
        # 컬럼 정의
        if tree_type == 'realtime':
            columns = ('status', 'filename', 'profile', 'progress', 'time', 'message')
        else:  # history
            columns = ('date', 'filename', 'profile', 'pages', 'errors', 'warnings', 'score')
        
        # 트리뷰 생성
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='tree headings',
            selectmode='extended'
        )
        
        # 컬럼 설정
        tree.heading('#0', text='', anchor='w')
        tree.column('#0', width=30, stretch=False)
        
        if tree_type == 'realtime':
            self._setup_realtime_columns(tree)
        else:
            self._setup_history_columns(tree)
        
        # 스크롤바
        vsb = ttk.Scrollbar(parent, orient='vertical', command=tree.yview)
        hsb = ttk.Scrollbar(parent, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 배치
        tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        
        # 이벤트 바인딩
        if tree_type == 'realtime':
            tree.bind('<Double-Button-1>', self.view.event_handler.on_realtime_double_click)
            tree.bind('<<TreeviewSelect>>', self.view.event_handler.on_realtime_selection)
        else:
            tree.bind('<Double-Button-1>', self.view.event_handler.on_history_double_click)
            tree.bind('<<TreeviewSelect>>', self.view.event_handler.on_history_selection)
        
        return tree
    
    def _setup_realtime_columns(self, tree):
        """실시간 트리 컬럼 설정"""
        tree.heading('status', text='상태')
        tree.heading('filename', text='파일명')
        tree.heading('profile', text='프로파일')
        tree.heading('progress', text='진행률')
        tree.heading('time', text='시작 시간')
        tree.heading('message', text='메시지')
        
        tree.column('status', width=60, anchor='center')
        tree.column('filename', width=250)
        tree.column('profile', width=100)
        tree.column('progress', width=100)
        tree.column('time', width=100)
        tree.column('message', width=200)
    
    def _setup_history_columns(self, tree):
        """이력 트리 컬럼 설정"""
        tree.heading('date', text='처리일시')
        tree.heading('filename', text='파일명')
        tree.heading('profile', text='프로파일')
        tree.heading('pages', text='페이지')
        tree.heading('errors', text='오류')
        tree.heading('warnings', text='경고')
        tree.heading('score', text='점수')
        
        tree.column('date', width=150)
        tree.column('filename', width=250)
        tree.column('profile', width=100)
        tree.column('pages', width=80, anchor='center')
        tree.column('errors', width=80, anchor='center')
        tree.column('warnings', width=80, anchor='center')
        tree.column('score', width=80, anchor='center')
    
    def _create_pagination(self, parent):
        """페이지네이션 컨트롤 생성"""
        pagination_frame = ctk.CTkFrame(parent, fg_color='transparent', height=40)
        pagination_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # 이전 페이지
        ctk.CTkButton(
            pagination_frame,
            text="◀",
            command=self.view.action_handler.prev_page,
            width=30,
            height=30
        ).pack(side='left', padx=5)
        
        # 페이지 정보
        self.view.page_label = ctk.CTkLabel(
            pagination_frame,
            text="페이지 1",
            text_color=self.view.colors['text_secondary']
        )
        self.view.page_label.pack(side='left', padx=10)
        
        # 다음 페이지
        ctk.CTkButton(
            pagination_frame,
            text="▶",
            command=self.view.action_handler.next_page,
            width=30,
            height=30
        ).pack(side='left', padx=5)
        
        # 데이터 내보내기
        ctk.CTkButton(
            pagination_frame,
            text="📥 내보내기",
            command=self.view.action_handler.export_data,
            width=80,
            height=30
        ).pack(side='right', padx=5)
    
    def _set_initial_sash_position(self):
        """초기 sash 위치 설정"""
        try:
            total_height = self.view.paned_window.winfo_height()
            sash_position = int(total_height * self.view.split_ratio)
            self.view.paned_window.sash_place(0, 0, sash_position)
        except:
            pass
    
    def _setup_tree_style(self):
        """트리뷰 스타일 설정"""
        style = ttk.Style()
        
        # 테마 설정
        style.theme_use('clam')
        
        # 트리뷰 스타일
        style.configure(
            "Treeview",
            background=self.view.colors['bg_secondary'],
            foreground=self.view.colors['text_primary'],
            fieldbackground=self.view.colors['bg_secondary'],
            borderwidth=0
        )
        
        style.configure(
            "Treeview.Heading",
            background=self.view.colors['bg_card'],
            foreground=self.view.colors['text_primary'],
            relief='flat'
        )
        
        style.map(
            "Treeview",
            background=[('selected', self.view.colors['accent'])],
            foreground=[('selected', 'white')]
        )
        
        # 상태별 태그 스타일
        for status, tag in self.view.STATUS_TAGS.items():
            color = self._get_status_color(status)
            self.view.realtime_tree.tag_configure(tag, foreground=color) if hasattr(self.view, 'realtime_tree') else None
    
    def _get_status_color(self, status):
        """상태별 색상 반환"""
        color_map = {
            'waiting': self.view.colors['text_secondary'],
            'processing': self.view.colors['info'],
            'success': self.view.colors['success'],
            'error': self.view.colors['error'],
            'cancelled': self.view.colors['warning']
        }
        return color_map.get(status, self.view.colors['text_primary'])
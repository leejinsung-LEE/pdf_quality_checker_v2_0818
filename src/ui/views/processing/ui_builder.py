"""
UI Builder 헬퍼 클래스
기능: 처리 화면의 UI 컴포넌트 생성 및 스타일 설정
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import ProcessingView


class UIBuilder:
    """
    UI 생성 및 관리 헬퍼
    
    역할:
    - UI 컴포넌트 생성
    - 레이아웃 구성
    - 스타일 설정
    """
    
    def __init__(self, view: 'ProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def create_ui(self):
        """전체 UI 구성"""
        # 메인 컨테이너
        self.view.configure(fg_color=self.view.colors['bg_primary'])
        
        # 상단 툴바
        toolbar_frame = self._create_toolbar()
        toolbar_frame.pack(fill='x', padx=10, pady=(10, 0))
        
        # 필터 바
        filter_frame = self._create_filter_bar()
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        # 파일 리스트
        list_frame = self._create_file_list()
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 하단 정보 바
        info_frame = self._create_info_bar()
        info_frame.pack(fill='x', padx=10, pady=(0, 10))
    
    def _create_toolbar(self) -> ctk.CTkFrame:
        """상단 툴바 생성"""
        toolbar = ctk.CTkFrame(self.view, fg_color=self.view.colors['bg_card'], height=50)
        
        # 왼쪽 버튼들
        left_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_frame.pack(side='left', fill='y', padx=10)
        
        # 파일 추가
        ctk.CTkButton(
            left_frame,
            text="📁 파일 추가",
            command=lambda: self.view.event_handler.add_files(),
            width=100,
            height=32
        ).pack(side='left', padx=(0, 5))
        
        # 폴더 추가
        ctk.CTkButton(
            left_frame,
            text="📂 폴더 추가",
            command=lambda: self.view.event_handler.add_folder(),
            width=100,
            height=32
        ).pack(side='left', padx=5)
        
        # 구분선
        separator = ctk.CTkFrame(left_frame, width=2, fg_color=self.view.colors['border'])
        separator.pack(side='left', fill='y', padx=10)
        
        # 일괄 작업
        ctk.CTkButton(
            left_frame,
            text="🔄 재처리",
            command=lambda: self.view.event_handler.retry_selected(),
            width=80,
            height=32,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=(0, 5))
        
        ctk.CTkButton(
            left_frame,
            text="🚫 취소",
            command=lambda: self.view.event_handler.cancel_selected(),
            width=80,
            height=32,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            left_frame,
            text="🗑️ 제거",
            command=lambda: self.view.event_handler.remove_selected(),
            width=80,
            height=32,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # 오른쪽 정보
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.pack(side='right', fill='y', padx=10)
        
        # 통계 정보
        stats_label = ctk.CTkLabel(
            right_frame,
            text="대기: 0 | 처리중: 0 | 완료: 0",
            font=('Arial', 12)
        )
        stats_label.pack(side='right')
        self.view.widgets['stats_label'] = stats_label
        
        return toolbar
    
    def _create_filter_bar(self) -> ctk.CTkFrame:
        """필터 바 생성"""
        filter_bar = ctk.CTkFrame(self.view, fg_color=self.view.colors['bg_card'], height=40)
        
        # 상태 필터
        status_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        status_frame.pack(side='left', padx=10)
        
        ctk.CTkLabel(status_frame, text="상태:").pack(side='left', padx=(0, 5))
        
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.view.filter_status,
            values=["all", "waiting", "processing", "completed", "error"],
            command=lambda v: self.view.file_list_manager.apply_filters(),
            width=120
        )
        status_menu.pack(side='left')
        
        # 검색
        search_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        search_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(search_frame, text="검색:").pack(side='left', padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.view.search_var,
            width=200
        )
        search_entry.pack(side='left')
        search_entry.bind('<KeyRelease>', lambda e: self.view.file_list_manager.apply_filters())
        
        # 폴더 필터
        folder_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        folder_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(folder_frame, text="폴더:").pack(side='left', padx=(0, 5))
        
        folder_menu = ctk.CTkOptionMenu(
            folder_frame,
            variable=self.view.folder_filter,
            values=["all"],
            command=lambda v: self.view.file_list_manager.apply_filters(),
            width=150
        )
        folder_menu.pack(side='left')
        self.view.widgets['folder_menu'] = folder_menu
        
        # 초기화 버튼
        ctk.CTkButton(
            filter_bar,
            text="🔄 초기화",
            command=lambda: self.view.file_list_manager.reset_filters(),
            width=80,
            height=28,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='right', padx=10)
        
        return filter_bar
    
    def _create_file_list(self) -> ctk.CTkFrame:
        """파일 리스트 생성"""
        list_frame = ctk.CTkFrame(self.view, fg_color=self.view.colors['bg_card'])
        
        # 트리뷰 컨테이너
        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 트리뷰 생성
        columns = ['icon', 'filename', 'folder', 'profile', 'size', 
                  'pages', 'issues', 'score', 'time', 'status']
        
        tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='tree headings',
            selectmode='extended'
        )
        
        # 컬럼 헤더 설정
        tree.heading('#0', text='☐', anchor='center')
        tree.heading('icon', text='')
        tree.heading('filename', text='파일명')
        tree.heading('folder', text='폴더')
        tree.heading('profile', text='프로파일')
        tree.heading('size', text='크기')
        tree.heading('pages', text='페이지')
        tree.heading('issues', text='문제')
        tree.heading('score', text='점수')
        tree.heading('time', text='처리시간')
        tree.heading('status', text='상태')
        
        # 컬럼 너비
        tree.column('#0', width=30, stretch=False)
        tree.column('icon', width=30, stretch=False)
        tree.column('filename', width=250)
        tree.column('folder', width=120)
        tree.column('profile', width=80)
        tree.column('size', width=80)
        tree.column('pages', width=60)
        tree.column('issues', width=100)
        tree.column('score', width=60)
        tree.column('time', width=100)
        tree.column('status', width=100)
        
        # 스크롤바
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 배치
        tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # 이벤트 바인딩
        tree.bind('<Double-Button-1>', lambda e: self.view.event_handler.on_double_click(e))
        tree.bind('<Button-3>', lambda e: self.view.event_handler.show_context_menu(e))
        tree.bind('<Button-1>', lambda e: self.view.event_handler.on_tree_click(e))
        
        # 트리뷰를 뷰에 저장
        self.view.tree = tree
        
        # 컨텍스트 메뉴
        self._create_context_menu()
        
        return list_frame
    
    def _create_info_bar(self) -> ctk.CTkFrame:
        """하단 정보 바 생성"""
        info_bar = ctk.CTkFrame(self.view, fg_color=self.view.colors['bg_card'], height=40)
        
        # 선택 정보
        selection_label = ctk.CTkLabel(
            info_bar,
            text="선택: 0개",
            font=('Arial', 11)
        )
        selection_label.pack(side='left', padx=10)
        self.view.widgets['selection_label'] = selection_label
        
        # 처리 정보
        process_info_label = ctk.CTkLabel(
            info_bar,
            text="",
            font=('Arial', 11),
            text_color=self.view.colors['text_secondary']
        )
        process_info_label.pack(side='right', padx=10)
        self.view.widgets['process_info_label'] = process_info_label
        
        return info_bar
    
    def _create_context_menu(self):
        """컨텍스트 메뉴 생성"""
        context_menu = tk.Menu(self.view, tearoff=0)
        context_menu.add_command(label="📄 보고서 보기", 
                                command=lambda: self.view.event_handler.view_report())
        context_menu.add_command(label="📁 폴더에서 보기", 
                                command=lambda: self.view.event_handler.show_in_folder())
        context_menu.add_separator()
        context_menu.add_command(label="🔄 다시 처리", 
                                command=lambda: self.view.event_handler.retry_file())
        context_menu.add_command(label="🚫 처리 취소", 
                                command=lambda: self.view.event_handler.cancel_file())
        context_menu.add_separator()
        context_menu.add_command(label="🗑️ 목록에서 제거", 
                                command=lambda: self.view.event_handler.remove_file())
        
        self.view.context_menu = context_menu
    
    def setup_tree_style(self):
        """트리뷰 스타일 설정"""
        if not self.view.tree:
            return
            
        style = ttk.Style()
        
        # 다크 테마 스타일
        style.configure("Treeview",
                       background=self.view.colors['bg_secondary'],
                       foreground=self.view.colors['text_primary'],
                       fieldbackground=self.view.colors['bg_secondary'],
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       background=self.view.colors['bg_card'],
                       foreground=self.view.colors['text_primary'],
                       borderwidth=0)
        
        style.map("Treeview",
                 background=[('selected', self.view.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # 태그 스타일
        self.view.tree.tag_configure('waiting', foreground='#ffc107')
        self.view.tree.tag_configure('processing', foreground='#17a2b8')
        self.view.tree.tag_configure('success', foreground='#28a745')
        self.view.tree.tag_configure('error', foreground='#dc3545')
        self.view.tree.tag_configure('cancelled', foreground='#6c757d')
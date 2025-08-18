"""
UI Builder 헬퍼 클래스
기능: 통합 처리 뷰의 UI 컴포넌트 생성 및 스타일 설정
최종 수정: 2025-01-12
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Any
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import UnifiedProcessingView

from ...controllers import FileStatus


class UIBuilder:
    """
    UI 생성 및 관리 헬퍼
    
    역할:
    - UI 컴포넌트 생성
    - 레이아웃 구성
    - 스타일 설정
    """
    
    def __init__(self, view: 'UnifiedProcessingView'):
        """
        헬퍼 초기화
        
        Args:
            view: 메인 뷰 인스턴스
        """
        self.view = view
    
    def create_ui(self):
        """전체 UI 구성"""
        self.view.configure(fg_color=self.view.colors['bg_primary'])
        
        # 헤더
        header_frame = self._create_header()
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # 필터 영역
        filter_frame = self._create_filter_section()
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # 메인 콘텐츠 영역
        content_frame = self._create_content_section()
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
    
    def _create_header(self) -> ctk.CTkFrame:
        """헤더 생성"""
        header = ctk.CTkFrame(self.view, fg_color="transparent", height=50)
        
        # 제목
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            title_frame,
            text="📁 처리 현황",
            font=('Arial', 24, 'bold')
        ).pack(side='left')
        
        # 상태 요약
        status_summary_label = ctk.CTkLabel(
            title_frame,
            text="",
            font=('Arial', 12),
            text_color=self.view.colors['text_secondary']
        )
        status_summary_label.pack(side='left', padx=(20, 0))
        self.view.widgets['status_summary_label'] = status_summary_label
        
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
                variable=self.view.date_range,
                value=value,
                command=self.view.refresh,
                width=80
            )
            btn.pack(side='left', padx=5)
        
        # 액션 버튼
        ctk.CTkButton(
            button_frame,
            text="➕ 파일 추가",
            width=100,
            height=32,
            command=lambda: self.view.action_handler.add_files(),
            fg_color=self.view.colors['success']
        ).pack(side='left', padx=(20, 5))
        
        ctk.CTkButton(
            button_frame,
            text="🔄 새로고침",
            width=100,
            height=32,
            command=self.view.refresh
        ).pack(side='left', padx=5)
        
        return header
    
    def _create_filter_section(self) -> ctk.CTkFrame:
        """필터 섹션 생성"""
        filter_container = ctk.CTkFrame(
            self.view,
            fg_color=self.view.colors['bg_card'],
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
            textvariable=self.view.search_var,
            width=300
        )
        search_entry.pack(side='left')
        search_entry.bind('<Return>', lambda e: self.view.refresh())
        
        # 상태 필터
        status_frame = ctk.CTkFrame(inner, fg_color="transparent")
        status_frame.pack(side='left', fill='y', padx=(0, 20))
        
        ctk.CTkLabel(
            status_frame,
            text="상태:",
            font=('Arial', 12)
        ).pack(side='left', padx=(0, 5))
        
        status_options = [
            "all", "processing", "waiting", "completed", "error", "history_only"
        ]
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.view.filter_status,
            values=status_options,
            command=lambda v: self.view.refresh(),
            width=120
        )
        status_menu.pack(side='left')
        
        # 프로파일 필터
        profile_frame = ctk.CTkFrame(inner, fg_color="transparent")
        profile_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            profile_frame,
            text="프로파일:",
            font=('Arial', 12)
        ).pack(side='left', padx=(0, 5))
        
        profiles = ["all"] + list(self.view.controller.profile_manager.profiles.keys())
        profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.view.profile_filter,
            values=profiles,
            command=lambda v: self.view.refresh(),
            width=150
        )
        profile_menu.pack(side='left')
        
        return filter_container
    
    def _create_content_section(self) -> ctk.CTkFrame:
        """콘텐츠 섹션 생성"""
        content_container = ctk.CTkFrame(
            self.view,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10
        )
        
        # 섹션 헤더
        header_frame = ctk.CTkFrame(content_container, fg_color="transparent", height=40)
        header_frame.pack(fill='x', padx=15, pady=(15, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="📋 처리 목록",
            font=('Arial', 16, 'bold')
        ).pack(side='left')
        
        # 통계 라벨
        stats_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=('Arial', 11),
            text_color=self.view.colors['text_secondary']
        )
        stats_label.pack(side='left', padx=(20, 0))
        self.view.widgets['stats_label'] = stats_label
        
        # 액션 버튼들
        action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        action_frame.pack(side='right')
        
        ctk.CTkButton(
            action_frame,
            text="⏸️ 일시정지",
            width=90,
            height=28,
            command=lambda: self.view.action_handler.toggle_pause(),
            fg_color=self.view.colors['warning']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="📂 파일 열기",
            width=90,
            height=28,
            command=lambda: self.view.action_handler.open_selected_file(),
            fg_color=self.view.colors['info']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="📝 보고서",
            width=80,
            height=28,
            command=lambda: self.view.action_handler.view_report(),
            fg_color=self.view.colors['accent']
        ).pack(side='left', padx=2)
        
        ctk.CTkButton(
            action_frame,
            text="🗑️ 완료 지우기",
            width=100,
            height=28,
            command=lambda: self.view.action_handler.clear_completed(),
            fg_color=self.view.colors['error']
        ).pack(side='left', padx=2)
        
        # 트리뷰 프레임
        tree_frame = ctk.CTkFrame(content_container, fg_color="transparent")
        tree_frame.pack(fill='both', expand=True, padx=15, pady=(5, 15))
        
        # 트리뷰 생성
        self.view.tree = self._create_treeview(tree_frame)
        self.view.widgets['tree'] = self.view.tree
        
        return content_container
    
    def _create_treeview(self, parent) -> ttk.Treeview:
        """트리뷰 생성"""
        # 스크롤바
        scrollbar = ttk.Scrollbar(parent)
        scrollbar.pack(side='right', fill='y')
        
        # 컬럼 정의
        columns = ('type', 'status', 'filename', 'profile', 'size', 'pages', 
                  'issues', 'progress', 'time', 'date')
        headings = {
            'type': '구분',
            'status': '상태',
            'filename': '파일명',
            'profile': '프로파일',
            'size': '크기',
            'pages': '페이지',
            'issues': '문제',
            'progress': '진행률',
            'time': '소요시간',
            'date': '처리일시'
        }
        
        # 트리뷰 생성
        tree = ttk.Treeview(
            parent,
            columns=columns,
            show='tree headings',
            selectmode='extended',
            height=20
        )
        tree.pack(side='left', fill='both', expand=True)
        
        # 스크롤바 연결
        scrollbar.config(command=tree.yview)
        tree.config(yscrollcommand=scrollbar.set)
        
        # 컬럼 설정
        tree.column('#0', width=50, stretch=False)  # 아이콘
        tree.heading('#0', text='')
        
        # 컬럼 너비 설정
        column_widths = {
            'type': 60,
            'status': 80,
            'filename': 300,
            'profile': 120,
            'size': 80,
            'pages': 60,
            'issues': 80,
            'progress': 80,
            'time': 80,
            'date': 140
        }
        
        for col, heading in headings.items():
            width = column_widths.get(col, 100)
            tree.column(col, width=width, stretch=(col == 'filename'))
            tree.heading(col, text=heading)
        
        # 이벤트 바인딩
        tree.bind('<Double-Button-1>', lambda e: self.view.event_handler.on_double_click(e))
        tree.bind('<<TreeviewSelect>>', lambda e: self.view.event_handler.on_selection(e))
        
        return tree
    
    def setup_tree_style(self):
        """트리뷰 스타일 설정"""
        style = ttk.Style()
        
        # 기본 스타일
        style.configure("Treeview",
                       background=self.view.colors['bg_secondary'],
                       foreground=self.view.colors['text_primary'],
                       fieldbackground=self.view.colors['bg_secondary'],
                       borderwidth=0)
        style.map('Treeview',
                 background=[('selected', self.view.colors['accent'])])
        
        # 헤더 스타일
        style.configure("Treeview.Heading",
                       background=self.view.colors['bg_card'],
                       foreground=self.view.colors['text_primary'],
                       borderwidth=0)
        style.map("Treeview.Heading",
                 background=[('active', self.view.colors['accent'])])
        
        # 태그 색상 설정
        if hasattr(self.view, 'tree'):
            self.view.tree.tag_configure('waiting', foreground='#ffc107')
            self.view.tree.tag_configure('processing', foreground='#17a2b8')
            self.view.tree.tag_configure('success', foreground='#28a745')
            self.view.tree.tag_configure('error', foreground='#dc3545')
            self.view.tree.tag_configure('cancelled', foreground='#6c757d')
            self.view.tree.tag_configure('history', foreground=self.view.colors['history'])
            
            # 구분선을 위한 태그
            self.view.tree.tag_configure('separator', background='#3a3a3a')
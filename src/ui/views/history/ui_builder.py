"""
처리 이력 UI 빌더
기능: 이력 화면의 UI 구성 요소 생성
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import HistoryView


class UIBuilder:
    """UI 생성 헬퍼 클래스"""
    
    def __init__(self, view: 'HistoryView'):
        self.view = view
        
    def create_ui(self):
        """전체 UI 구성"""
        # 헤더
        header_frame = self._create_header()
        header_frame.pack(fill='x', padx=20, pady=(20, 10))
        
        # 필터 영역
        filter_frame = self._create_filter_section()
        filter_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        # 테이블 영역
        table_frame = self._create_table_section()
        table_frame.pack(fill='both', expand=True, padx=20, pady=(0, 10))
        
        # 하단 컨트롤
        bottom_frame = self._create_bottom_controls()
        bottom_frame.pack(fill='x', padx=20, pady=(0, 20))
    
    def _create_header(self) -> ctk.CTkFrame:
        """헤더 생성"""
        header = ctk.CTkFrame(self.view, fg_color="transparent", height=50)
        
        # 제목
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side='left', fill='y')
        
        ctk.CTkLabel(
            title_frame,
            text="📋 처리 이력",
            font=('Arial', 24, 'bold')
        ).pack(side='left')
        
        ctk.CTkLabel(
            title_frame,
            text="PDF 처리 기록 조회 및 관리",
            font=('Arial', 12),
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(20, 0))
        
        # 액션 버튼
        action_frame = ctk.CTkFrame(header, fg_color="transparent")
        action_frame.pack(side='right', fill='y')
        
        # 새로고침
        ctk.CTkButton(
            action_frame,
            text="🔄",
            width=40,
            height=32,
            command=self.view.refresh_data,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # CSV 내보내기
        ctk.CTkButton(
            action_frame,
            text="📊 내보내기",
            width=100,
            height=32,
            command=self.view.export_to_csv,
            fg_color=self.view.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # 삭제
        delete_button = ctk.CTkButton(
            action_frame,
            text="🗑️ 삭제",
            width=80,
            height=32,
            command=self.view.delete_selected,
            fg_color=self.view.colors['error'],
            state='disabled'
        )
        delete_button.pack(side='left', padx=5)
        self.view.widgets['delete_button'] = delete_button
        
        return header
    
    def _create_filter_section(self) -> ctk.CTkFrame:
        """필터 섹션 생성"""
        filter_container = ctk.CTkFrame(
            self.view,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10
        )
        
        filter_frame = ctk.CTkFrame(filter_container, fg_color="transparent")
        filter_frame.pack(fill='x', padx=20, pady=15)
        
        # 첫 번째 행: 검색 및 기간
        row1 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row1.pack(fill='x', pady=(0, 10))
        
        # 검색
        search_frame = ctk.CTkFrame(row1, fg_color="transparent")
        search_frame.pack(side='left', fill='x', expand=True)
        
        ctk.CTkLabel(
            search_frame,
            text="🔍",
            font=('Arial', 16)
        ).pack(side='left', padx=(0, 10))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.view.search_var,
            placeholder_text="파일명 검색...",
            width=300
        )
        search_entry.pack(side='left', fill='x', expand=True)
        search_entry.bind('<Return>', lambda e: self.view.apply_filters())
        self.view.widgets['search_entry'] = search_entry
        
        # 기간 선택
        date_frame = ctk.CTkFrame(row1, fg_color="transparent")
        date_frame.pack(side='right', padx=(20, 0))
        
        ctk.CTkLabel(
            date_frame,
            text="기간:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        date_options = [
            "전체", "오늘", "어제", "이번 주", 
            "이번 달", "지난 달", "사용자 지정"
        ]
        
        date_menu = ctk.CTkOptionMenu(
            date_frame,
            variable=self.view.date_range,
            values=date_options,
            command=lambda v: self.view.event_handler.on_date_range_change(v),
            width=120
        )
        date_menu.pack(side='left')
        self.view.widgets['date_menu'] = date_menu
        
        # 사용자 지정 날짜 (초기에는 숨김)
        custom_date_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        self.view.widgets['custom_date_frame'] = custom_date_frame
        
        # 두 번째 행: 상태 및 프로파일 필터
        row2 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row2.pack(fill='x')
        
        # 상태 필터
        status_frame = ctk.CTkFrame(row2, fg_color="transparent")
        status_frame.pack(side='left', padx=(0, 20))
        
        ctk.CTkLabel(
            status_frame,
            text="상태:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.view.status_filter,
            values=["전체", "완료", "오류", "취소"],
            command=lambda _: self.view.apply_filters(),
            width=100
        )
        status_menu.pack(side='left')
        self.view.widgets['status_menu'] = status_menu
        
        # 프로파일 필터
        profile_frame = ctk.CTkFrame(row2, fg_color="transparent")
        profile_frame.pack(side='left')
        
        ctk.CTkLabel(
            profile_frame,
            text="프로파일:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.view.profile_filter,
            values=["전체"],
            command=lambda _: self.view.apply_filters(),
            width=120
        )
        profile_menu.pack(side='left')
        self.view.widgets['profile_menu'] = profile_menu
        
        # 적용 버튼
        ctk.CTkButton(
            row2,
            text="적용",
            width=80,
            height=32,
            command=self.view.apply_filters
        ).pack(side='right')
        
        return filter_container
    
    def _create_table_section(self) -> ctk.CTkFrame:
        """테이블 섹션 생성 - list_manager에서 관리"""
        table_container = ctk.CTkFrame(
            self.view,
            fg_color=self.view.colors['bg_card'],
            corner_radius=10
        )
        
        # 테이블 프레임
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # HistoryListManager가 테이블 생성
        if hasattr(self.view, 'list_manager'):
            self.view.list_manager.create_table(table_frame)
        
        # 빈 상태 메시지
        empty_label = ctk.CTkLabel(
            table_container,
            text="처리 이력이 없습니다",
            font=('Arial', 16),
            text_color=self.view.colors['text_secondary']
        )
        self.view.widgets['empty_label'] = empty_label
        # 초기에는 숨김
        
        return table_container
    
    def _create_bottom_controls(self) -> ctk.CTkFrame:
        """하단 컨트롤 생성"""
        bottom_frame = ctk.CTkFrame(self.view, fg_color="transparent")
        
        # 왼쪽: 선택 정보
        info_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        info_frame.pack(side='left', fill='y')
        
        selection_label = ctk.CTkLabel(
            info_frame,
            text="선택: 0개",
            text_color=self.view.colors['text_secondary']
        )
        selection_label.pack(side='left', padx=(0, 20))
        self.view.widgets['selection_label'] = selection_label
        
        total_label = ctk.CTkLabel(
            info_frame,
            text="전체: 0개",
            text_color=self.view.colors['text_secondary']
        )
        total_label.pack(side='left')
        self.view.widgets['total_label'] = total_label
        
        # 오른쪽: 페이징
        paging_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        paging_frame.pack(side='right', fill='y')
        
        # 이전 페이지
        prev_button = ctk.CTkButton(
            paging_frame,
            text="◀",
            width=40,
            height=32,
            command=self.view.prev_page,
            fg_color=self.view.colors['bg_secondary']
        )
        prev_button.pack(side='left', padx=5)
        self.view.widgets['prev_button'] = prev_button
        
        # 페이지 정보
        page_label = ctk.CTkLabel(
            paging_frame,
            text="1 / 1",
            font=('Arial', 12)
        )
        page_label.pack(side='left', padx=20)
        self.view.widgets['page_label'] = page_label
        
        # 다음 페이지
        next_button = ctk.CTkButton(
            paging_frame,
            text="▶",
            width=40,
            height=32,
            command=self.view.next_page,
            fg_color=self.view.colors['bg_secondary']
        )
        next_button.pack(side='left', padx=5)
        self.view.widgets['next_button'] = next_button
        
        # 페이지당 항목 수
        ctk.CTkLabel(
            paging_frame,
            text="페이지당:",
            text_color=self.view.colors['text_secondary']
        ).pack(side='left', padx=(20, 10))
        
        per_page_menu = ctk.CTkOptionMenu(
            paging_frame,
            variable=self.view.per_page_var,
            values=["20", "50", "100", "200"],
            command=lambda v: self.view.event_handler.on_per_page_change(v),
            width=80
        )
        per_page_menu.pack(side='left')
        
        return bottom_frame
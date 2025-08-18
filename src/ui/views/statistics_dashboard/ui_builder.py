"""
UI 빌더 - 통계 대시보드 UI 구성
"""

import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
from typing import TYPE_CHECKING, Dict, Any
from datetime import datetime

if TYPE_CHECKING:
    from .base import StatisticsDashboardView


class UIBuilder:
    """UI 빌더"""
    
    def __init__(self, view: 'StatisticsDashboardView'):
        self.view = view
        
    def create_ui(self):
        """UI 생성"""
        # 상단 툴바
        self._create_toolbar()
        
        # 메인 컨텐츠 영역
        self._create_content_area()
        
    def _create_toolbar(self):
        """툴바 생성"""
        toolbar = ctk.CTkFrame(self.view, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # 제목
        title = ctk.CTkLabel(
            toolbar,
            text="📊 통계 대시보드",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(side="left", padx=(0, 20))
        
        # 기간 선택
        period_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        period_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(period_frame, text="기간:").pack(side="left", padx=(0, 5))
        
        self.view.period_var = ctk.StringVar(value="일별")
        period_menu = ctk.CTkOptionMenu(
            period_frame,
            values=["일별", "주별", "월별", "연별"],
            variable=self.view.period_var,
            command=self.view.on_period_change,
            width=100
        )
        period_menu.pack(side="left")
        self.view.widgets['period_menu'] = period_menu
        
        # 날짜 범위 선택
        date_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        date_frame.pack(side="left", padx=20)
        
        ctk.CTkLabel(date_frame, text="날짜:").pack(side="left", padx=(0, 5))
        
        date_label = ctk.CTkLabel(
            date_frame,
            text=self.view.data_processor.get_date_range_text("day"),
            fg_color=("gray85", "gray25"),
            corner_radius=5
        )
        date_label.pack(side="left", padx=5, pady=2, ipadx=10, ipady=2)
        self.view.widgets['date_label'] = date_label
        
        # 새로고침 버튼
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="🔄 새로고침",
            command=self.view.refresh_data,
            width=100
        )
        refresh_btn.pack(side="right", padx=5)
        
        # 내보내기 버튼
        export_btn = ctk.CTkButton(
            toolbar,
            text="📥 내보내기",
            command=self.view.export_statistics,
            width=100
        )
        export_btn.pack(side="right", padx=5)
        
    def _create_content_area(self):
        """메인 컨텐츠 영역 생성"""
        # 스크롤 가능한 프레임
        content_frame = ctk.CTkScrollableFrame(self.view)
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        content_frame.grid_columnconfigure(0, weight=1)
        self.view.widgets['content_frame'] = content_frame
        
        # 요약 카드
        self._create_summary_cards(content_frame)
        
        # 차트 영역
        self._create_chart_area(content_frame)
        
        # 최근 처리 목록
        self._create_recent_list(content_frame)
        
    def _create_summary_cards(self, parent):
        """요약 카드 생성"""
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # 각 카드 생성
        cards = [
            ("처리 파일", "📄", ("blue", "darkblue")),
            ("성공률", "✅", ("green", "darkgreen")),
            ("평균 시간", "⏱", ("orange", "darkorange")),
            ("총 에러", "⚠️", ("red", "darkred"))
        ]
        
        for i, (title, icon, colors) in enumerate(cards):
            card = self._create_card(parent, title, icon, colors)
            card.grid(row=0, column=i, padx=5, sticky="ew")
            self.view.widgets[f'card_{title}'] = card
            
    def _create_card(self, parent, title: str, icon: str, colors: tuple) -> ctk.CTkFrame:
        """개별 카드 생성"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid_columnconfigure(0, weight=1)
        
        # 아이콘
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=24)
        )
        icon_label.grid(row=0, column=0, pady=(10, 5))
        
        # 값
        value_label = ctk.CTkLabel(
            card,
            text="0",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        value_label.grid(row=1, column=0, pady=5)
        card.value_label = value_label  # 참조 저장
        
        # 제목
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        title_label.grid(row=2, column=0, pady=(0, 10))
        
        return card
        
    def _create_chart_area(self, parent):
        """차트 영역 생성"""
        chart_frame = ctk.CTkFrame(parent, corner_radius=10)
        chart_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        chart_frame.grid_columnconfigure(0, weight=1)
        self.view.widgets['chart_frame'] = chart_frame
        
        # 차트 제목
        chart_title = ctk.CTkLabel(
            chart_frame,
            text="처리 통계",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        chart_title.grid(row=0, column=0, pady=10)
        
        # 차트 캔버스 (ChartManager가 사용)
        chart_canvas_frame = ctk.CTkFrame(chart_frame, height=300)
        chart_canvas_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        chart_canvas_frame.grid_columnconfigure(0, weight=1)
        self.view.widgets['chart_canvas_frame'] = chart_canvas_frame
        
    def _create_recent_list(self, parent):
        """최근 처리 목록 생성"""
        list_frame = ctk.CTkFrame(parent, corner_radius=10)
        list_frame.grid(row=2, column=0, sticky="ew")
        list_frame.grid_columnconfigure(0, weight=1)
        
        # 헤더
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            header_frame,
            text="최근 처리 파일",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        more_btn = ctk.CTkButton(
            header_frame,
            text="더보기",
            command=self.view.show_more_history,
            width=80
        )
        more_btn.pack(side="right")
        
        # 트리뷰
        tree_frame = ctk.CTkFrame(list_frame)
        tree_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        columns = ("파일명", "상태", "처리시간", "프로파일")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        tree.pack(side="left", fill="both", expand=True)
        self.view.widgets['recent_tree'] = tree
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
    def update_summary_cards(self, stats: Dict[str, Any]):
        """요약 카드 업데이트"""
        # 카드 값 업데이트
        if 'card_처리 파일' in self.view.widgets:
            card = self.view.widgets['card_처리 파일']
            if hasattr(card, 'value_label'):
                card.value_label.configure(text=str(stats.get('total_files', 0)))
                
        if 'card_성공률' in self.view.widgets:
            card = self.view.widgets['card_성공률']
            if hasattr(card, 'value_label'):
                success_rate = stats.get('success_rate', 0)
                card.value_label.configure(text=f"{success_rate:.1f}%")
                
        if 'card_평균 시간' in self.view.widgets:
            card = self.view.widgets['card_평균 시간']
            if hasattr(card, 'value_label'):
                avg_time = stats.get('avg_processing_time', 0)
                card.value_label.configure(text=f"{avg_time:.1f}초")
                
        if 'card_총 에러' in self.view.widgets:
            card = self.view.widgets['card_총 에러']
            if hasattr(card, 'value_label'):
                card.value_label.configure(text=str(stats.get('total_errors', 0)))
                
    def update_recent_list(self):
        """최근 처리 목록 업데이트"""
        if 'recent_tree' not in self.view.widgets:
            return
            
        tree = self.view.widgets['recent_tree']
        
        # 기존 항목 삭제
        for item in tree.get_children():
            tree.delete(item)
            
        # 최근 히스토리 가져오기
        recent_history = self.view.history_manager.get_recent_history(10)
        
        for history in recent_history:
            status = "✅ 성공" if history.status == "completed" else "❌ 실패"
            processing_time = f"{history.processing_time:.1f}초" if history.processing_time else "-"
            
            tree.insert("", "end", values=(
                history.file_name,
                status,
                processing_time,
                history.profile_name or "기본"
            ))
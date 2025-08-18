# src/ui/views/history_view.py
"""
처리 이력 뷰

PDF 처리 이력을 조회하고 관리하는 화면입니다.
날짜별, 상태별 필터링과 검색 기능을 제공합니다.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime, timedelta, date
from pathlib import Path
import webbrowser
import os

from ..controllers import FileController
from ...data import get_data_manager, HistoryEntry


class HistoryView(ctk.CTkFrame):
    """
    처리 이력 뷰 - PDF 처리 이력을 표시하고 관리
    """
    
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
        
        # UI 상태
        self.selected_ids: Set[int] = set()
        self.current_page = 1
        self.items_per_page = 50
        self.total_items = 0
        
        # 필터 변수
        self.search_var = tk.StringVar()
        self.status_filter = tk.StringVar(value="all")
        self.profile_filter = tk.StringVar(value="all")
        self.date_range = tk.StringVar(value="all")
        self.custom_start_date: Optional[date] = None
        self.custom_end_date: Optional[date] = None
        
        # 현재 표시 중인 이력
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
            'border': '#404040'
        }
        
        # UI 생성
        self._create_ui()
        
        # 초기 데이터 로드
        self.refresh_data()
    
    def _create_ui(self):
        """UI 구성"""
        self.configure(fg_color=self.colors['bg_primary'])
        
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
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        
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
            text_color=self.colors['text_secondary']
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
            command=self.refresh_data,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # CSV 내보내기
        ctk.CTkButton(
            action_frame,
            text="📊 내보내기",
            width=100,
            height=32,
            command=self.export_to_csv,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # 삭제
        self.delete_button = ctk.CTkButton(
            action_frame,
            text="🗑️ 삭제",
            width=80,
            height=32,
            command=self.delete_selected,
            fg_color=self.colors['error'],
            state='disabled'
        )
        self.delete_button.pack(side='left', padx=5)
        
        return header
    
    def _create_filter_section(self) -> ctk.CTkFrame:
        """필터 섹션 생성"""
        filter_container = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_card'],
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
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="파일명 검색...",
            width=300
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<Return>', lambda e: self.apply_filters())
        
        # 기간 선택
        date_frame = ctk.CTkFrame(row1, fg_color="transparent")
        date_frame.pack(side='right', padx=(20, 0))
        
        ctk.CTkLabel(
            date_frame,
            text="기간:",
            text_color=self.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        date_options = [
            ("전체", "all"),
            ("오늘", "today"),
            ("어제", "yesterday"),
            ("이번 주", "week"),
            ("이번 달", "month"),
            ("지난 달", "last_month"),
            ("사용자 지정", "custom")
        ]
        
        self.date_menu = ctk.CTkOptionMenu(
            date_frame,
            variable=self.date_range,
            values=[opt[0] for opt in date_options],
            command=self.on_date_range_change,
            width=120
        )
        self.date_menu.pack(side='left')
        
        # 사용자 지정 날짜 (초기에는 숨김)
        self.custom_date_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        # self.custom_date_frame.pack(side='left', padx=(10, 0))
        
        # 두 번째 행: 상태 및 프로파일 필터
        row2 = ctk.CTkFrame(filter_frame, fg_color="transparent")
        row2.pack(fill='x')
        
        # 상태 필터
        status_frame = ctk.CTkFrame(row2, fg_color="transparent")
        status_frame.pack(side='left', padx=(0, 20))
        
        ctk.CTkLabel(
            status_frame,
            text="상태:",
            text_color=self.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        self.status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.status_filter,
            values=["전체", "완료", "오류", "취소"],
            command=lambda _: self.apply_filters(),
            width=100
        )
        self.status_menu.pack(side='left')
        
        # 프로파일 필터
        profile_frame = ctk.CTkFrame(row2, fg_color="transparent")
        profile_frame.pack(side='left')
        
        ctk.CTkLabel(
            profile_frame,
            text="프로파일:",
            text_color=self.colors['text_secondary']
        ).pack(side='left', padx=(0, 10))
        
        self.profile_menu = ctk.CTkOptionMenu(
            profile_frame,
            variable=self.profile_filter,
            values=["전체"],
            command=lambda _: self.apply_filters(),
            width=120
        )
        self.profile_menu.pack(side='left')
        
        # 적용 버튼
        ctk.CTkButton(
            row2,
            text="적용",
            width=80,
            height=32,
            command=self.apply_filters
        ).pack(side='right')
        
        return filter_container
    
    def _create_table_section(self) -> ctk.CTkFrame:
        """테이블 섹션 생성"""
        table_container = ctk.CTkFrame(
            self,
            fg_color=self.colors['bg_card'],
            corner_radius=10
        )
        
        # 테이블 프레임
        table_frame = ctk.CTkFrame(table_container, fg_color="transparent")
        table_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Treeview 스타일
        style = ttk.Style()
        style.theme_use('default')
        
        # 색상 설정
        style.configure(
            "History.Treeview",
            background=self.colors['bg_secondary'],
            foreground=self.colors['text_primary'],
            fieldbackground=self.colors['bg_secondary'],
            borderwidth=0,
            font=('Arial', 10)
        )
        style.map('History.Treeview',
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.configure(
            "History.Treeview.Heading",
            background=self.colors['bg_card'],
            foreground=self.colors['text_primary'],
            borderwidth=1,
            font=('Arial', 10, 'bold')
        )
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columns = (
            'filename', 'processed_at', 'profile', 'pages', 
            'quality_score', 'errors', 'warnings', 'time', 'status'
        )
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='tree headings',
            style="History.Treeview",
            yscrollcommand=scrollbar.set
        )
        
        scrollbar.config(command=self.tree.yview)
        
        # 컬럼 설정
        self.tree.heading('#0', text='✓', anchor='center')
        self.tree.column('#0', width=40, stretch=False)
        
        column_configs = [
            ('filename', '파일명', 250, 'w'),
            ('processed_at', '처리일시', 150, 'center'),
            ('profile', '프로파일', 100, 'center'),
            ('pages', '페이지', 70, 'center'),
            ('quality_score', '품질점수', 80, 'center'),
            ('errors', '오류', 60, 'center'),
            ('warnings', '경고', 60, 'center'),
            ('time', '처리시간', 80, 'center'),
            ('status', '상태', 80, 'center')
        ]
        
        for col_id, heading, width, anchor in column_configs:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor=anchor)
        
        # 이벤트 바인딩
        self.tree.bind('<ButtonRelease-1>', self.on_tree_click)
        self.tree.bind('<Double-Button-1>', self.on_tree_double_click)
        
        # 태그 설정
        self.tree.tag_configure('completed', foreground=self.colors['success'])
        self.tree.tag_configure('error', foreground=self.colors['error'])
        self.tree.tag_configure('cancelled', foreground=self.colors['text_secondary'])
        
        self.tree.pack(fill='both', expand=True)
        
        # 빈 상태 메시지
        self.empty_label = ctk.CTkLabel(
            table_container,
            text="처리 이력이 없습니다",
            font=('Arial', 16),
            text_color=self.colors['text_secondary']
        )
        # 초기에는 숨김
        
        return table_container
    
    def _create_bottom_controls(self) -> ctk.CTkFrame:
        """하단 컨트롤 생성"""
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        # 왼쪽: 선택 정보
        info_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        info_frame.pack(side='left', fill='y')
        
        self.selection_label = ctk.CTkLabel(
            info_frame,
            text="선택: 0개",
            text_color=self.colors['text_secondary']
        )
        self.selection_label.pack(side='left', padx=(0, 20))
        
        self.total_label = ctk.CTkLabel(
            info_frame,
            text="전체: 0개",
            text_color=self.colors['text_secondary']
        )
        self.total_label.pack(side='left')
        
        # 오른쪽: 페이징
        paging_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        paging_frame.pack(side='right', fill='y')
        
        # 이전 페이지
        self.prev_button = ctk.CTkButton(
            paging_frame,
            text="◀",
            width=40,
            height=32,
            command=self.prev_page,
            fg_color=self.colors['bg_secondary']
        )
        self.prev_button.pack(side='left', padx=5)
        
        # 페이지 정보
        self.page_label = ctk.CTkLabel(
            paging_frame,
            text="1 / 1",
            font=('Arial', 12)
        )
        self.page_label.pack(side='left', padx=20)
        
        # 다음 페이지
        self.next_button = ctk.CTkButton(
            paging_frame,
            text="▶",
            width=40,
            height=32,
            command=self.next_page,
            fg_color=self.colors['bg_secondary']
        )
        self.next_button.pack(side='left', padx=5)
        
        # 페이지당 항목 수
        ctk.CTkLabel(
            paging_frame,
            text="페이지당:",
            text_color=self.colors['text_secondary']
        ).pack(side='left', padx=(20, 10))
        
        self.per_page_var = tk.StringVar(value="50")
        per_page_menu = ctk.CTkOptionMenu(
            paging_frame,
            variable=self.per_page_var,
            values=["20", "50", "100", "200"],
            command=self.on_per_page_change,
            width=80
        )
        per_page_menu.pack(side='left')
        
        return bottom_frame
    
    def refresh_data(self):
        """데이터 새로고침"""
        self.current_page = 1
        self.apply_filters()
        self._update_profile_filter()
    
    def apply_filters(self):
        """필터 적용"""
        # 날짜 범위 계산
        start_date, end_date = self._calculate_date_range()
        
        # 필터 값 변환
        status_map = {
            "전체": "all",
            "완료": "completed",
            "오류": "error",
            "취소": "cancelled"
        }
        status_filter = status_map.get(self.status_filter.get(), "all")
        
        profile_filter = self.profile_filter.get()
        if profile_filter == "전체":
            profile_filter = "all"
        
        # 전체 개수 조회
        self.total_items = self.data_manager.get_history_count(
            start_date=start_date,
            end_date=end_date,
            filename_filter=self.search_var.get(),
            status_filter=status_filter,
            profile_filter=profile_filter
        )
        
        # 페이지 계산
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        if self.current_page > total_pages:
            self.current_page = total_pages
        
        # 이력 조회
        offset = (self.current_page - 1) * self.items_per_page
        self.current_entries = self.data_manager.get_history(
            start_date=start_date,
            end_date=end_date,
            filename_filter=self.search_var.get(),
            status_filter=status_filter,
            profile_filter=profile_filter,
            limit=self.items_per_page,
            offset=offset
        )
        
        # 테이블 업데이트
        self._update_table()
        
        # UI 업데이트
        self._update_ui_state()
    
    def _update_table(self):
        """테이블 업데이트"""
        # 기존 항목 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 선택 초기화
        self.selected_ids.clear()
        
        if not self.current_entries:
            # 빈 상태 표시
            self.empty_label.pack(expand=True)
            return
        else:
            self.empty_label.pack_forget()
        
        # 이력 추가
        for entry in self.current_entries:
            # 태그 결정
            tag = ''
            if entry.status == 'completed':
                tag = 'completed'
            elif entry.status == 'error':
                tag = 'error'
            elif entry.status == 'cancelled':
                tag = 'cancelled'
            
            # 값 포맷팅
            values = (
                entry.filename,
                entry.processed_at.strftime('%Y-%m-%d %H:%M'),
                entry.profile_used,
                str(entry.page_count),
                f"{entry.quality_score:.1f}",
                str(entry.error_count),
                str(entry.warning_count),
                f"{entry.processing_time:.1f}s",
                self._get_status_text(entry.status)
            )
            
            # 트리에 추가
            item = self.tree.insert('', 'end', values=values, tags=(tag,))
            # ID 저장
            self.tree.set(item, 'id', entry.id)
    
    def _update_ui_state(self):
        """UI 상태 업데이트"""
        # 페이지 정보
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        self.page_label.configure(text=f"{self.current_page} / {total_pages}")
        
        # 버튼 상태
        self.prev_button.configure(state='normal' if self.current_page > 1 else 'disabled')
        self.next_button.configure(state='normal' if self.current_page < total_pages else 'disabled')
        
        # 정보 레이블
        self.total_label.configure(text=f"전체: {self.total_items}개")
        self._update_selection_info()
    
    def _update_selection_info(self):
        """선택 정보 업데이트"""
        count = len(self.selected_ids)
        self.selection_label.configure(text=f"선택: {count}개")
        self.delete_button.configure(state='normal' if count > 0 else 'disabled')
    
    def _update_profile_filter(self):
        """프로파일 필터 옵션 업데이트"""
        # 고유한 프로파일 목록 가져오기 (간단한 방법)
        profiles = ["전체", "default", "strict", "quick", "web"]
        
        # 실제로는 데이터베이스에서 조회해야 하지만, 
        # 성능을 위해 하드코딩하거나 캐시 사용
        
        self.profile_menu.configure(values=profiles)
    
    def _calculate_date_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """날짜 범위 계산"""
        date_range = self.date_range.get()
        now = datetime.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if date_range == "all" or date_range == "전체":
            return None, None
        elif date_range == "today" or date_range == "오늘":
            return today, now
        elif date_range == "yesterday" or date_range == "어제":
            yesterday = today - timedelta(days=1)
            return yesterday, today
        elif date_range == "week" or date_range == "이번 주":
            start = today - timedelta(days=today.weekday())
            return start, now
        elif date_range == "month" or date_range == "이번 달":
            start = today.replace(day=1)
            return start, now
        elif date_range == "last_month" or date_range == "지난 달":
            last_month = today.replace(day=1) - timedelta(days=1)
            start = last_month.replace(day=1)
            end = today.replace(day=1) - timedelta(seconds=1)
            return start, end
        elif date_range == "custom" or date_range == "사용자 지정":
            # 사용자 지정 날짜 사용
            if self.custom_start_date and self.custom_end_date:
                start = datetime.combine(self.custom_start_date, datetime.min.time())
                end = datetime.combine(self.custom_end_date, datetime.max.time())
                return start, end
        
        return None, None
    
    def _get_status_text(self, status: str) -> str:
        """상태 텍스트"""
        status_map = {
            'completed': '완료',
            'error': '오류',
            'cancelled': '취소',
            'processing': '처리중',
            'waiting': '대기'
        }
        return status_map.get(status, status)
    
    # 이벤트 핸들러
    
    def on_tree_click(self, event):
        """트리 클릭 이벤트"""
        # 체크박스 영역 클릭 확인
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                # ID 가져오기
                entry_id = self.tree.set(item, 'id')
                if entry_id:
                    entry_id = int(entry_id)
                    
                    # 선택 토글
                    if entry_id in self.selected_ids:
                        self.selected_ids.remove(entry_id)
                        self.tree.item(item, text='')
                    else:
                        self.selected_ids.add(entry_id)
                        self.tree.item(item, text='✓')
                    
                    self._update_selection_info()
    
    def on_tree_double_click(self, event):
        """트리 더블클릭 이벤트"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            entry_id = int(self.tree.set(item, 'id'))
            
            # 해당 이력 찾기
            for entry in self.current_entries:
                if entry.id == entry_id:
                    self.show_details(entry)
                    break
    
    def on_date_range_change(self, value):
        """날짜 범위 변경"""
        if value == "사용자 지정":
            # 날짜 선택 다이얼로그 표시
            self.show_date_picker()
        else:
            self.apply_filters()
    
    def on_per_page_change(self, value):
        """페이지당 항목 수 변경"""
        self.items_per_page = int(value)
        self.current_page = 1
        self.apply_filters()
    
    def show_date_picker(self):
        """날짜 선택 다이얼로그"""
        # 간단한 구현 - 실제로는 달력 위젯 사용
        messagebox.showinfo("알림", "날짜 선택 기능은 추후 구현 예정입니다.")
        self.date_range.set("전체")
    
    def show_details(self, entry: HistoryEntry):
        """상세 정보 표시"""
        # 보고서가 있으면 열기
        if entry.report_paths:
            # HTML 보고서 우선
            if 'html' in entry.report_paths:
                report_path = Path(entry.report_paths['html'])
                if report_path.exists():
                    webbrowser.open(str(report_path))
                else:
                    messagebox.showwarning("경고", "보고서 파일을 찾을 수 없습니다.")
            else:
                messagebox.showinfo("정보", "HTML 보고서가 없습니다.")
        else:
            # 간단한 정보 다이얼로그
            info = f"""파일: {entry.filename}
처리일시: {entry.processed_date_str}
프로파일: {entry.profile_used}
품질점수: {entry.quality_score:.1f}
오류: {entry.error_count}개
경고: {entry.warning_count}개
처리시간: {entry.processing_time:.1f}초"""
            
            messagebox.showinfo("처리 상세 정보", info)
    
    def prev_page(self):
        """이전 페이지"""
        if self.current_page > 1:
            self.current_page -= 1
            self.apply_filters()
    
    def next_page(self):
        """다음 페이지"""
        total_pages = max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
        if self.current_page < total_pages:
            self.current_page += 1
            self.apply_filters()
    
    def delete_selected(self):
        """선택 항목 삭제"""
        if not self.selected_ids:
            return
        
        count = len(self.selected_ids)
        if messagebox.askyesno("확인", f"{count}개 항목을 삭제하시겠습니까?"):
            deleted = self.data_manager.delete_history(list(self.selected_ids))
            
            if deleted > 0:
                messagebox.showinfo("완료", f"{deleted}개 항목이 삭제되었습니다.")
                self.refresh_data()
            else:
                messagebox.showerror("오류", "삭제 중 오류가 발생했습니다.")
    
    def export_to_csv(self):
        """CSV로 내보내기"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
            initialfile=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            # 현재 필터 적용된 날짜 범위 사용
            start_date, end_date = self._calculate_date_range()
            
            if self.data_manager.export_to_csv(Path(filename), start_date, end_date):
                messagebox.showinfo("완료", "CSV 파일이 저장되었습니다.")
                
                # 파일 열기 여부 확인
                if messagebox.askyesno("확인", "파일을 열어보시겠습니까?"):
                    try:
                        os.startfile(filename)  # Windows
                    except:
                        webbrowser.open(filename)  # 다른 OS
            else:
                messagebox.showerror("오류", "CSV 저장 중 오류가 발생했습니다.")
    
    def clear_all_history(self):
        """전체 이력 삭제"""
        if messagebox.askyesno(
            "경고", 
            "모든 처리 이력을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."
        ):
            if messagebox.askyesno(
                "최종 확인",
                "정말로 모든 이력을 삭제하시겠습니까?"
            ):
                if self.data_manager.clear_all_history():
                    messagebox.showinfo("완료", "모든 이력이 삭제되었습니다.")
                    self.refresh_data()
                else:
                    messagebox.showerror("오류", "이력 삭제 중 오류가 발생했습니다.")
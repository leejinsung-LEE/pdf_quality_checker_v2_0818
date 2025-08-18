# src/ui/views/processing_view.py
"""
처리 화면 뷰

파일 처리 상태를 표시하고 관리하는 메인 화면입니다.
MVC 패턴의 View 역할을 담당합니다.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Callable, Any, Set
from pathlib import Path
from datetime import datetime
import threading

from ..controllers import FileController, FileStatus, FileItem


class ProcessingView(ctk.CTkFrame):
    """
    처리 화면 - 파일 처리 상태를 표시하는 메인 뷰
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
        
        # UI 상태
        self.selected_items: Set[str] = set()
        self.filter_status = tk.StringVar(value="all")
        self.search_var = tk.StringVar()
        self.folder_filter = tk.StringVar(value="all")
        
        # 컬럼 표시 설정
        self.column_visibility = {
            'icon': True,
            'filename': True,
            'folder': True,
            'profile': True,
            'size': True,
            'pages': True,
            'issues': True,
            'score': True,
            'time': True,
            'status': True
        }
        
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
        
        # 컨트롤러 콜백 설정
        self._setup_controller_callbacks()
        
        # 트리뷰 스타일 설정
        self._setup_tree_style()
    
    def _create_ui(self):
        """UI 구성"""
        # 메인 컨테이너
        self.configure(fg_color=self.colors['bg_primary'])
        
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
        toolbar = ctk.CTkFrame(self, fg_color=self.colors['bg_card'], height=50)
        
        # 왼쪽 버튼들
        left_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        left_frame.pack(side='left', fill='y', padx=10)
        
        # 파일 추가
        ctk.CTkButton(
            left_frame,
            text="📁 파일 추가",
            command=self._add_files,
            width=100,
            height=32
        ).pack(side='left', padx=(0, 5))
        
        # 폴더 추가
        ctk.CTkButton(
            left_frame,
            text="📂 폴더 추가",
            command=self._add_folder,
            width=100,
            height=32
        ).pack(side='left', padx=5)
        
        # 구분선
        separator = ctk.CTkFrame(left_frame, width=2, fg_color=self.colors['border'])
        separator.pack(side='left', fill='y', padx=10)
        
        # 일괄 작업
        ctk.CTkButton(
            left_frame,
            text="🔄 재처리",
            command=self._retry_selected,
            width=80,
            height=32,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=(0, 5))
        
        ctk.CTkButton(
            left_frame,
            text="🚫 취소",
            command=self._cancel_selected,
            width=80,
            height=32,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            left_frame,
            text="🗑️ 제거",
            command=self._remove_selected,
            width=80,
            height=32,
            fg_color=self.colors['bg_secondary']
        ).pack(side='left', padx=5)
        
        # 오른쪽 정보
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.pack(side='right', fill='y', padx=10)
        
        # 통계 정보
        self.stats_label = ctk.CTkLabel(
            right_frame,
            text="대기: 0 | 처리중: 0 | 완료: 0",
            font=('Arial', 12)
        )
        self.stats_label.pack(side='right')
        
        return toolbar
    
    def _create_filter_bar(self) -> ctk.CTkFrame:
        """필터 바 생성"""
        filter_bar = ctk.CTkFrame(self, fg_color=self.colors['bg_card'], height=40)
        
        # 상태 필터
        status_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        status_frame.pack(side='left', padx=10)
        
        ctk.CTkLabel(status_frame, text="상태:").pack(side='left', padx=(0, 5))
        
        status_menu = ctk.CTkOptionMenu(
            status_frame,
            variable=self.filter_status,
            values=["all", "waiting", "processing", "completed", "error"],
            command=self._apply_filters,
            width=120
        )
        status_menu.pack(side='left')
        
        # 검색
        search_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        search_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(search_frame, text="검색:").pack(side='left', padx=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            width=200
        )
        search_entry.pack(side='left')
        search_entry.bind('<KeyRelease>', lambda e: self._apply_filters())
        
        # 폴더 필터
        folder_frame = ctk.CTkFrame(filter_bar, fg_color="transparent")
        folder_frame.pack(side='left', padx=20)
        
        ctk.CTkLabel(folder_frame, text="폴더:").pack(side='left', padx=(0, 5))
        
        self.folder_menu = ctk.CTkOptionMenu(
            folder_frame,
            variable=self.folder_filter,
            values=["all"],
            command=self._apply_filters,
            width=150
        )
        self.folder_menu.pack(side='left')
        
        # 초기화 버튼
        ctk.CTkButton(
            filter_bar,
            text="🔄 초기화",
            command=self._reset_filters,
            width=80,
            height=28,
            fg_color=self.colors['bg_secondary']
        ).pack(side='right', padx=10)
        
        return filter_bar
    
    def _create_file_list(self) -> ctk.CTkFrame:
        """파일 리스트 생성"""
        list_frame = ctk.CTkFrame(self, fg_color=self.colors['bg_card'])
        
        # 트리뷰 컨테이너
        tree_container = ctk.CTkFrame(list_frame, fg_color="transparent")
        tree_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 트리뷰 생성
        columns = ['icon', 'filename', 'folder', 'profile', 'size', 
                  'pages', 'issues', 'score', 'time', 'status']
        
        self.tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show='tree headings',
            selectmode='extended'
        )
        
        # 컬럼 헤더 설정
        self.tree.heading('#0', text='☐', anchor='center')
        self.tree.heading('icon', text='')
        self.tree.heading('filename', text='파일명')
        self.tree.heading('folder', text='폴더')
        self.tree.heading('profile', text='프로파일')
        self.tree.heading('size', text='크기')
        self.tree.heading('pages', text='페이지')
        self.tree.heading('issues', text='문제')
        self.tree.heading('score', text='점수')
        self.tree.heading('time', text='처리시간')
        self.tree.heading('status', text='상태')
        
        # 컬럼 너비
        self.tree.column('#0', width=30, stretch=False)
        self.tree.column('icon', width=30, stretch=False)
        self.tree.column('filename', width=250)
        self.tree.column('folder', width=120)
        self.tree.column('profile', width=80)
        self.tree.column('size', width=80)
        self.tree.column('pages', width=60)
        self.tree.column('issues', width=100)
        self.tree.column('score', width=60)
        self.tree.column('time', width=100)
        self.tree.column('status', width=100)
        
        # 스크롤바
        v_scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 배치
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)
        
        # 이벤트 바인딩
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._show_context_menu)
        self.tree.bind('<Button-1>', self._on_tree_click)
        
        # 컨텍스트 메뉴
        self._create_context_menu()
        
        return list_frame
    
    def _create_info_bar(self) -> ctk.CTkFrame:
        """하단 정보 바 생성"""
        info_bar = ctk.CTkFrame(self, fg_color=self.colors['bg_card'], height=40)
        
        # 선택 정보
        self.selection_label = ctk.CTkLabel(
            info_bar,
            text="선택: 0개",
            font=('Arial', 11)
        )
        self.selection_label.pack(side='left', padx=10)
        
        # 처리 정보
        self.process_info_label = ctk.CTkLabel(
            info_bar,
            text="",
            font=('Arial', 11),
            text_color=self.colors['text_secondary']
        )
        self.process_info_label.pack(side='right', padx=10)
        
        return info_bar
    
    def _create_context_menu(self):
        """컨텍스트 메뉴 생성"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="📄 보고서 보기", command=self._view_report)
        self.context_menu.add_command(label="📁 폴더에서 보기", command=self._show_in_folder)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 다시 처리", command=self._retry_file)
        self.context_menu.add_command(label="🚫 처리 취소", command=self._cancel_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ 목록에서 제거", command=self._remove_file)
    
    def _setup_tree_style(self):
        """트리뷰 스타일 설정"""
        style = ttk.Style()
        
        # 다크 테마 스타일
        style.configure("Treeview",
                       background=self.colors['bg_secondary'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_secondary'],
                       borderwidth=0)
        
        style.configure("Treeview.Heading",
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       borderwidth=0)
        
        style.map("Treeview",
                 background=[('selected', self.colors['accent'])],
                 foreground=[('selected', 'white')])
        
        # 태그 스타일
        self.tree.tag_configure('waiting', foreground='#ffc107')
        self.tree.tag_configure('processing', foreground='#17a2b8')
        self.tree.tag_configure('success', foreground='#28a745')
        self.tree.tag_configure('error', foreground='#dc3545')
        self.tree.tag_configure('cancelled', foreground='#6c757d')
    
    def _setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        self.controller.set_ui_callbacks(
            on_file_added=self._on_file_added,
            on_file_status_changed=self._on_file_status_changed,
            on_file_progress=self._on_file_progress,
            on_file_completed=self._on_file_completed,
            on_file_error=self._on_file_error
        )
    
    # 콜백 메서드들
    
    def _on_file_added(self, file_item: FileItem):
        """파일 추가 콜백"""
        # 트리에 아이템 추가
        values = self._create_tree_values(file_item)
        
        self.tree.insert('', 'end',
                        iid=file_item.file_id,
                        text='☐',
                        values=values,
                        tags=(self.STATUS_TAGS[file_item.status],))
        
        # 폴더 필터 업데이트
        self._update_folder_filter(file_item)
        
        # 통계 업데이트
        self._update_statistics()
    
    def _on_file_status_changed(self, file_id: str, status: FileStatus):
        """파일 상태 변경 콜백"""
        if self.tree.exists(file_id):
            # 아이콘 업데이트
            values = list(self.tree.item(file_id)['values'])
            values[0] = self.STATUS_ICONS[status]
            values[9] = self._get_status_text(status)
            
            self.tree.item(file_id, values=values, tags=(self.STATUS_TAGS[status],))
            
            # 통계 업데이트
            self._update_statistics()
    
    def _on_file_progress(self, file_id: str, progress: int, message: str):
        """파일 진행률 콜백"""
        if self.tree.exists(file_id):
            values = list(self.tree.item(file_id)['values'])
            values[9] = f"{message} ({progress}%)"
            self.tree.item(file_id, values=values)
    
    def _on_file_completed(self, file_id: str, file_item: FileItem):
        """파일 완료 콜백"""
        if self.tree.exists(file_id):
            # update_file_complete 메서드 사용
            self.update_file_complete(file_id, file_item)
            return
        
        # 트리에 아이템이 없으면 기존 코드 실행
        if self.tree.exists(file_id):
            values = self._create_tree_values(file_item)
            self.tree.item(file_id, values=values, 
                          tags=(self.STATUS_TAGS[file_item.status],))
            
            # 통계 업데이트
            self._update_statistics()
    
    def _on_file_error(self, file_id: str, error: str):
        """파일 오류 콜백"""
        if self.tree.exists(file_id):
            values = list(self.tree.item(file_id)['values'])
            values[0] = self.STATUS_ICONS[FileStatus.ERROR]
            values[9] = f"오류: {error[:30]}..."
            self.tree.item(file_id, values=values, tags=('error',))
            
            # 통계 업데이트
            self._update_statistics()
    
    # UI 이벤트 핸들러
    
    def _add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if files:
            file_paths = [Path(f) for f in files]
            self.controller.add_files(file_paths)
    
    def _add_folder(self):
        """폴더 추가"""
        folder = filedialog.askdirectory(title="PDF 파일이 있는 폴더 선택")
        
        if folder:
            folder_path = Path(folder)
            pdf_files = list(folder_path.glob("*.pdf"))
            
            if pdf_files:
                self.controller.add_files(pdf_files)
                messagebox.showinfo("폴더 추가", 
                                  f"{len(pdf_files)}개의 PDF 파일을 추가했습니다.")
            else:
                messagebox.showwarning("폴더 추가", 
                                     "선택한 폴더에 PDF 파일이 없습니다.")
    
    def _retry_selected(self):
        """선택 파일 재처리"""
        for file_id in self.selected_items:
            self.controller.retry_file(file_id)
    
    def _cancel_selected(self):
        """선택 파일 취소"""
        for file_id in self.selected_items:
            self.controller.cancel_file(file_id)
    
    def _remove_selected(self):
        """선택 파일 제거"""
        if messagebox.askyesno("확인", f"{len(self.selected_items)}개 파일을 목록에서 제거하시겠습니까?"):
            for file_id in self.selected_items.copy():
                self.tree.delete(file_id)
                self.selected_items.discard(file_id)
            
            self._update_statistics()
            self._update_selection_info()
    
    def _on_tree_click(self, event):
        """트리 클릭 이벤트"""
        # 체크박스 영역 클릭 확인
        region = self.tree.identify_region(event.x, event.y)
        if region == "tree":
            item = self.tree.identify_row(event.y)
            if item:
                # 체크박스 토글
                if item in self.selected_items:
                    self.selected_items.discard(item)
                    self.tree.item(item, text='☐')
                else:
                    self.selected_items.add(item)
                    self.tree.item(item, text='☑')
                
                self._update_selection_info()
    
    def _on_double_click(self, event):
        """더블클릭 이벤트"""
        item = self.tree.identify_row(event.y)
        if item:
            self._view_report_for_item(item)
    
    def _show_context_menu(self, event):
        """컨텍스트 메뉴 표시"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _view_report(self):
        """보고서 보기"""
        selection = self.tree.selection()
        if selection:
            self._view_report_for_item(selection[0])
    
    def _view_report_for_item(self, file_id: str):
        """특정 아이템의 보고서 보기"""
        file_item = self.controller.get_file_item(file_id)
        if file_item and file_item.report_paths:
            # HTML 보고서 우선
            if 'html' in file_item.report_paths:
                import webbrowser
                webbrowser.open(str(file_item.report_paths['html']))
    
    def _show_in_folder(self):
        """폴더에서 보기"""
        selection = self.tree.selection()
        if selection:
            file_item = self.controller.get_file_item(selection[0])
            if file_item:
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', '/select,', str(file_item.path)])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', '-R', str(file_item.path)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(file_item.path.parent)])
    
    def _retry_file(self):
        """파일 재처리"""
        selection = self.tree.selection()
        if selection:
            self.controller.retry_file(selection[0])
    
    def _cancel_file(self):
        """파일 처리 취소"""
        selection = self.tree.selection()
        if selection:
            self.controller.cancel_file(selection[0])
    
    def _remove_file(self):
        """파일 제거"""
        selection = self.tree.selection()
        if selection and messagebox.askyesno("확인", "선택한 파일을 목록에서 제거하시겠습니까?"):
            for item in selection:
                self.tree.delete(item)
                self.selected_items.discard(item)
            
            self._update_statistics()
    
    # 파일 추가 및 업데이트
    
    def add_file(self, file_item):
        """파일 추가"""
        # 상태 아이콘 매핑
        status_icons = {
            'waiting': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'error': '❌',
            'cancelled': '⛔'
        }
        
        # 트리에 아이템 추가
        values = [
            status_icons.get(file_item.status.value, ''),  # icon
            file_item.filename,  # filename
            file_item.folder_name or '수동 추가',  # folder
            file_item.profile,  # profile
            f"{file_item.size_mb:.1f} MB",  # size
            '',  # pages (나중에 업데이트)
            '',  # issues (나중에 업데이트)
            '',  # score (나중에 업데이트)
            '',  # time (나중에 업데이트)
            file_item.status.value  # status
        ]
        
        self.tree.insert('', 'end', file_item.file_id, text='☐', values=values)
        self._update_statistics()
    
    def update_file_status(self, file_id: str, status):
        """파일 상태 업데이트"""
        if not self.tree.exists(file_id):
            return
        
        # 상태 아이콘 매핑
        status_icons = {
            'waiting': '⏳',
            'processing': '🔄',
            'completed': '✅',
            'error': '❌',
            'cancelled': '⛔'
        }
        
        # 현재 값 가져오기
        values = list(self.tree.item(file_id, 'values'))
        values[0] = status_icons.get(status.value, '')  # icon 업데이트
        values[9] = status.value  # status 업데이트
        
        self.tree.item(file_id, values=values)
        self._update_statistics()
    
    def update_file_progress(self, file_id: str, progress: int, message: str):
        """파일 진행률 업데이트"""
        if not self.tree.exists(file_id):
            return
        
        # 진행률을 상태 컬럼에 표시
        values = list(self.tree.item(file_id, 'values'))
        values[9] = f"처리중 {progress}%"
        self.tree.item(file_id, values=values)
    
    def update_file_complete(self, file_id: str, file_item):
        """파일 처리 완료 업데이트"""
        if not self.tree.exists(file_id):
            return
        
        # 상태 아이콘
        status_icon = '✅' if file_item.status.value == 'completed' else '❌'
        
        # 문제 표시
        issues_text = ''
        if file_item.error_count > 0:
            issues_text = f"🔴 {file_item.error_count}"
        if file_item.warning_count > 0:
            issues_text += f" 🟡 {file_item.warning_count}"
        if not issues_text:
            issues_text = '✅ 없음'
        
        # 처리 시간 포맷
        time_text = f"{file_item.processing_time:.1f}초" if file_item.processing_time else ''
        
        # 점수 표시
        score_text = f"{file_item.quality_score:.0f}" if file_item.quality_score else ''
        
        values = [
            status_icon,  # icon
            file_item.filename,  # filename
            file_item.folder_name or '수동 추가',  # folder
            file_item.profile,  # profile
            f"{file_item.size_mb:.1f} MB",  # size
            '',  # pages (TODO: 페이지 수 추가)
            issues_text,  # issues
            score_text,  # score
            time_text,  # time
            file_item.status.value  # status
        ]
        
        self.tree.item(file_id, values=values)
        self._update_statistics()
    
    # 필터링
    
    def _apply_filters(self, *args):
        """필터 적용"""
        # 모든 아이템 가져오기
        all_items = self.tree.get_children()
        
        # 필터 조건
        status_filter = self.filter_status.get()
        search_text = self.search_var.get().lower()
        folder_filter = self.folder_filter.get()
        
        for item_id in all_items:
            file_item = self.controller.get_file_item(item_id)
            if not file_item:
                continue
            
            show = True
            
            # 상태 필터
            if status_filter != "all":
                if status_filter == "waiting" and file_item.status != FileStatus.WAITING:
                    show = False
                elif status_filter == "processing" and file_item.status != FileStatus.PROCESSING:
                    show = False
                elif status_filter == "completed" and file_item.status != FileStatus.COMPLETED:
                    show = False
                elif status_filter == "error" and file_item.status != FileStatus.ERROR:
                    show = False
            
            # 검색 필터
            if show and search_text:
                if search_text not in file_item.filename.lower():
                    show = False
            
            # 폴더 필터
            if show and folder_filter != "all":
                if file_item.folder_name != folder_filter:
                    show = False
            
            # 표시/숨김
            if show:
                self.tree.reattach(item_id, '', 'end')
            else:
                self.tree.detach(item_id)
    
    def _reset_filters(self):
        """필터 초기화"""
        self.filter_status.set("all")
        self.search_var.set("")
        self.folder_filter.set("all")
        self._apply_filters()
    
    # 유틸리티 메서드
    
    def _create_tree_values(self, file_item: FileItem) -> List[str]:
        """트리 아이템 값 생성"""
        return [
            self.STATUS_ICONS[file_item.status],  # icon
            file_item.filename,                    # filename
            file_item.folder_name or "-",          # folder
            file_item.profile,                     # profile
            f"{file_item.size_mb:.1f} MB",       # size
            "-",                                   # pages (TODO)
            self._format_issues(file_item),        # issues
            f"{file_item.quality_score:.0f}" if file_item.quality_score > 0 else "-",  # score
            self._format_time(file_item),          # time
            self._get_status_text(file_item.status)  # status
        ]
    
    def _format_issues(self, file_item: FileItem) -> str:
        """이슈 포맷팅"""
        if file_item.error_count > 0 or file_item.warning_count > 0:
            return f"오류:{file_item.error_count} 경고:{file_item.warning_count}"
        return "-"
    
    def _format_time(self, file_item: FileItem) -> str:
        """시간 포맷팅"""
        if file_item.processing_time > 0:
            return f"{file_item.processing_time:.1f}초"
        elif file_item.start_time:
            return file_item.start_time.strftime("%H:%M:%S")
        return "-"
    
    def _get_status_text(self, status: FileStatus) -> str:
        """상태 텍스트"""
        status_texts = {
            FileStatus.WAITING: "대기 중",
            FileStatus.PROCESSING: "처리 중",
            FileStatus.COMPLETED: "완료",
            FileStatus.ERROR: "오류",
            FileStatus.CANCELLED: "취소됨"
        }
        return status_texts.get(status, "-")
    
    def _update_folder_filter(self, file_item: FileItem):
        """폴더 필터 업데이트"""
        if file_item.folder_name:
            current_values = list(self.folder_menu.cget("values"))
            if file_item.folder_name not in current_values:
                current_values.append(file_item.folder_name)
                self.folder_menu.configure(values=current_values)
    
    def _update_statistics(self):
        """통계 업데이트"""
        stats = self.controller.get_statistics()
        
        waiting = stats['by_status'].get('waiting', 0)
        processing = stats['by_status'].get('processing', 0)
        completed = stats['by_status'].get('completed', 0)
        
        self.stats_label.configure(
            text=f"대기: {waiting} | 처리중: {processing} | 완료: {completed}"
        )
    
    def _update_selection_info(self):
        """선택 정보 업데이트"""
        count = len(self.selected_items)
        self.selection_label.configure(text=f"선택: {count}개")
    
    def refresh(self):
        """화면 새로고침"""
        # 통계 업데이트
        self._update_statistics()
        
        # 필터 재적용
        self._apply_filters()
    
    def clear_completed(self):
        """완료 항목 정리"""
        if messagebox.askyesno("확인", "완료된 항목을 모두 제거하시겠습니까?"):
            completed_items = []
            for item_id in self.tree.get_children():
                file_item = self.controller.get_file_item(item_id)
                if file_item and file_item.status == FileStatus.COMPLETED:
                    completed_items.append(item_id)
            
            for item_id in completed_items:
                self.tree.delete(item_id)
                self.selected_items.discard(item_id)
            
            self.controller.clear_completed()
            self._update_statistics()
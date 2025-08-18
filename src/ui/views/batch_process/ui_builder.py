"""
일괄 처리 UI 빌더
기능: 일괄 처리 창의 UI 구성 요소 생성
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import BatchProcessView


class UIBuilder:
    """UI 생성 헬퍼 클래스"""
    
    def __init__(self, view: 'BatchProcessView'):
        self.view = view
        
    def create_ui(self):
        """전체 UI 구성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.view)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        self.view.widgets['main_frame'] = main_frame
        
        # 상단: 파일 선택 영역
        self._create_top_section(main_frame)
        
        # 중단: 파일 목록 및 설정
        self._create_middle_section(main_frame)
        
        # 하단: 진행 상황 및 컨트롤
        self._create_bottom_section(main_frame)
    
    def _create_top_section(self, parent):
        """상단 섹션 - 파일 선택 영역"""
        top_frame = ctk.CTkFrame(parent)
        top_frame.pack(fill='x', pady=(0, 10))
        
        # 제목
        title_label = ctk.CTkLabel(
            top_frame,
            text="일괄 처리",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 파일 선택 버튼들
        button_frame = ctk.CTkFrame(top_frame)
        button_frame.pack()
        
        add_files_btn = ctk.CTkButton(
            button_frame,
            text="파일 추가",
            command=self.view.add_files,
            width=120
        )
        add_files_btn.pack(side='left', padx=5)
        self.view.widgets['add_files_btn'] = add_files_btn
        
        add_folder_btn = ctk.CTkButton(
            button_frame,
            text="폴더 추가",
            command=self.view.add_folder,
            width=120
        )
        add_folder_btn.pack(side='left', padx=5)
        self.view.widgets['add_folder_btn'] = add_folder_btn
        
        clear_btn = ctk.CTkButton(
            button_frame,
            text="목록 초기화",
            command=self.view.clear_list,
            width=120,
            fg_color="gray"
        )
        clear_btn.pack(side='left', padx=5)
        self.view.widgets['clear_btn'] = clear_btn
    
    def _create_middle_section(self, parent):
        """중단 섹션 - 파일 목록 및 설정"""
        middle_frame = ctk.CTkFrame(parent)
        middle_frame.pack(fill='both', expand=True, pady=10)
        
        # 좌측: 파일 목록
        self._create_file_list(middle_frame)
        
        # 우측: 처리 설정
        self._create_settings(middle_frame)
    
    def _create_file_list(self, parent):
        """파일 목록 생성"""
        left_frame = ctk.CTkFrame(parent)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        list_label = ctk.CTkLabel(
            left_frame,
            text="처리할 파일 목록",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        list_label.pack(pady=5)
        
        # 파일 수 레이블
        file_count_label = ctk.CTkLabel(
            left_frame,
            text="0개 파일",
            text_color="gray"
        )
        file_count_label.pack()
        self.view.widgets['file_count_label'] = file_count_label
        
        # 파일 리스트 프레임
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 파일 트리뷰
        file_tree = ttk.Treeview(
            list_frame,
            columns=('size', 'pages', 'status'),
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        file_tree.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=file_tree.yview)
        
        # 컬럼 설정
        file_tree.heading('#0', text='파일명')
        file_tree.heading('size', text='크기')
        file_tree.heading('pages', text='페이지')
        file_tree.heading('status', text='상태')
        
        file_tree.column('#0', width=400)
        file_tree.column('size', width=80)
        file_tree.column('pages', width=60)
        file_tree.column('status', width=100)
        
        # 트리 스타일
        style = ttk.Style()
        style.configure("Treeview",
                       background="#2b2b2b",
                       foreground="white",
                       fieldbackground="#2b2b2b")
        
        self.view.widgets['file_tree'] = file_tree
    
    def _create_settings(self, parent):
        """처리 설정 생성"""
        right_frame = ctk.CTkFrame(parent, width=350)
        right_frame.pack(side='right', fill='y', padx=(5, 0))
        right_frame.pack_propagate(False)
        
        settings_label = ctk.CTkLabel(
            right_frame,
            text="처리 설정",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        settings_label.pack(pady=10)
        
        # 설정 스크롤 프레임
        settings_scroll = ctk.CTkScrollableFrame(right_frame)
        settings_scroll.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 프로파일 선택
        self._create_profile_selection(settings_scroll)
        
        # 출력 설정
        self._create_output_settings(settings_scroll)
        
        # 처리 옵션
        self._create_process_options(settings_scroll)
    
    def _create_profile_selection(self, parent):
        """프로파일 선택 UI"""
        profile_label = ctk.CTkLabel(parent, text="검사 프로파일:")
        profile_label.pack(anchor='w', pady=(10, 5))
        
        profiles = self.view.profile_controller.get_profile_list()
        profile_names = [p.name for p in profiles]
        
        profile_combo = ctk.CTkComboBox(
            parent,
            values=profile_names,
            width=300
        )
        profile_combo.pack(fill='x', pady=(0, 10))
        
        current_profile, _ = self.view.profile_controller.get_current_profile()
        profile_combo.set(current_profile)
        
        self.view.widgets['profile_combo'] = profile_combo
    
    def _create_output_settings(self, parent):
        """출력 설정 UI"""
        output_label = ctk.CTkLabel(
            parent,
            text="출력 설정",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        output_label.pack(anchor='w', pady=(20, 5))
        
        # 출력 폴더
        output_folder_label = ctk.CTkLabel(parent, text="출력 폴더:")
        output_folder_label.pack(anchor='w', pady=(5, 2))
        
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill='x', pady=(0, 10))
        
        output_entry = ctk.CTkEntry(output_frame, width=220)
        output_entry.pack(side='left', padx=(0, 5))
        output_entry.insert(0, "output")
        self.view.widgets['output_entry'] = output_entry
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="찾기",
            command=self.view.file_manager.browse_output if hasattr(self.view, 'file_manager') else None,
            width=60
        )
        browse_btn.pack(side='left')
        
        # 파일 구성
        keep_structure = ctk.CTkCheckBox(
            parent,
            text="원본 폴더 구조 유지"
        )
        keep_structure.pack(anchor='w', pady=5)
        self.view.widgets['keep_structure'] = keep_structure
        
        create_subfolders = ctk.CTkCheckBox(
            parent,
            text="파일별 하위 폴더 생성"
        )
        create_subfolders.pack(anchor='w', pady=5)
        self.view.widgets['create_subfolders'] = create_subfolders
    
    def _create_process_options(self, parent):
        """처리 옵션 UI"""
        options_label = ctk.CTkLabel(
            parent,
            text="처리 옵션",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        options_label.pack(anchor='w', pady=(20, 5))
        
        # 처리 옵션들
        auto_fix = ctk.CTkCheckBox(parent, text="자동 수정 적용")
        auto_fix.pack(anchor='w', pady=5)
        self.view.widgets['auto_fix'] = auto_fix
        
        generate_report = ctk.CTkCheckBox(parent, text="보고서 생성", state='normal')
        generate_report.select()
        generate_report.pack(anchor='w', pady=5)
        self.view.widgets['generate_report'] = generate_report
        
        stop_on_error = ctk.CTkCheckBox(parent, text="오류 시 중지")
        stop_on_error.pack(anchor='w', pady=5)
        self.view.widgets['stop_on_error'] = stop_on_error
    
    def _create_bottom_section(self, parent):
        """하단 섹션 - 진행 상황 및 컨트롤"""
        bottom_frame = ctk.CTkFrame(parent)
        bottom_frame.pack(fill='x', pady=(10, 0))
        
        # 진행 상황
        progress_label = ctk.CTkLabel(
            bottom_frame,
            text="진행 상황",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        progress_label.pack(pady=5)
        
        # 진행률 바
        progress_bar = ctk.CTkProgressBar(bottom_frame, width=800)
        progress_bar.pack(pady=10)
        progress_bar.set(0)
        self.view.widgets['progress_bar'] = progress_bar
        
        # 상태 레이블
        status_label = ctk.CTkLabel(
            bottom_frame,
            text="대기 중",
            text_color="gray"
        )
        status_label.pack(pady=5)
        self.view.widgets['status_label'] = status_label
        
        # 컨트롤 버튼
        control_frame = ctk.CTkFrame(bottom_frame)
        control_frame.pack(pady=10)
        
        start_btn = ctk.CTkButton(
            control_frame,
            text="처리 시작",
            command=self.view.start_process,
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        start_btn.pack(side='left', padx=10)
        self.view.widgets['start_btn'] = start_btn
        
        cancel_btn = ctk.CTkButton(
            control_frame,
            text="취소",
            command=self.view.cancel_process,
            width=100,
            height=40,
            fg_color="gray",
            state='disabled'
        )
        cancel_btn.pack(side='left', padx=10)
        self.view.widgets['cancel_btn'] = cancel_btn
"""
UI 빌더 - 폴더 관리 UI 구성
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import FolderManagerView


class UIBuilder:
    """UI 빌더"""
    
    def __init__(self, view: 'FolderManagerView'):
        self.view = view
    
    def create_ui(self):
        """UI 생성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self.view)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 좌측: 폴더 목록
        self._create_folder_list(main_frame)
        
        # 우측: 폴더 설정
        self._create_settings_panel(main_frame)
    
    def _create_folder_list(self, parent):
        """폴더 목록 생성"""
        left_frame = ctk.CTkFrame(parent, width=300)
        left_frame.pack(side='left', fill='both', padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # 폴더 목록 레이블
        list_label = ctk.CTkLabel(left_frame, text="감시 폴더 목록", font=("", 14, "bold"))
        list_label.pack(pady=10)
        
        # 폴더 리스트박스
        folder_listbox = tk.Listbox(
            left_frame,
            selectmode='single',
            bg='#2b2b2b',
            fg='white',
            selectbackground='#667eea',
            font=("", 10)
        )
        folder_listbox.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        folder_listbox.bind('<<ListboxSelect>>', self._on_folder_select)
        self.view.widgets['folder_listbox'] = folder_listbox
        
        # 폴더 추가/제거 버튼
        button_frame = ctk.CTkFrame(left_frame)
        button_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="폴더 추가",
            command=self.view.add_folder,
            width=100
        )
        add_btn.pack(side='left', padx=(0, 5))
        
        remove_btn = ctk.CTkButton(
            button_frame,
            text="폴더 제거",
            command=self.view.remove_folder,
            width=100
        )
        remove_btn.pack(side='left')
    
    def _create_settings_panel(self, parent):
        """설정 패널 생성"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 설정 레이블
        settings_label = ctk.CTkLabel(right_frame, text="폴더 설정", font=("", 14, "bold"))
        settings_label.pack(pady=10)
        
        # 탭뷰
        tabview = ctk.CTkTabview(right_frame)
        tabview.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        self.view.widgets['tabview'] = tabview
        
        # 탭 추가
        tabview.add("기본 설정")
        tabview.add("체크 설정")
        tabview.add("수정 설정")
        tabview.add("리포트")
        
        # 각 탭 내용 생성
        self._create_basic_settings(tabview.tab("기본 설정"))
        self._create_check_settings(tabview.tab("체크 설정"))
        self._create_fix_settings(tabview.tab("수정 설정"))
        self._create_report_settings(tabview.tab("리포트"))
        
        # 저장 버튼
        save_btn = ctk.CTkButton(
            right_frame,
            text="설정 저장",
            command=self.view.save_settings,
            height=35
        )
        save_btn.pack(fill='x', padx=10, pady=(0, 10))
    
    def _create_basic_settings(self, parent):
        """기본 설정 탭"""
        # 활성화 체크박스
        self.view.widgets['enabled'] = ctk.CTkCheckBox(parent, text="폴더 감시 활성화")
        self.view.widgets['enabled'].pack(anchor='w', padx=20, pady=(20, 10))
        
        # 자동 처리
        self.view.widgets['auto_process'] = ctk.CTkCheckBox(parent, text="파일 발견 시 자동 처리")
        self.view.widgets['auto_process'].pack(anchor='w', padx=20, pady=10)
        
        # 출력 폴더
        output_frame = ctk.CTkFrame(parent)
        output_frame.pack(fill='x', padx=20, pady=10)
        
        ctk.CTkLabel(output_frame, text="출력 폴더:").pack(side='left', padx=(0, 10))
        
        self.view.widgets['output_folder'] = ctk.CTkEntry(output_frame, width=300)
        self.view.widgets['output_folder'].pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            output_frame,
            text="찾아보기",
            command=self.view.browse_output_folder,
            width=80
        )
        browse_btn.pack(side='right')
        
        # 프로파일 선택
        profile_frame = ctk.CTkFrame(parent)
        profile_frame.pack(fill='x', padx=20, pady=10)
        
        ctk.CTkLabel(profile_frame, text="프로파일:").pack(side='left', padx=(0, 10))
        
        self.view.widgets['profile'] = ctk.CTkOptionMenu(
            profile_frame,
            values=["기본", "인쇄용", "웹용", "아카이브"],
            width=200
        )
        self.view.widgets['profile'].pack(side='left')
        
        # 파일 패턴
        pattern_frame = ctk.CTkFrame(parent)
        pattern_frame.pack(fill='x', padx=20, pady=10)
        
        ctk.CTkLabel(pattern_frame, text="파일 패턴:").pack(side='left', padx=(0, 10))
        
        self.view.widgets['file_pattern'] = ctk.CTkEntry(pattern_frame, placeholder_text="*.pdf")
        self.view.widgets['file_pattern'].pack(side='left', fill='x', expand=True)
    
    def _create_check_settings(self, parent):
        """체크 설정 탭"""
        # 스크롤 가능한 프레임
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True)
        
        # 체크 항목들
        check_items = [
            ("check_images", "이미지 품질 체크"),
            ("check_fonts", "폰트 임베딩 체크"),
            ("check_colors", "색상 프로파일 체크"),
            ("check_resolution", "해상도 체크"),
            ("check_bleed", "재단선 체크"),
            ("check_transparency", "투명도 체크"),
            ("check_layers", "레이어 체크"),
            ("check_annotations", "주석 체크")
        ]
        
        for key, text in check_items:
            self.view.widgets[key] = ctk.CTkCheckBox(scroll_frame, text=text)
            self.view.widgets[key].pack(anchor='w', padx=20, pady=5)
    
    def _create_fix_settings(self, parent):
        """수정 설정 탭"""
        # 자동 수정 활성화
        self.view.widgets['auto_fix'] = ctk.CTkCheckBox(parent, text="자동 수정 활성화")
        self.view.widgets['auto_fix'].pack(anchor='w', padx=20, pady=(20, 10))
        
        # 수정 옵션들
        fix_frame = ctk.CTkFrame(parent)
        fix_frame.pack(fill='x', padx=40, pady=10)
        
        fix_options = [
            ("fix_images", "이미지 최적화"),
            ("fix_fonts", "폰트 임베딩"),
            ("fix_colors", "색상 변환"),
            ("fix_compression", "압축 최적화")
        ]
        
        for key, text in fix_options:
            self.view.widgets[key] = ctk.CTkCheckBox(fix_frame, text=text)
            self.view.widgets[key].pack(anchor='w', pady=5)
    
    def _create_report_settings(self, parent):
        """리포트 설정 탭"""
        # 리포트 생성
        self.view.widgets['generate_report'] = ctk.CTkCheckBox(
            parent, 
            text="처리 후 리포트 생성",
            command=self.view.toggle_report_formats
        )
        self.view.widgets['generate_report'].pack(anchor='w', padx=20, pady=(20, 10))
        
        # 리포트 형식
        format_frame = ctk.CTkFrame(parent)
        format_frame.pack(fill='x', padx=40, pady=10)
        self.view.widgets['format_frame'] = format_frame
        
        ctk.CTkLabel(format_frame, text="리포트 형식:").pack(anchor='w', pady=(0, 5))
        
        report_formats = [
            ("report_pdf", "PDF"),
            ("report_html", "HTML"),
            ("report_excel", "Excel"),
            ("report_json", "JSON")
        ]
        
        for key, text in report_formats:
            self.view.widgets[key] = ctk.CTkCheckBox(format_frame, text=text)
            self.view.widgets[key].pack(anchor='w', pady=2)
        
        # 이메일 알림
        email_frame = ctk.CTkFrame(parent)
        email_frame.pack(fill='x', padx=20, pady=20)
        
        self.view.widgets['send_email'] = ctk.CTkCheckBox(email_frame, text="이메일 알림")
        self.view.widgets['send_email'].pack(anchor='w', pady=(0, 10))
        
        ctk.CTkLabel(email_frame, text="수신자:").pack(anchor='w', padx=20)
        
        self.view.widgets['email_recipients'] = ctk.CTkTextbox(email_frame, height=60)
        self.view.widgets['email_recipients'].pack(fill='x', padx=20, pady=(5, 0))
    
    def _on_folder_select(self, event):
        """폴더 선택 이벤트"""
        listbox = self.view.widgets.get('folder_listbox')
        if listbox:
            selection = listbox.curselection()
            if selection:
                folder_path = listbox.get(selection[0])
                self.view.on_folder_select(folder_path)
# src/ui/views/settings_v2/categories/processing_category.py
"""
처리 설정 카테고리

프로파일, 자동 처리, 보고서, 폴더 경로 설정 관리
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Dict, Any
from pathlib import Path
from ..base_category import BaseCategory


class ProcessingCategory(BaseCategory):
    """
    처리 설정 카테고리
    
    - 프로파일 관리
    - 자동 처리 옵션
    - 보고서 설정
    - 폴더 경로 설정
    """
    
    def _create_ui(self):
        """UI 생성"""
        # 프로파일 설정 섹션
        self._create_profile_section()
        
        # 자동 처리 섹션
        self._create_auto_processing_section()
        
        # 보고서 설정 섹션
        self._create_report_section()
        
        # 폴더 경로 섹션
        self._create_folder_section()
    
    def _create_profile_section(self):
        """프로파일 설정 섹션"""
        section = self.create_section("프로파일 설정", "👤")
        
        # 기본 프로파일
        self.create_option_row(
            section,
            "기본 프로파일:",
            "combobox",
            "default_profile",
            values=["default", "quick", "strict", "custom"]
        )
        
        # 프로파일 관리 버튼
        btn_frame = ctk.CTkFrame(section, fg_color="transparent")
        btn_frame.pack(fill='x', pady=10)
        
        ctk.CTkLabel(
            btn_frame,
            text="",
            width=200
        ).pack(side='left', padx=(0, 20))
        
        manage_btn = ctk.CTkButton(
            btn_frame,
            text="프로파일 관리...",
            width=150,
            command=self._open_profile_manager
        )
        manage_btn.pack(side='left')
    
    def _create_auto_processing_section(self):
        """자동 처리 섹션"""
        section = self.create_section("자동 처리", "⚡")
        
        # 자동 수정
        self.create_option_row(
            section,
            "검사 후 자동으로 문제 수정:",
            "switch",
            "auto_fix_enabled"
        )
        
        # 수정 레벨
        fix_level_frame = ctk.CTkFrame(section, fg_color="transparent")
        fix_level_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            fix_level_frame,
            text="자동 수정 레벨:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.fix_level_var = ctk.StringVar(value="안전")
        fix_level_menu = ctk.CTkSegmentedButton(
            fix_level_frame,
            values=["안전", "보통", "적극적"],
            variable=self.fix_level_var,
            command=lambda v: self._on_widget_change("auto_fix_level", v)
        )
        fix_level_menu.pack(side='left')
        self.widgets['auto_fix_level'] = fix_level_menu
        
        # 완료 파일 이동
        self.create_option_row(
            section,
            "처리 완료된 파일 자동 이동:",
            "switch",
            "move_completed_files"
        )
        
        # 백업 생성
        self.create_option_row(
            section,
            "수정 전 백업 생성:",
            "switch",
            "create_backup"
        )
    
    def _create_report_section(self):
        """보고서 설정 섹션"""
        section = self.create_section("보고서", "📊")
        
        # 보고서 자동 생성
        self.create_option_row(
            section,
            "처리 완료 후 보고서 자동 생성:",
            "switch",
            "generate_report"
        )
        
        # 보고서 형식
        format_frame = ctk.CTkFrame(section, fg_color="transparent")
        format_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            format_frame,
            text="보고서 형식:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        # 체크박스 프레임
        checkbox_frame = ctk.CTkFrame(format_frame, fg_color="transparent")
        checkbox_frame.pack(side='left')
        
        self.format_checkboxes = {}
        formats = ["HTML", "PDF", "Excel", "JSON"]
        for fmt in formats:
            cb = ctk.CTkCheckBox(
                checkbox_frame,
                text=fmt,
                width=80,
                command=lambda f=fmt.lower(): self._on_report_format_change(f)
            )
            cb.pack(side='left', padx=5)
            self.format_checkboxes[fmt.lower()] = cb
            self.widgets[f'report_format_{fmt.lower()}'] = cb
        
        # 보고서 상세도
        detail_frame = ctk.CTkFrame(section, fg_color="transparent")
        detail_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            detail_frame,
            text="보고서 상세도:",
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        self.detail_var = ctk.StringVar(value="표준")
        detail_menu = ctk.CTkSegmentedButton(
            detail_frame,
            values=["간단", "표준", "상세"],
            variable=self.detail_var,
            command=lambda v: self._on_widget_change("report_detail_level", v)
        )
        detail_menu.pack(side='left')
        self.widgets['report_detail_level'] = detail_menu
    
    def _create_folder_section(self):
        """폴더 경로 섹션"""
        section = self.create_section("폴더 경로", "📁")
        
        # 출력 폴더
        self._create_folder_row(
            section,
            "출력 폴더:",
            "default_output_folder"
        )
        
        # 완료 폴더
        self._create_folder_row(
            section,
            "완료 폴더:",
            "default_completed_folder"
        )
        
        # 백업 폴더
        self._create_folder_row(
            section,
            "백업 폴더:",
            "backup_folder"
        )
        
        # 임시 폴더
        self._create_folder_row(
            section,
            "임시 폴더:",
            "temp_folder"
        )
    
    def _create_folder_row(self, parent, label: str, widget_id: str):
        """폴더 선택 행 생성"""
        row_frame = ctk.CTkFrame(parent, fg_color="transparent")
        row_frame.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            row_frame,
            text=label,
            width=200,
            anchor='w'
        ).pack(side='left', padx=(0, 20))
        
        # 경로 입력 필드
        entry = ctk.CTkEntry(
            row_frame,
            width=250,
            height=32,
            placeholder_text="폴더를 선택하세요..."
        )
        entry.pack(side='left', padx=(0, 10))
        self.widgets[widget_id] = entry
        
        # 찾아보기 버튼
        browse_btn = ctk.CTkButton(
            row_frame,
            text="찾아보기...",
            width=80,
            command=lambda: self._browse_folder(widget_id)
        )
        browse_btn.pack(side='left')
    
    def _browse_folder(self, widget_id: str):
        """폴더 찾아보기"""
        folder = filedialog.askdirectory(
            title="폴더 선택",
            initialdir=Path.home()
        )
        
        if folder:
            entry = self.widgets.get(widget_id)
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, folder)
                self._on_widget_change(widget_id, folder)
    
    def _open_profile_manager(self):
        """프로파일 관리자 열기"""
        # 이벤트 발행 또는 콜백 호출
        if hasattr(self, 'settings_controller'):
            # 프로파일 관리 다이얼로그 열기
            from tkinter import messagebox
            messagebox.showinfo("프로파일 관리", "프로파일 관리 창이 열립니다.")
    
    def _on_report_format_change(self, format_type: str):
        """보고서 형식 변경"""
        # 선택된 형식들 수집
        formats = []
        for fmt, checkbox in self.format_checkboxes.items():
            if checkbox.get():
                formats.append(fmt)
        
        self._on_widget_change("report_formats", formats)
    
    def load_settings(self, settings):
        """설정 로드"""
        # 프로파일
        if hasattr(settings, 'default_profile'):
            self.widgets['default_profile'].set(settings.default_profile)
        
        # 자동 처리
        if hasattr(settings, 'auto_fix_enabled'):
            if settings.auto_fix_enabled:
                self.widgets['auto_fix_enabled'].select()
            else:
                self.widgets['auto_fix_enabled'].deselect()
        
        if hasattr(settings, 'auto_fix_level'):
            self.widgets['auto_fix_level'].set(settings.auto_fix_level)
        else:
            self.widgets['auto_fix_level'].set("안전")
        
        if hasattr(settings, 'move_completed_files'):
            if settings.move_completed_files:
                self.widgets['move_completed_files'].select()
            else:
                self.widgets['move_completed_files'].deselect()
        
        if hasattr(settings, 'create_backup'):
            if 'create_backup' in self.widgets:
                if settings.create_backup:
                    self.widgets['create_backup'].select()
                else:
                    self.widgets['create_backup'].deselect()
        elif 'create_backup' in self.widgets:
            self.widgets['create_backup'].select()  # 기본값
        
        # 보고서
        if hasattr(settings, 'generate_report'):
            if settings.generate_report:
                self.widgets['generate_report'].select()
            else:
                self.widgets['generate_report'].deselect()
        
        if hasattr(settings, 'report_formats'):
            for fmt in ['html', 'pdf', 'excel', 'json']:
                checkbox = self.format_checkboxes.get(fmt)
                if checkbox:
                    if fmt in settings.report_formats:
                        checkbox.select()
                    else:
                        checkbox.deselect()
        
        if hasattr(settings, 'report_detail_level'):
            self.widgets['report_detail_level'].set(settings.report_detail_level)
        else:
            self.widgets['report_detail_level'].set("표준")
        
        # 폴더 경로
        if hasattr(settings, 'default_output_folder') and settings.default_output_folder:
            entry = self.widgets.get('default_output_folder')
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, settings.default_output_folder)
        
        if hasattr(settings, 'default_completed_folder') and settings.default_completed_folder:
            entry = self.widgets.get('default_completed_folder')
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, settings.default_completed_folder)
        
        if hasattr(settings, 'backup_folder') and settings.backup_folder:
            entry = self.widgets.get('backup_folder')
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, settings.backup_folder)
        
        if hasattr(settings, 'temp_folder') and settings.temp_folder:
            entry = self.widgets.get('temp_folder')
            if entry:
                entry.delete(0, 'end')
                entry.insert(0, settings.temp_folder)
    
    def get_settings(self) -> Dict[str, Any]:
        """현재 설정 값 반환"""
        settings = {}
        
        # 프로파일
        settings['default_profile'] = self.widgets['default_profile'].get()
        
        # 자동 처리
        settings['auto_fix_enabled'] = self.widgets['auto_fix_enabled'].get()
        settings['auto_fix_level'] = self.widgets['auto_fix_level'].get()
        settings['move_completed_files'] = self.widgets['move_completed_files'].get()
        
        if 'create_backup' in self.widgets:
            settings['create_backup'] = self.widgets['create_backup'].get()
        
        # 보고서
        settings['generate_report'] = self.widgets['generate_report'].get()
        
        formats = []
        for fmt, checkbox in self.format_checkboxes.items():
            if checkbox.get():
                formats.append(fmt)
        settings['report_formats'] = formats
        
        settings['report_detail_level'] = self.widgets['report_detail_level'].get()
        
        # 폴더 경로
        output_folder = self.widgets['default_output_folder'].get()
        settings['default_output_folder'] = output_folder if output_folder else None
        
        completed_folder = self.widgets['default_completed_folder'].get()
        settings['default_completed_folder'] = completed_folder if completed_folder else None
        
        if 'backup_folder' in self.widgets:
            backup_folder = self.widgets['backup_folder'].get()
            settings['backup_folder'] = backup_folder if backup_folder else None
        
        if 'temp_folder' in self.widgets:
            temp_folder = self.widgets['temp_folder'].get()
            settings['temp_folder'] = temp_folder if temp_folder else None
        
        return settings
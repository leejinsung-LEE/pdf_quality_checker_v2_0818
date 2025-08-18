# src/ui/views/settings/processing_tab.py
"""
환경설정 뷰 - 처리 설정 탭

이 모듈은 처리 설정 탭의 UI 생성과 관련 기능을 담당합니다.
- 기본 프로파일 설정
- 자동 처리 옵션 (자동 수정, 파일 이동)
- 보고서 생성 설정 및 형식 선택

AI 친화적 설계:
- 독립적인 탭 헬퍼 클래스
- 섹션별로 구분된 UI 생성 함수
- 설정 로드/수집 함수 분리
"""

import customtkinter as ctk
from typing import Dict, Any, List


class ProcessingTabHelper:
    """처리 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any]) -> None:
        """
        처리 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 기본 프로파일 섹션
        ProcessingTabHelper._create_profile_section(scroll_frame, widgets)
        
        # 자동 처리 옵션 섹션
        ProcessingTabHelper._create_auto_processing_section(scroll_frame, widgets)
        
        # 보고서 섹션
        ProcessingTabHelper._create_report_section(scroll_frame, widgets)
    
    @staticmethod
    def _create_profile_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """기본 프로파일 섹션 생성"""
        # 기본 프로파일
        profile_frame = ctk.CTkFrame(parent, fg_color="transparent")
        profile_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(profile_frame, text="기본 프로파일:", width=150, anchor='w').pack(side='left')
        widgets['default_profile'] = ctk.CTkComboBox(
            profile_frame,
            values=["default", "quick", "strict"],
            width=200
        )
        widgets['default_profile'].pack(side='left')
    
    @staticmethod
    def _create_auto_processing_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """자동 처리 옵션 섹션 생성"""
        # 자동 처리 제목
        auto_label = ctk.CTkLabel(
            parent,
            text="자동 처리",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        auto_label.pack(fill='x', pady=(20, 10))
        
        # 자동 수정
        widgets['auto_fix_enabled'] = ctk.CTkCheckBox(
            parent,
            text="검사 후 자동으로 문제 수정 시도"
        )
        widgets['auto_fix_enabled'].pack(fill='x', pady=5)
        
        # 완료 파일 이동
        widgets['move_completed_files'] = ctk.CTkCheckBox(
            parent,
            text="처리 완료된 파일을 완료 폴더로 이동"
        )
        widgets['move_completed_files'].pack(fill='x', pady=5)
    
    @staticmethod
    def _create_report_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """보고서 섹션 생성"""
        # 보고서 제목
        report_label = ctk.CTkLabel(
            parent,
            text="보고서",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        report_label.pack(fill='x', pady=(20, 10))
        
        # 보고서 생성 옵션
        widgets['generate_report'] = ctk.CTkCheckBox(
            parent,
            text="처리 완료 후 보고서 자동 생성"
        )
        widgets['generate_report'].pack(fill='x', pady=5)
        
        # 보고서 형식
        format_frame = ctk.CTkFrame(parent, fg_color="transparent")
        format_frame.pack(fill='x', pady=(5, 15))
        
        ctk.CTkLabel(format_frame, text="보고서 형식:", width=150, anchor='w').pack(side='left')
        
        format_container = ctk.CTkFrame(format_frame, fg_color="transparent")
        format_container.pack(side='left')
        
        # 형식별 체크박스
        widgets['report_html'] = ctk.CTkCheckBox(format_container, text="HTML")
        widgets['report_html'].pack(side='left', padx=5)
        
        widgets['report_json'] = ctk.CTkCheckBox(format_container, text="JSON")
        widgets['report_json'].pack(side='left', padx=5)
        
        widgets['report_text'] = ctk.CTkCheckBox(format_container, text="텍스트")
        widgets['report_text'].pack(side='left', padx=5)
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings) -> None:
        """처리 설정 로드"""
        # 기본 프로파일
        widgets['default_profile'].set(settings.default_profile)
        
        # 자동 처리 옵션
        if settings.auto_fix_enabled:
            widgets['auto_fix_enabled'].select()
        else:
            widgets['auto_fix_enabled'].deselect()
            
        if settings.move_completed_files:
            widgets['move_completed_files'].select()
        else:
            widgets['move_completed_files'].deselect()
            
        if settings.generate_report:
            widgets['generate_report'].select()
        else:
            widgets['generate_report'].deselect()
        
        # 보고서 형식
        if hasattr(settings, 'report_formats') and settings.report_formats:
            if 'html' in settings.report_formats:
                widgets['report_html'].select()
            if 'json' in settings.report_formats:
                widgets['report_json'].select()
            if 'text' in settings.report_formats:
                widgets['report_text'].select()
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """처리 설정 수집"""
        settings = {}
        
        # 기본 프로파일
        settings['default_profile'] = widgets['default_profile'].get()
        
        # 자동 처리 옵션
        settings['auto_fix_enabled'] = widgets['auto_fix_enabled'].get()
        settings['move_completed_files'] = widgets['move_completed_files'].get()
        settings['generate_report'] = widgets['generate_report'].get()
        
        # 보고서 형식
        formats = []
        if widgets['report_html'].get():
            formats.append('html')
        if widgets['report_json'].get():
            formats.append('json')
        if widgets['report_text'].get():
            formats.append('text')
        settings['report_formats'] = formats
        
        return settings
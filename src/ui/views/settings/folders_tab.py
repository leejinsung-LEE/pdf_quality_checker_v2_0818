# src/ui/views/settings/folders_tab.py
"""
환경설정 뷰 - 폴더 설정 탭

이 모듈은 폴더 설정 탭의 UI 생성과 관련 기능을 담당합니다.
- 기본 출력 폴더 설정
- 완료 파일 폴더 설정
- 감시 폴더 정보 표시

AI 친화적 설계:
- 독립적인 탭 헬퍼 클래스
- 폴더 브라우저 기능 포함
- 설정 로드/수집 함수 분리
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Dict, Any, Callable


class FoldersTabHelper:
    """폴더 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any], browse_callback: Callable[[str], None]) -> None:
        """
        폴더 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
            browse_callback: 폴더 찾기 콜백 함수
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 기본 출력 폴더 섹션
        FoldersTabHelper._create_output_folder_section(scroll_frame, widgets, browse_callback)
        
        # 완료 파일 폴더 섹션
        FoldersTabHelper._create_completed_folder_section(scroll_frame, widgets, browse_callback)
        
        # 감시 폴더 정보 섹션
        FoldersTabHelper._create_watch_folders_section(scroll_frame)
    
    @staticmethod
    def _create_output_folder_section(
        parent: ctk.CTkScrollableFrame, 
        widgets: Dict[str, Any], 
        browse_callback: Callable[[str], None]
    ) -> None:
        """기본 출력 폴더 섹션 생성"""
        # 제목
        output_label = ctk.CTkLabel(
            parent,
            text="기본 출력 폴더",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        output_label.pack(fill='x', pady=(0, 10))
        
        # 폴더 선택 프레임
        output_frame = ctk.CTkFrame(parent, fg_color="transparent")
        output_frame.pack(fill='x', pady=(0, 20))
        
        widgets['default_output_folder'] = ctk.CTkEntry(
            output_frame,
            placeholder_text="기본값: output/"
        )
        widgets['default_output_folder'].pack(side='left', fill='x', expand=True)
        
        output_browse_btn = ctk.CTkButton(
            output_frame,
            text="찾아보기",
            width=100,
            command=lambda: browse_callback('default_output_folder')
        )
        output_browse_btn.pack(side='left', padx=(10, 0))
    
    @staticmethod
    def _create_completed_folder_section(
        parent: ctk.CTkScrollableFrame, 
        widgets: Dict[str, Any], 
        browse_callback: Callable[[str], None]
    ) -> None:
        """완료 파일 폴더 섹션 생성"""
        # 제목
        completed_label = ctk.CTkLabel(
            parent,
            text="완료 파일 폴더",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        completed_label.pack(fill='x', pady=(0, 10))
        
        # 폴더 선택 프레임
        completed_frame = ctk.CTkFrame(parent, fg_color="transparent")
        completed_frame.pack(fill='x', pady=(0, 20))
        
        widgets['default_completed_folder'] = ctk.CTkEntry(
            completed_frame,
            placeholder_text="기본값: completed/"
        )
        widgets['default_completed_folder'].pack(side='left', fill='x', expand=True)
        
        completed_browse_btn = ctk.CTkButton(
            completed_frame,
            text="찾아보기",
            width=100,
            command=lambda: browse_callback('default_completed_folder')
        )
        completed_browse_btn.pack(side='left', padx=(10, 0))
    
    @staticmethod
    def _create_watch_folders_section(parent: ctk.CTkScrollableFrame) -> None:
        """감시 폴더 정보 섹션 생성"""
        # 제목
        watch_label = ctk.CTkLabel(
            parent,
            text="감시 폴더",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        watch_label.pack(fill='x', pady=(0, 10))
        
        # 안내 문구
        watch_info = ctk.CTkLabel(
            parent,
            text="감시 폴더는 메인 화면의 사이드바에서 관리할 수 있습니다.",
            text_color="gray"
        )
        watch_info.pack(fill='x', pady=10)
    
    @staticmethod
    def browse_folder(widget_key: str, widgets: Dict[str, Any]) -> None:
        """폴더 찾아보기"""
        folder = filedialog.askdirectory(title="폴더 선택")
        if folder:
            widgets[widget_key].delete(0, 'end')
            widgets[widget_key].insert(0, folder)
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings) -> None:
        """폴더 설정 로드"""
        # 기본 출력 폴더
        if hasattr(settings, 'default_output_folder') and settings.default_output_folder:
            widgets['default_output_folder'].insert(0, settings.default_output_folder)
        
        # 완료 파일 폴더
        if hasattr(settings, 'default_completed_folder') and settings.default_completed_folder:
            widgets['default_completed_folder'].insert(0, settings.default_completed_folder)
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """폴더 설정 수집"""
        settings = {}
        
        # 출력 폴더
        output_folder = widgets['default_output_folder'].get()
        settings['default_output_folder'] = output_folder if output_folder else None
        
        # 완료 폴더
        completed_folder = widgets['default_completed_folder'].get()
        settings['default_completed_folder'] = completed_folder if completed_folder else None
        
        return settings
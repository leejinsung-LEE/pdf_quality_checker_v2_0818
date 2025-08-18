# src/ui/views/settings/general_tab.py
"""
환경설정 뷰 - 일반 설정 탭

이 모듈은 일반 설정 탭의 UI 생성과 관련 기능을 담당합니다.
- 언어 및 테마 설정
- 프로그램 시작 옵션
- 자동 감시 및 트레이 최소화 설정

AI 친화적 설계:
- 독립적인 탭 헬퍼 클래스
- 위젯 생성과 설정 로직 분리
- 명확한 함수 이름과 구조
"""

import customtkinter as ctk
from typing import Dict, Any


class GeneralTabHelper:
    """일반 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any]) -> None:
        """
        일반 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
        """
        # 스크롤 프레임
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 언어 및 테마 섹션
        GeneralTabHelper._create_appearance_section(scroll_frame, widgets)
        
        # 시작 옵션 섹션
        GeneralTabHelper._create_startup_section(scroll_frame, widgets)
    
    @staticmethod
    def _create_appearance_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """외관 설정 섹션 생성"""
        # 언어 설정
        lang_frame = ctk.CTkFrame(parent, fg_color="transparent")
        lang_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(lang_frame, text="언어:", width=150, anchor='w').pack(side='left')
        widgets['language'] = ctk.CTkComboBox(
            lang_frame,
            values=["한국어", "English", "日本語", "中文"],
            width=200
        )
        widgets['language'].pack(side='left')
        
        # 테마 설정
        theme_frame = ctk.CTkFrame(parent, fg_color="transparent")
        theme_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(theme_frame, text="테마:", width=150, anchor='w').pack(side='left')
        widgets['theme'] = ctk.CTkComboBox(
            theme_frame,
            values=["다크", "라이트", "시스템"],
            width=200
        )
        widgets['theme'].pack(side='left')
    
    @staticmethod
    def _create_startup_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """시작 옵션 섹션 생성"""
        # 시작 옵션 제목
        startup_label = ctk.CTkLabel(
            parent,
            text="시작 옵션",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        startup_label.pack(fill='x', pady=(20, 10))
        
        # 자동 폴더 감시
        widgets['auto_start_watching'] = ctk.CTkCheckBox(
            parent,
            text="프로그램 시작 시 폴더 감시 자동 시작"
        )
        widgets['auto_start_watching'].pack(fill='x', pady=5)
        
        # 트레이로 최소화
        widgets['minimize_to_tray'] = ctk.CTkCheckBox(
            parent,
            text="닫기 버튼 클릭 시 트레이로 최소화"
        )
        widgets['minimize_to_tray'].pack(fill='x', pady=5)
        
        # 시작 시 폴더 감시
        widgets['watch_folders_on_startup'] = ctk.CTkCheckBox(
            parent,
            text="마지막 감시 폴더 자동 복원"
        )
        widgets['watch_folders_on_startup'].pack(fill='x', pady=5)
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings) -> None:
        """일반 설정 로드"""
        # 언어 설정
        if settings.language == "ko":
            widgets['language'].set("한국어")
        else:
            widgets['language'].set(settings.language)
        
        # 테마 설정
        if settings.theme == "dark":
            widgets['theme'].set("다크")
        elif settings.theme == "light":
            widgets['theme'].set("라이트")
        else:
            widgets['theme'].set("시스템")
        
        # 체크박스 설정
        if settings.auto_start_watching:
            widgets['auto_start_watching'].select()
        else:
            widgets['auto_start_watching'].deselect()
            
        if settings.minimize_to_tray:
            widgets['minimize_to_tray'].select()
        else:
            widgets['minimize_to_tray'].deselect()
            
        if settings.watch_folders_on_startup:
            widgets['watch_folders_on_startup'].select()
        else:
            widgets['watch_folders_on_startup'].deselect()
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """일반 설정 수집"""
        settings = {}
        
        # 언어 매핑
        lang_map = {"한국어": "ko", "English": "en", "日本語": "ja", "中文": "zh"}
        settings['language'] = lang_map.get(widgets['language'].get(), "ko")
        
        # 테마 매핑
        theme_map = {"다크": "dark", "라이트": "light", "시스템": "system"}
        settings['theme'] = theme_map.get(widgets['theme'].get(), "dark")
        
        # 체크박스 설정
        settings['auto_start_watching'] = widgets['auto_start_watching'].get()
        settings['minimize_to_tray'] = widgets['minimize_to_tray'].get()
        settings['watch_folders_on_startup'] = widgets['watch_folders_on_startup'].get()
        
        return settings
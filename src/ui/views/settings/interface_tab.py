# src/ui/views/settings/interface_tab.py
"""
환경설정 뷰 - 인터페이스 설정 탭

이 모듈은 인터페이스 설정 탭의 UI 생성과 관련 기능을 담당합니다.
- 알림 설정 (처리 완료, 소리)
- 사이드바 너비 설정
- 테이블 열 표시/숨기기 설정

AI 친화적 설계:
- 독립적인 탭 헬퍼 클래스
- 동적 열 설정 지원
- 슬라이더 콜백 함수 포함
"""

import customtkinter as ctk
from typing import Dict, Any, Optional


class InterfaceTabHelper:
    """인터페이스 설정 탭 헬퍼 클래스"""
    
    @staticmethod
    def create_tab(parent: ctk.CTkFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """
        인터페이스 탭 생성
        
        Args:
            parent: 부모 프레임 (탭 프레임)
            widgets: 위젯 딕셔너리 (참조로 전달)
            
        Returns:
            sidebar_width_label: 사이드바 너비 표시 레이블
        """
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 알림 설정 섹션
        InterfaceTabHelper._create_notification_section(scroll_frame, widgets)
        
        # 사이드바 설정 섹션
        sidebar_width_label = InterfaceTabHelper._create_sidebar_section(scroll_frame, widgets)
        
        # 테이블 열 설정 섹션
        InterfaceTabHelper._create_columns_section(scroll_frame, widgets)
        
        return sidebar_width_label
    
    @staticmethod
    def _create_notification_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """알림 설정 섹션 생성"""
        # 알림 제목
        notif_label = ctk.CTkLabel(
            parent,
            text="알림",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        notif_label.pack(fill='x', pady=(0, 10))
        
        # 처리 완료 알림
        widgets['show_notifications'] = ctk.CTkCheckBox(
            parent,
            text="처리 완료 알림 표시"
        )
        widgets['show_notifications'].pack(fill='x', pady=5)
        
        # 알림음 재생
        widgets['notification_sound'] = ctk.CTkCheckBox(
            parent,
            text="알림음 재생"
        )
        widgets['notification_sound'].pack(fill='x', pady=5)
    
    @staticmethod
    def _create_sidebar_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> ctk.CTkLabel:
        """사이드바 설정 섹션 생성"""
        # 사이드바 제목
        sidebar_label = ctk.CTkLabel(
            parent,
            text="사이드바",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        sidebar_label.pack(fill='x', pady=(20, 10))
        
        # 사이드바 너비 설정
        sidebar_frame = ctk.CTkFrame(parent, fg_color="transparent")
        sidebar_frame.pack(fill='x', pady=(0, 15))
        
        ctk.CTkLabel(sidebar_frame, text="너비:", width=150, anchor='w').pack(side='left')
        widgets['sidebar_width'] = ctk.CTkSlider(
            sidebar_frame,
            from_=200,
            to=400,
            width=200
        )
        widgets['sidebar_width'].pack(side='left', padx=(0, 10))
        
        sidebar_width_label = ctk.CTkLabel(sidebar_frame, text="250px")
        sidebar_width_label.pack(side='left')
        
        # 슬라이더 값 변경 시 레이블 업데이트
        widgets['sidebar_width'].configure(
            command=lambda v: sidebar_width_label.configure(text=f"{int(v)}px")
        )
        
        return sidebar_width_label
    
    @staticmethod
    def _create_columns_section(parent: ctk.CTkScrollableFrame, widgets: Dict[str, Any]) -> None:
        """테이블 열 설정 섹션 생성"""
        # 열 표시 제목
        columns_label = ctk.CTkLabel(
            parent,
            text="테이블 열 표시",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        columns_label.pack(fill='x', pady=(20, 10))
        
        # 열 설정 프레임
        columns_frame = ctk.CTkFrame(parent, fg_color="transparent")
        columns_frame.pack(fill='x')
        
        # 열 체크박스들
        column_names = {
            'icon': '아이콘',
            'filename': '파일명',
            'folder': '폴더',
            'pagesize': '페이지 크기',
            'pages': '페이지 수',
            'issues': '문제',
            'time': '처리 시간',
            'report': '보고서'
        }
        
        # 2행으로 배치
        row1_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
        row1_frame.pack(fill='x', pady=2)
        
        row2_frame = ctk.CTkFrame(columns_frame, fg_color="transparent")
        row2_frame.pack(fill='x', pady=2)
        
        for i, (key, label) in enumerate(column_names.items()):
            widget_key = f'column_{key}'
            frame = row1_frame if i < 4 else row2_frame
            
            widgets[widget_key] = ctk.CTkCheckBox(
                frame,
                text=label,
                width=120
            )
            widgets[widget_key].pack(side='left', padx=5, pady=2)
    
    @staticmethod
    def load_settings(widgets: Dict[str, Any], settings, sidebar_width_label: ctk.CTkLabel) -> None:
        """인터페이스 설정 로드"""
        # 알림 설정
        if hasattr(settings, 'show_notifications') and settings.show_notifications:
            widgets['show_notifications'].select()
        else:
            widgets['show_notifications'].deselect()
            
        if hasattr(settings, 'notification_sound') and settings.notification_sound:
            widgets['notification_sound'].select()
        else:
            widgets['notification_sound'].deselect()
        
        # 사이드바 너비
        if hasattr(settings, 'sidebar_width'):
            widgets['sidebar_width'].set(settings.sidebar_width)
            sidebar_width_label.configure(text=f"{settings.sidebar_width}px")
        
        # 열 표시 설정
        if hasattr(settings, 'column_visibility'):
            for key, visible in settings.column_visibility.items():
                widget_key = f'column_{key}'
                if widget_key in widgets:
                    if visible:
                        widgets[widget_key].select()
                    else:
                        widgets[widget_key].deselect()
    
    @staticmethod
    def collect_settings(widgets: Dict[str, Any]) -> Dict[str, Any]:
        """인터페이스 설정 수집"""
        settings = {}
        
        # 알림 설정
        settings['show_notifications'] = widgets['show_notifications'].get()
        settings['notification_sound'] = widgets['notification_sound'].get()
        
        # 사이드바 너비
        settings['sidebar_width'] = int(widgets['sidebar_width'].get())
        
        # 열 표시 설정
        column_visibility = {}
        for key in ['icon', 'filename', 'folder', 'pagesize', 'pages', 'issues', 'time', 'report']:
            widget_key = f'column_{key}'
            if widget_key in widgets:
                column_visibility[key] = bool(widgets[widget_key].get())
        settings['column_visibility'] = column_visibility
        
        return settings
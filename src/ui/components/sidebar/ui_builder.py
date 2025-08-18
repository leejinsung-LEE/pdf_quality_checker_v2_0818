# src/ui/components/sidebar/ui_builder.py
"""
사이드바 UI 구성 요소 생성

각 섹션별 UI 컴포넌트를 생성하는 정적 메서드들을 제공합니다.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .base import SidebarBase


class UIBuilder:
    """사이드바 UI 생성 클래스"""
    
    @staticmethod
    def create_header_section(parent: ctk.CTkFrame, colors: Dict[str, str]) -> ctk.CTkFrame:
        """헤더 섹션 생성"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill='x', padx=20, pady=(25, 20))
        
        # 로고
        logo_label = ctk.CTkLabel(
            header,
            text="📊",
            font=('Arial', 36)
        )
        logo_label.pack(side='left', padx=(0, 15))
        
        # 타이틀 정보
        title_info = ctk.CTkFrame(header, fg_color="transparent")
        title_info.pack(side='left', fill='x', expand=True)
        
        # 메인 타이틀
        main_title = ctk.CTkLabel(
            title_info,
            text="PDF Quality",
            font=('맑은 고딕', 16, 'bold'),
            text_color=colors['text_primary']
        )
        main_title.pack(anchor='w')
        
        # 서브 타이틀
        sub_title = ctk.CTkLabel(
            title_info,
            text="Checker v2.0",
            font=('맑은 고딕', 11),
            text_color=colors['text_secondary']
        )
        sub_title.pack(anchor='w')
        
        return header
    
    @staticmethod
    def create_separator(parent: ctk.CTkFrame, colors: Dict[str, str]) -> ctk.CTkFrame:
        """구분선 생성"""
        separator = ctk.CTkFrame(
            parent,
            height=1,
            fg_color=colors['border']
        )
        separator.pack(fill='x', padx=20, pady=15)
        return separator
    
    @staticmethod
    def create_folder_watch_section(parent: ctk.CTkFrame, colors: Dict[str, str], 
                                  sidebar_ref: 'SidebarBase') -> Dict[str, Any]:
        """폴더 감시 섹션 생성"""
        # 메인 컨테이너
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill='x', padx=20, pady=(0, 20))
        
        # 헤더
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill='x', pady=(0, 10))
        
        # 타이틀
        title_label = ctk.CTkLabel(
            header,
            text="📂 폴더 감시",
            font=('맑은 고딕', 12, 'bold'),
            text_color=colors['text_primary']
        )
        title_label.pack(side='left')
        
        # 토글 스위치
        toggle_switch = ctk.CTkSwitch(
            header,
            text="",
            width=40,
            height=20,
            button_length=20,
            command=sidebar_ref._on_watch_toggle if hasattr(sidebar_ref, '_on_watch_toggle') else None
        )
        toggle_switch.pack(side='right')
        
        # 폴더 목록 프레임
        folder_frame = ctk.CTkFrame(
            section,
            height=100,
            fg_color=colors['bg_card'],
            corner_radius=8
        )
        folder_frame.pack(fill='x', pady=(0, 10))
        folder_frame.pack_propagate(False)
        
        # 폴더 추가 버튼
        add_button = ctk.CTkButton(
            section,
            text="➕ 폴더 추가",
            height=28,
            command=sidebar_ref._on_add_folder if hasattr(sidebar_ref, '_on_add_folder') else None
        )
        add_button.pack(fill='x')
        
        return {
            'section': section,
            'toggle_switch': toggle_switch,
            'folder_frame': folder_frame,
            'add_button': add_button
        }
    
    @staticmethod
    def create_quick_stats_section(parent: ctk.CTkFrame, colors: Dict[str, str]) -> Dict[str, Any]:
        """통계 섹션 생성"""
        # 메인 컨테이너
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill='x', padx=20, pady=(0, 20))
        
        # 타이틀
        title_label = ctk.CTkLabel(
            section,
            text="📊 오늘의 통계",
            font=('맑은 고딕', 12, 'bold'),
            text_color=colors['text_primary']
        )
        title_label.pack(pady=(0, 10))
        
        # 통계 카드
        stats_card = ctk.CTkFrame(
            section,
            fg_color=colors['bg_card'],
            corner_radius=8
        )
        stats_card.pack(fill='x')
        
        # 통계 항목들
        stats_data = [
            ("처리 완료", "processed_count", "0"),
            ("오류 발견", "error_count", "0"),
            ("자동 수정", "fixed_count", "0"),
            ("처리 시간", "processing_time", "0분")
        ]
        
        stats_widgets = {}
        
        for i, (label_text, key, default_value) in enumerate(stats_data):
            # 각 통계 항목
            stat_frame = ctk.CTkFrame(stats_card, fg_color="transparent")
            stat_frame.pack(fill='x', padx=15, pady=8)
            
            # 라벨
            label = ctk.CTkLabel(
                stat_frame,
                text=label_text,
                font=('맑은 고딕', 11),
                text_color=colors['text_secondary']
            )
            label.pack(side='left')
            
            # 값
            value_label = ctk.CTkLabel(
                stat_frame,
                text=default_value,
                font=('맑은 고딕', 11, 'bold'),
                text_color=colors['text_primary']
            )
            value_label.pack(side='right')
            
            stats_widgets[f'{key}_label'] = value_label
        
        return {
            'section': section,
            'stats_card': stats_card,
            'widgets': stats_widgets
        }
    
    @staticmethod
    def create_drop_zone(parent: ctk.CTkFrame, colors: Dict[str, str], 
                        sidebar_ref: 'SidebarBase') -> Dict[str, Any]:
        """드래그앤드롭 영역 생성"""
        # 메인 컨테이너
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill='x', padx=20, pady=(0, 20))
        
        # 타이틀
        title_label = ctk.CTkLabel(
            section,
            text="🚀 빠른 처리",
            font=('맑은 고딕', 12, 'bold'),
            text_color=colors['text_primary']
        )
        title_label.pack(pady=(0, 10))
        
        # 드롭 영역
        drop_zone = ctk.CTkFrame(
            section,
            height=120,
            fg_color=colors['bg_card'],
            corner_radius=10
        )
        drop_zone.pack(fill='x', pady=(0, 10))
        
        # 드롭 존 내용
        drop_icon = ctk.CTkLabel(
            drop_zone,
            text="📥",
            font=('Arial', 32)
        )
        drop_icon.pack(pady=(20, 5))
        
        drop_text = ctk.CTkLabel(
            drop_zone,
            text="PDF 파일을 여기에 드롭",
            font=('Arial', 12),
            text_color=colors['text_secondary']
        )
        drop_text.pack(pady=(0, 15))
        
        # 파일 선택 버튼
        file_button = ctk.CTkButton(
            section,
            text="파일 선택",
            height=28,
            width=100,
            command=sidebar_ref._on_file_select if hasattr(sidebar_ref, '_on_file_select') else None
        )
        file_button.pack()
        
        return {
            'section': section,
            'drop_zone': drop_zone,
            'drop_icon': drop_icon,
            'drop_text': drop_text,
            'file_button': file_button
        }
    
    @staticmethod
    def create_profile_selector(parent: ctk.CTkFrame, colors: Dict[str, str],
                              sidebar_ref: 'SidebarBase') -> Dict[str, Any]:
        """프로파일 선택 섹션 생성"""
        # 메인 컨테이너
        section = ctk.CTkFrame(parent, fg_color="transparent")
        section.pack(fill='x', padx=20, pady=(0, 20))
        
        # 타이틀
        title_label = ctk.CTkLabel(
            section,
            text="프로파일",
            font=('Arial', 12, 'bold'),
            text_color=colors['text_primary']
        )
        title_label.pack(pady=(0, 8))
        
        # 프로파일 목록 가져오기
        try:
            profiles = sidebar_ref.profile_controller.get_profile_list()
            # ProfileInfo 객체를 문자열로 변환
            if profiles and hasattr(profiles[0], 'name'):
                profiles = [p.name for p in profiles]
            
            current_profile_info = sidebar_ref.profile_controller.get_current_profile()
            if current_profile_info:
                if hasattr(current_profile_info[0], 'name'):
                    current_profile = current_profile_info[0].name
                else:
                    current_profile = current_profile_info[0]
            else:
                current_profile = "default"
        except:
            profiles = ["default"]
            current_profile = "default"
        
        # 프로파일 드롭다운
        profile_dropdown = ctk.CTkOptionMenu(
            section,
            values=profiles,
            width=230,
            command=sidebar_ref._on_profile_select if hasattr(sidebar_ref, '_on_profile_select') else None
        )
        profile_dropdown.pack(fill='x')
        profile_dropdown.set(current_profile)
        
        return {
            'section': section,
            'title_label': title_label,
            'profile_dropdown': profile_dropdown
        }
    
    @staticmethod
    def create_footer_section(parent: ctk.CTkFrame, colors: Dict[str, str]) -> ctk.CTkFrame:
        """하단 정보 섹션 생성"""
        # 스페이서 (상단 여백)
        spacer = ctk.CTkFrame(parent, fg_color="transparent", height=20)
        spacer.pack(fill='x')
        
        # 푸터
        footer = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=40
        )
        footer.pack(side='bottom', fill='x', padx=20, pady=(0, 20))
        footer.pack_propagate(False)
        
        # 버전 정보
        version_label = ctk.CTkLabel(
            footer,
            text="v2.0.0",
            font=('Arial', 10),
            text_color=colors['text_secondary']
        )
        version_label.pack(side='bottom')
        
        return footer
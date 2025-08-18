# src/ui/views/profile_manager/base.py
"""
프로파일 관리 뷰 - 기본 클래스
ProfileManagerView의 기본 구조와 초기화 로직을 담당

AI 친화적 문서화:
- 모든 메서드는 명확한 역할과 책임을 가짐
- 타입 힌트를 통한 명시적 인터페이스 제공
- 컴포넌트 간 결합도 최소화
- MVC 패턴 준수
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

from ...controllers import get_profile_controller, ProfileInfo
from .profile_list import ProfileListWidget
from .info_tab import InfoTabHelper
from .standards_tab import StandardsTabHelper
from .rules_tab import RulesTabHelper
from .color_tab import ColorTabHelper
from .handlers import ProfileEventHandler


class ProfileManagerView(ctk.CTkToplevel):
    """
    프로파일 관리 메인 뷰 클래스
    
    역할:
    - 전체 UI 레이아웃 구성 및 관리
    - 각 탭별 헬퍼 클래스 통합
    - 프로파일 컨트롤러와의 인터페이스
    - 이벤트 핸들링 위임
    
    아키텍처:
    - MVC 패턴의 View 역할
    - 헬퍼 클래스 패턴으로 책임 분산
    - 이벤트 위임을 통한 결합도 감소
    """
    
    def __init__(self, parent):
        """
        프로파일 관리 창 초기화
        
        Args:
            parent: 부모 윈도우 객체
        """
        super().__init__(parent)
        
        # 컨트롤러 초기화
        self.profile_controller = get_profile_controller()
        
        # 상태 변수
        self.selected_profile: Optional[str] = None
        self.current_profile_name: Optional[str] = None
        
        # UI 컴포넌트 참조
        self.widgets: Dict[str, Any] = {}
        self.detail_tabs: Optional[ctk.CTkTabview] = None
        
        # 헬퍼 클래스들
        self.profile_list_widget: Optional[ProfileListWidget] = None
        self.info_tab_helper: Optional[InfoTabHelper] = None
        self.standards_tab_helper: Optional[StandardsTabHelper] = None
        self.rules_tab_helper: Optional[RulesTabHelper] = None
        self.color_tab_helper: Optional[ColorTabHelper] = None
        self.event_handler: Optional[ProfileEventHandler] = None
        
        # 초기화
        self._setup_window()
        self._initialize_ui()
        self._load_initial_data()
        
    def _setup_window(self):
        """창 기본 설정"""
        self.title("프로파일 관리")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # 모달 창 설정
        self.transient(self.master)
        self.grab_set()
        
        # 포커스 설정
        self.focus()
    
    def _initialize_ui(self):
        """UI 초기화 및 구성"""
        # 메인 프레임
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 좌측: 프로파일 목록
        self._create_left_panel(main_frame)
        
        # 우측: 상세 정보 탭뷰
        self._create_right_panel(main_frame)
        
        # 하단: 버튼들
        self._create_bottom_panel()
        
        # 이벤트 핸들러 초기화
        self.event_handler = ProfileEventHandler(self)
        
        # 프로파일 리스트 위젯에 이벤트 핸들러 연결
        if self.profile_list_widget:
            self._connect_event_handlers()
    
    def _create_left_panel(self, parent: ctk.CTkFrame):
        """좌측 패널 생성 (프로파일 목록)"""
        left_frame = ctk.CTkFrame(parent, width=350)
        left_frame.pack(side='left', fill='both', padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # 프로파일 목록 위젯 생성
        self.profile_list_widget = ProfileListWidget(
            parent=left_frame,
            profile_controller=self.profile_controller,
            on_profile_select=self._on_profile_select,
            on_profile_double_click=self._on_profile_double_click
        )
    
    def _create_right_panel(self, parent: ctk.CTkFrame):
        """우측 패널 생성 (상세 정보)"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 헤더
        detail_header = ctk.CTkLabel(
            right_frame,
            text="프로파일 상세 정보",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        detail_header.pack(pady=10)
        
        # 탭뷰 생성
        self.detail_tabs = ctk.CTkTabview(right_frame)
        self.detail_tabs.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # 탭 추가
        self.detail_tabs.add("기본 정보")
        self.detail_tabs.add("품질 기준")
        self.detail_tabs.add("검사 규칙")
        self.detail_tabs.add("색상 설정")
        
        # 각 탭 헬퍼 클래스 생성
        self._initialize_tab_helpers()
    
    def _initialize_tab_helpers(self):
        """탭별 헬퍼 클래스 초기화"""
        # 기본 정보 탭
        self.info_tab_helper = InfoTabHelper(
            parent=self.detail_tabs.tab("기본 정보"),
            widgets=self.widgets
        )
        
        # 품질 기준 탭
        self.standards_tab_helper = StandardsTabHelper(
            parent=self.detail_tabs.tab("품질 기준"),
            widgets=self.widgets
        )
        
        # 검사 규칙 탭
        self.rules_tab_helper = RulesTabHelper(
            parent=self.detail_tabs.tab("검사 규칙"),
            profile_controller=self.profile_controller,
            widgets=self.widgets
        )
        
        # 색상 설정 탭
        self.color_tab_helper = ColorTabHelper(
            parent=self.detail_tabs.tab("색상 설정"),
            widgets=self.widgets
        )
    
    def _create_bottom_panel(self):
        """하단 패널 생성 (저장/닫기 버튼)"""
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        save_btn = ctk.CTkButton(
            bottom_frame,
            text="저장",
            command=self._on_save_clicked,
            width=100
        )
        save_btn.pack(side='right', padx=(5, 0))
        
        cancel_btn = ctk.CTkButton(
            bottom_frame,
            text="닫기",
            command=self.destroy,
            width=100
        )
        cancel_btn.pack(side='right')
    
    def _load_initial_data(self):
        """초기 데이터 로드"""
        if self.profile_list_widget:
            self.profile_list_widget.load_profiles()
        
        # 현재 프로파일 설정
        current_name, _ = self.profile_controller.get_current_profile()
        self.current_profile_name = current_name
    
    def _connect_event_handlers(self):
        """이벤트 핸들러 연결"""
        if not self.event_handler or not self.profile_list_widget:
            return
        
        handlers = {
            'create': self.event_handler.create_profile,
            'duplicate': self.event_handler.duplicate_profile,
            'delete': self.event_handler.delete_profile,
            'import': self.event_handler.import_profile,
            'export': self.event_handler.export_profile,
            'set_current': self.event_handler.set_as_current_profile
        }
        
        self.profile_list_widget.set_event_handlers(handlers)
    
    def _on_profile_select(self, profile_name: str):
        """프로파일 선택 이벤트 핸들러"""
        if self.event_handler:
            self.event_handler.on_profile_select(profile_name)
    
    def _on_profile_double_click(self, profile_name: str):
        """프로파일 더블클릭 이벤트 핸들러"""
        if self.event_handler:
            self.event_handler.on_profile_double_click(profile_name)
    
    def _on_save_clicked(self):
        """저장 버튼 클릭 이벤트 핸들러"""
        if self.event_handler:
            self.event_handler.on_save_profile()
    
    def load_profile_details(self, profile_name: str):
        """
        프로파일 상세 정보 로드
        
        Args:
            profile_name: 로드할 프로파일 이름
        """
        profile = self.profile_controller.get_profile(profile_name)
        if not profile:
            return
        
        # 프로파일 정보 가져오기
        profiles = self.profile_controller.get_profile_list()
        profile_info = next((p for p in profiles if p.name == profile_name), None)
        
        if not profile_info:
            return
        
        # 각 탭별 데이터 로드
        if self.info_tab_helper:
            self.info_tab_helper.load_profile_data(profile_info)
        
        if self.standards_tab_helper:
            self.standards_tab_helper.load_profile_data(profile.data)
        
        if self.rules_tab_helper:
            self.rules_tab_helper.load_profile_data(profile.data, profile_info.is_builtin)
        
        if self.color_tab_helper:
            self.color_tab_helper.load_profile_data(profile.data)
        
        # 내장 프로파일인 경우 편집 불가 설정
        self._set_editing_enabled(not profile_info.is_builtin)
    
    def _set_editing_enabled(self, enabled: bool):
        """편집 가능 여부 설정"""
        if self.info_tab_helper:
            self.info_tab_helper.set_editing_enabled(enabled)
        
        if self.standards_tab_helper:
            self.standards_tab_helper.set_editing_enabled(enabled)
        
        if self.rules_tab_helper:
            self.rules_tab_helper.set_editing_enabled(enabled)
        
        if self.color_tab_helper:
            self.color_tab_helper.set_editing_enabled(enabled)
    
    def refresh_profile_list(self):
        """프로파일 목록 새로고침"""
        if self.profile_list_widget:
            self.profile_list_widget.load_profiles()
    
    # 외부 인터페이스 메서드들
    def set_selected_profile(self, profile_name: Optional[str]):
        """선택된 프로파일 설정"""
        self.selected_profile = profile_name
    
    def get_selected_profile(self) -> Optional[str]:
        """선택된 프로파일 반환"""
        return self.selected_profile
    
    def get_current_profile_name(self) -> Optional[str]:
        """현재 프로파일 이름 반환"""
        return self.current_profile_name
    
    def show_message(self, title: str, message: str, message_type: str = "info"):
        """메시지 표시"""
        if message_type == "error":
            messagebox.showerror(title, message)
        elif message_type == "warning":
            messagebox.showwarning(title, message)
        else:
            messagebox.showinfo(title, message)
    
    def ask_yes_no(self, title: str, message: str) -> bool:
        """예/아니오 질문"""
        return messagebox.askyesno(title, message)
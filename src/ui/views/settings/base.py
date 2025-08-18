# src/ui/views/settings/base.py
"""
환경설정 뷰 - 기본 클래스와 초기화 로직

이 모듈은 SettingsView의 핵심 기능과 초기화를 담당합니다.
- 윈도우 설정 및 기본 UI 구조 생성
- 탭 뷰 관리
- 버튼 핸들러와 기본 이벤트 처리
- 설정 적용과 저장 로직

모듈화 구조:
- SettingsViewBase: 기본 윈도우와 탭 관리
- 각 탭별 모듈에서 탭 내용을 생성
- handlers 모듈에서 이벤트 처리 로직 분리

AI 친화적 설계:
- 명확한 클래스 구조와 메서드 분리
- 타입 힌트와 상세한 주석
- 확장 가능한 탭 시스템
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from typing import Dict, Any, Optional, Callable
from pathlib import Path
import logging

from ....config import Config
from ....config.alarm_config import AlarmSettings, AlarmConditionType, NotificationMethod
from ....utils.alarm_manager import get_alarm_manager
from ...controllers import get_settings_controller, UserSettings
from ...events import EventBus, EventType, Event


class SettingsViewBase(ctk.CTkToplevel):
    """
    환경설정 뷰 기본 클래스
    
    환경설정을 위한 독립 윈도우의 기본 구조를 제공합니다.
    탭 관리와 기본 이벤트 처리를 담당합니다.
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 컨트롤러
        self.settings_controller = get_settings_controller()
        self.settings = self.settings_controller.get_settings()
        
        # 이벤트 버스 초기화
        self.event_bus = EventBus()
        
        # 임시 설정 (적용 전까지 보관)
        self.temp_settings = {}
        
        # 위젯 참조
        self.widgets: Dict[str, Any] = {}
        
        # 콜백 (하위 호환성 유지)
        self.on_settings_applied: Optional[Callable[[Dict[str, Any]], None]] = None
        self.callbacks: Dict[str, Callable] = {}
        
        # 탭뷰 참조
        self.tabview: Optional[ctk.CTkTabview] = None
        
        # 레이블 참조들 (슬라이더용)
        self.sidebar_width_label: Optional[ctk.CTkLabel] = None
        self.concurrent_label: Optional[ctk.CTkLabel] = None
        self.volume_label: Optional[ctk.CTkLabel] = None
        
        # 윈도우 설정
        self._setup_window()
        
        # UI 생성
        self._create_ui()
        
        # 포커스 설정
        self.focus()
        
        # 설정창 열림 이벤트 발행
        self.emit_event(EventType.SETTINGS_OPEN)
    
    def _setup_window(self):
        """윈도우 설정"""
        self.title("환경설정")
        self.geometry("800x600")
        self.resizable(False, False)
        
        # 모달 윈도우로 설정
        self.transient(self.master)
        self.grab_set()
        
        # ESC 키로 닫기
        self.bind('<Escape>', lambda e: self.cancel())
        
        # 닫기 버튼 처리
        self.protocol("WM_DELETE_WINDOW", self.cancel)
    
    def _create_ui(self):
        """기본 UI 생성"""
        # 메인 컨테이너
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 제목
        title_label = ctk.CTkLabel(
            main_container,
            text="환경설정",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 탭 뷰 생성
        self.tabview = ctk.CTkTabview(main_container, height=450)
        self.tabview.pack(fill='both', expand=True)
        
        # 탭 추가
        self._create_tabs()
        
        # 버튼 프레임
        self._create_buttons(main_container)
    
    def _create_tabs(self):
        """탭 생성 - 서브클래스에서 구현"""
        # 기본 탭들 추가
        self.tabview.add("일반")
        self.tabview.add("처리")
        self.tabview.add("폴더")
        self.tabview.add("인터페이스")
        self.tabview.add("알람")
        self.tabview.add("고급")
        self.tabview.add("외부 도구")
    
    def _create_buttons(self, parent):
        """하단 버튼들 생성"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill='x', pady=(20, 0))
        
        # 취소 버튼
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="취소",
            width=100,
            command=self.cancel
        )
        cancel_btn.pack(side='right', padx=(5, 0))
        
        # 적용 버튼
        apply_btn = ctk.CTkButton(
            button_frame,
            text="적용",
            width=100,
            command=self.apply_settings
        )
        apply_btn.pack(side='right')
        
        # 확인 버튼
        ok_btn = ctk.CTkButton(
            button_frame,
            text="확인",
            width=100,
            command=self.ok
        )
        ok_btn.pack(side='right', padx=(0, 5))
        
        # 초기화 버튼
        reset_btn = ctk.CTkButton(
            button_frame,
            text="기본값 복원",
            width=100,
            fg_color="gray",
            command=self.reset_to_defaults
        )
        reset_btn.pack(side='left')
    
    def apply_settings(self):
        """설정 적용 - 서브클래스에서 구현"""
        pass
    
    def ok(self):
        """확인 (적용 후 닫기)"""
        if self.apply_settings():
            self.emit_event(EventType.SETTINGS_APPLIED, self.temp_settings)
            self.emit_event(EventType.SETTINGS_CLOSED)
            self.destroy()
    
    def cancel(self):
        """취소"""
        self.emit_event(EventType.SETTINGS_CLOSED)
        self.destroy()
    
    def reset_to_defaults(self):
        """기본값으로 초기화 - 서브클래스에서 구현"""
        self.emit_event(EventType.SETTINGS_RESET)
        pass
    
    def emit_event(self, event_type: EventType, data: Optional[Dict[str, Any]] = None):
        """
        이벤트 발행 헬퍼 메서드
        
        Args:
            event_type: 발행할 이벤트 타입
            data: 이벤트 데이터
        """
        # 이벤트 버스로 발행
        event = Event(
            type=event_type,
            data=data or {},
            source='settings_view'
        )
        self.event_bus.emit(event_type, event)
        
        # 하위 호환성: 기존 콜백도 호출
        if str(event_type.value) in self.callbacks:
            self.callbacks[str(event_type.value)](data)
        
        # 특정 이벤트에 대한 기존 콜백 처리
        if event_type == EventType.SETTINGS_APPLIED and self.on_settings_applied:
            self.on_settings_applied(data or {})
    
    def subscribe_event(self, event_type: EventType, callback: Callable[[Event], None]):
        """
        이벤트 구독 헬퍼 메서드
        
        Args:
            event_type: 구독할 이벤트 타입
            callback: 이벤트 핸들러
        """
        self.event_bus.subscribe(event_type, callback)
    
    def get_tab(self, tab_name: str) -> Optional[ctk.CTkFrame]:
        """특정 탭 프레임 가져오기"""
        if self.tabview:
            return self.tabview.tab(tab_name)
        return None
    
    def set_apply_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """설정 적용 콜백 설정
        
        Args:
            callback: 설정 적용 시 호출될 콜백 함수
        """
        self.on_settings_applied = callback
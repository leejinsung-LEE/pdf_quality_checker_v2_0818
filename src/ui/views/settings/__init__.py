# src/ui/views/settings/__init__.py
"""
환경설정 뷰 모듈

모듈화된 환경설정 뷰를 통합하고 외부에 SettingsView를 제공합니다.
기존 API 호환성을 유지하면서 내부 구조를 모듈화했습니다.

모듈 구조:
- base.py: 기본 윈도우 클래스
- general_tab.py: 일반 설정 탭
- processing_tab.py: 처리 설정 탭  
- folders_tab.py: 폴더 설정 탭
- interface_tab.py: 인터페이스 설정 탭
- alarm_tab.py: 알람 설정 탭
- advanced_tools_tab.py: 고급 및 도구 설정 탭
- handlers.py: 이벤트 핸들러와 유틸리티
"""

import customtkinter as ctk
from typing import Dict, Any, Optional, Callable

from .base import SettingsViewBase
from .general_tab import GeneralTabHelper
from .processing_tab import ProcessingTabHelper
from .folders_tab import FoldersTabHelper
from .interface_tab import InterfaceTabHelper
from .alarm_tab import AlarmTabHelper
from .advanced_tools_tab import AdvancedTabHelper, ToolsTabHelper
from .handlers import SettingsEventHandlers
from ...events import EventType


class SettingsView(SettingsViewBase):
    """
    환경설정 뷰 - 모듈화된 버전
    
    기존 API와 호환성을 유지하면서 내부를 모듈화한 환경설정 뷰입니다.
    각 탭별로 모듈이 분리되어 있어 유지보수가 용이합니다.
    """
    
    def __init__(self, parent, **kwargs):
        # 기본 클래스 초기화 (탭 생성 제외)
        super().__init__(parent, **kwargs)
        
        # 탭 딕셔너리 초기화
        self.tabs = {}
        
        # 이벤트 핸들러 초기화
        self.handler = SettingsEventHandlers(self, self.settings_controller)
        self.handlers = self.handler  # 호환성을 위한 별칭
        
        # 레이블 참조들 (슬라이더용)
        self.sidebar_width_label: Optional[ctk.CTkLabel] = None
        self.concurrent_label: Optional[ctk.CTkLabel] = None
        self.volume_label: Optional[ctk.CTkLabel] = None
        
        # 각 탭 내용 생성
        self._create_tab_contents()
        
        # 현재 설정 로드
        self.handlers.load_all_settings()
    
    def _create_tab_contents(self):
        """각 탭 내용 생성"""
        # 일반 탭
        GeneralTabHelper.create_tab(
            self.get_tab("일반"), 
            self.widgets
        )
        
        # 처리 탭
        ProcessingTabHelper.create_tab(
            self.get_tab("처리"),
            self.widgets
        )
        
        # 폴더 탭
        FoldersTabHelper.create_tab(
            self.get_tab("폴더"),
            self.widgets,
            self.handlers.browse_folder
        )
        
        # 인터페이스 탭
        self.sidebar_width_label = InterfaceTabHelper.create_tab(
            self.get_tab("인터페이스"),
            self.widgets
        )
        
        # 알람 탭
        self.volume_label = AlarmTabHelper.create_tab(
            self.get_tab("알람"),
            self.widgets
        )
        
        # 고급 탭
        self.concurrent_label = AdvancedTabHelper.create_tab(
            self.get_tab("고급"),
            self.widgets
        )
        
        # 외부 도구 탭
        ToolsTabHelper.create_tab(
            self.get_tab("외부 도구"),
            self.widgets,
            self.settings_controller,
            self.handlers.browse_tool,
            self.handlers.test_tool,
            self.handlers.auto_detect_tools
        )
        
        # 위젯 변경 이벤트 바인딩
        self._bind_widget_events()
    
    def apply_settings(self) -> bool:
        """설정 적용"""
        return self.handlers.apply_settings()
    
    def reset_to_defaults(self) -> None:
        """기본값으로 초기화"""
        self.handlers.reset_to_defaults()
    
    # 기존 API 호환성을 위한 메서드들
    def _load_current_settings(self) -> None:
        """현재 설정 로드 (기존 호환성)"""
        self.handlers.load_all_settings()
    
    def _collect_settings(self) -> Dict[str, Any]:
        """설정 수집 (기존 호환성)"""
        return self.handlers.collect_all_settings()
    
    def _browse_folder(self, widget_key: str) -> None:
        """폴더 찾아보기 (기존 호환성)"""
        self.handlers.browse_folder(widget_key)
    
    def _browse_tool(self, widget_key: str) -> None:
        """도구 찾아보기 (기존 호환성)"""
        self.handlers.browse_tool(widget_key)
    
    def _test_tool(self, tool_name: str) -> None:
        """도구 테스트 (기존 호환성)"""
        self.handlers.test_tool(tool_name)
    
    def _auto_detect_tools(self) -> None:
        """도구 자동 감지 (기존 호환성)"""
        self.handlers.auto_detect_tools()
    
    def _test_alarm(self) -> None:
        """알람 테스트 (기존 호환성)"""
        AlarmTabHelper._test_alarm()
    
    def _bind_widget_events(self) -> None:
        """위젯 변경 이벤트 바인딩"""
        # 일반 탭 이벤트
        if 'theme' in self.widgets:
            self.widgets['theme'].configure(
                command=lambda value: self.emit_event(EventType.THEME_CHANGED, {'theme': value})
            )
        
        if 'language' in self.widgets:
            self.widgets['language'].configure(
                command=lambda value: self.emit_event(EventType.LANGUAGE_CHANGED, {'language': value})
            )
        
        if 'auto_start_watching' in self.widgets:
            self.widgets['auto_start_watching'].configure(
                command=lambda: self.emit_event(EventType.STARTUP_OPTIONS_CHANGED, 
                                               {'auto_start': self.widgets['auto_start_watching'].get()})
            )
        
        if 'minimize_to_tray' in self.widgets:
            self.widgets['minimize_to_tray'].configure(
                command=lambda: self.emit_event(EventType.TRAY_MINIMIZE_CHANGED,
                                               {'minimize_to_tray': self.widgets['minimize_to_tray'].get()})
            )
        
        # 처리 탭 이벤트
        if 'profile' in self.widgets:
            self.widgets['profile'].configure(
                command=lambda value: self.emit_event(EventType.PROFILE_SELECTED, {'profile': value})
            )
        
        if 'auto_process' in self.widgets:
            self.widgets['auto_process'].configure(
                command=lambda: self.emit_event(EventType.AUTO_PROCESS_CHANGED,
                                               {'auto_process': self.widgets['auto_process'].get()})
            )
        
        if 'report_format' in self.widgets:
            self.widgets['report_format'].configure(
                command=lambda value: self.emit_event(EventType.REPORT_FORMAT_CHANGED, {'format': value})
            )
        
        # 인터페이스 탭 이벤트
        if 'show_notifications' in self.widgets:
            self.widgets['show_notifications'].configure(
                command=lambda: self.emit_event(EventType.NOTIFICATION_SETTINGS_CHANGED,
                                               {'enabled': self.widgets['show_notifications'].get()})
            )
        
        if 'sidebar_width' in self.widgets:
            self.widgets['sidebar_width'].configure(
                command=lambda value: self.emit_event(EventType.SIDEBAR_SETTINGS_CHANGED,
                                                     {'width': int(value)})
            )
        
        # 알람 탭 이벤트
        if 'alarm_enabled' in self.widgets:
            self.widgets['alarm_enabled'].configure(
                command=lambda: self.emit_event(
                    EventType.ALARM_ENABLED if self.widgets['alarm_enabled'].get() else EventType.ALARM_DISABLED,
                    {'enabled': self.widgets['alarm_enabled'].get()}
                )
            )
        
        # 고급 탭 이벤트
        if 'concurrent_files' in self.widgets:
            self.widgets['concurrent_files'].configure(
                command=lambda value: self.emit_event(EventType.CONCURRENT_FILES_CHANGED,
                                                     {'count': int(value)})
            )
        
        if 'log_level' in self.widgets:
            self.widgets['log_level'].configure(
                command=lambda value: self.emit_event(EventType.LOG_LEVEL_CHANGED, {'level': value})
            )


# 외부 사용을 위한 export
__all__ = ['SettingsView']
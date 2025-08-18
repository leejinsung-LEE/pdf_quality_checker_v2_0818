# src/ui/components/menubar.py
"""
메뉴바 컴포넌트 - 이벤트 버스 통합 버전

애플리케이션의 메뉴바를 구성합니다.
이벤트 버스와 레거시 콜백을 모두 지원합니다.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import webbrowser

# 이벤트 시스템 (옵셔널 - 없어도 동작)
try:
    from ..events import EventBus, Event, EventType, get_event_bus
    from ..events.menu_actions import MenuDefinitions, MenuAction
    EVENT_SYSTEM_AVAILABLE = True
except ImportError:
    EVENT_SYSTEM_AVAILABLE = False


class MenuBar(tk.Menu):
    """
    메뉴바 컴포넌트
    
    이벤트 버스가 있으면 사용하고, 없으면 기존 콜백 방식으로 동작합니다.
    """
    
    def __init__(self, parent, event_bus: Optional['EventBus'] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 이벤트 버스 설정
        self.event_bus = None
        if EVENT_SYSTEM_AVAILABLE:
            self.event_bus = event_bus or get_event_bus()
        
        # 콜백 (기존 방식 지원)
        self.callbacks: Dict[str, Optional[Callable]] = {
            # 파일 메뉴
            'open_files': None,
            'open_folder': None,
            'recent_files': None,
            'exit': None,
            
            # 편집 메뉴
            'preferences': None,
            'profiles': None,
            
            # 보기 메뉴
            'view_processing': None,
            'view_dashboard': None,
            'view_statistics': None,
            'view_profile_settings': None,
            'toggle_sidebar': None,
            'toggle_statusbar': None,
            
            # 도구 메뉴
            'batch_process': None,
            'folder_watch': None,
            'batch_scheduler': None,
            'backup_manager': None,
            'export_report': None,
            
            # 도움말 메뉴
            'help_docs': None,
            'about': None,
            'check_updates': None
        }
        
        # 메뉴 액션 매핑
        self.actions: Dict[str, Any] = {}
        
        # 최근 파일 메뉴
        self.recent_menu: Optional[tk.Menu] = None
        
        # 체크 변수들
        self.sidebar_var = tk.BooleanVar(value=True)
        self.statusbar_var = tk.BooleanVar(value=True)
        
        # 메뉴 생성
        if EVENT_SYSTEM_AVAILABLE and self.event_bus:
            self._create_menus_with_events()
        else:
            self._create_menus_legacy()
        
        # 이벤트 구독 (가능한 경우)
        if EVENT_SYSTEM_AVAILABLE and self.event_bus:
            self._subscribe_events()
    
    def _create_menus_with_events(self):
        """이벤트 기반 메뉴 생성"""
        menu_definitions = MenuDefinitions.get_all_menus()
        
        for menu_name, actions in menu_definitions.items():
            menu = tk.Menu(self, tearoff=0)
            self.add_cascade(label=menu_name, menu=menu)
            
            if menu_name == "파일":
                self._build_file_menu_events(menu, actions)
            elif menu_name == "보기":
                self._build_view_menu_events(menu, actions)
            else:
                self._build_standard_menu_events(menu, actions)
    
    def _build_standard_menu_events(self, menu: tk.Menu, actions: List['MenuAction']):
        """표준 메뉴 구성 (이벤트 기반)"""
        for action in actions:
            menu.add_command(
                label=action.label,
                accelerator=action.accelerator,
                command=lambda a=action: self._trigger_action(a),
                state=tk.NORMAL if action.enabled else tk.DISABLED
            )
            
            if action.separator_after:
                menu.add_separator()
            
            self.actions[action.id] = action
    
    def _build_file_menu_events(self, menu: tk.Menu, actions: List['MenuAction']):
        """파일 메뉴 구성 (이벤트 기반)"""
        for action in actions:
            if action.id == "file.recent":
                self.recent_menu = tk.Menu(menu, tearoff=0)
                menu.add_cascade(label=action.label, menu=self.recent_menu)
                self._update_recent_files([])
            else:
                menu.add_command(
                    label=action.label,
                    accelerator=action.accelerator,
                    command=lambda a=action: self._trigger_action(a)
                )
            
            if action.separator_after:
                menu.add_separator()
            
            self.actions[action.id] = action
    
    def _build_view_menu_events(self, menu: tk.Menu, actions: List['MenuAction']):
        """보기 메뉴 구성 (이벤트 기반)"""
        for action in actions:
            if action.id == "view.sidebar":
                menu.add_checkbutton(
                    label=action.label,
                    variable=self.sidebar_var,
                    command=lambda a=action: self._trigger_action(a)
                )
            elif action.id == "view.statusbar":
                menu.add_checkbutton(
                    label=action.label,
                    variable=self.statusbar_var,
                    command=lambda a=action: self._trigger_action(a)
                )
            else:
                menu.add_command(
                    label=action.label,
                    accelerator=action.accelerator,
                    command=lambda a=action: self._trigger_action(a)
                )
            
            if action.separator_after:
                menu.add_separator()
            
            self.actions[action.id] = action
    
    def _trigger_action(self, action: 'MenuAction'):
        """액션 트리거 (이벤트 + 레거시)"""
        # 이벤트 발행
        if self.event_bus:
            event_data = {
                "action_id": action.id,
                "source": "menubar"
            }
            
            if action.id == "view.sidebar":
                event_data["visible"] = self.sidebar_var.get()
            elif action.id == "view.statusbar":
                event_data["visible"] = self.statusbar_var.get()
            
            self.event_bus.emit(
                action.event_type,
                data=event_data,
                source="menubar"
            )
        
        # 레거시 콜백
        legacy_key = self._get_legacy_callback_key(action.id)
        if legacy_key and legacy_key in self.callbacks:
            callback = self.callbacks.get(legacy_key)
            if callback:
                callback()
    
    def _get_legacy_callback_key(self, action_id: str) -> Optional[str]:
        """액션 ID를 레거시 콜백 키로 변환"""
        mapping = {
            "file.open": "open_files",
            "file.open_folder": "open_folder",
            "file.recent": "recent_files",
            "file.exit": "exit",
            "edit.preferences": "preferences",
            "edit.profiles": "profiles",
            "view.processing": "view_processing",
            "view.dashboard": "view_dashboard",
            "view.statistics": "view_statistics",
            "view.profile_settings": "view_profile_settings",
            "view.sidebar": "toggle_sidebar",
            "view.statusbar": "toggle_statusbar",
            "tools.batch_process": "batch_process",
            "tools.folder_watch": "folder_watch",
            "tools.batch_scheduler": "batch_scheduler",
            "tools.backup_manager": "backup_manager",
            "tools.export_report": "export_report",
            "help.docs": "help_docs",
            "help.about": "about",
            "help.update": "check_updates"
        }
        return mapping.get(action_id)
    
    def _create_menus_legacy(self):
        """레거시 메뉴 생성 (이벤트 시스템 없을 때)"""
        self._create_file_menu()
        self._create_edit_menu()
        self._create_view_menu()
        self._create_tools_menu()
        self._create_help_menu()
    
    def _create_file_menu(self):
        """파일 메뉴 생성 (레거시)"""
        file_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="파일", menu=file_menu)
        
        file_menu.add_command(
            label="파일 열기...",
            accelerator="Ctrl+O",
            command=lambda: self._execute_callback('open_files')
        )
        
        file_menu.add_command(
            label="폴더 열기...",
            accelerator="Ctrl+Shift+O",
            command=lambda: self._execute_callback('open_folder')
        )
        
        file_menu.add_separator()
        
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="최근 파일", menu=self.recent_menu)
        self._update_recent_files([])
        
        file_menu.add_separator()
        
        file_menu.add_command(
            label="종료",
            accelerator="Ctrl+Q",
            command=lambda: self._execute_callback('exit')
        )
    
    def _create_edit_menu(self):
        """편집 메뉴 생성 (레거시)"""
        edit_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="편집", menu=edit_menu)
        
        edit_menu.add_command(
            label="환경설정...",
            accelerator="Ctrl+,",
            command=lambda: self._execute_callback('preferences')
        )
        
        edit_menu.add_separator()
        
        edit_menu.add_command(
            label="프로파일 관리...",
            command=lambda: self._execute_callback('profiles')
        )
    
    def _create_view_menu(self):
        """보기 메뉴 생성 (레거시)"""
        view_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="보기", menu=view_menu)
        
        view_menu.add_command(
            label="처리 화면",
            accelerator="F1",
            command=lambda: self._execute_callback('view_processing')
        )
        
        view_menu.add_command(
            label="대시보드",
            accelerator="F2",
            command=lambda: self._execute_callback('view_dashboard')
        )
        
        view_menu.add_command(
            label="통계 분석",
            accelerator="F3",
            command=lambda: self._execute_callback('view_statistics')
        )
        
        view_menu.add_command(
            label="프로파일 설정",
            accelerator="F4",
            command=lambda: self._execute_callback('view_profile_settings')
        )
        
        view_menu.add_separator()
        
        view_menu.add_checkbutton(
            label="사이드바",
            variable=self.sidebar_var,
            command=lambda: self._execute_callback('toggle_sidebar')
        )
        
        view_menu.add_checkbutton(
            label="상태바",
            variable=self.statusbar_var,
            command=lambda: self._execute_callback('toggle_statusbar')
        )
    
    def _create_tools_menu(self):
        """도구 메뉴 생성 (레거시)"""
        tools_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="도구", menu=tools_menu)
        
        tools_menu.add_command(
            label="일괄 처리...",
            accelerator="Ctrl+B",
            command=lambda: self._execute_callback('batch_process')
        )
        
        tools_menu.add_command(
            label="폴더 감시 설정...",
            command=lambda: self._execute_callback('folder_watch')
        )
        
        tools_menu.add_separator()
        
        tools_menu.add_command(
            label="배치 스케줄러...",
            accelerator="Ctrl+S",
            command=lambda: self._execute_callback('batch_scheduler')
        )
        
        tools_menu.add_command(
            label="백업 관리자...",
            accelerator="Ctrl+R",
            command=lambda: self._execute_callback('backup_manager')
        )
        
        tools_menu.add_separator()
        
        tools_menu.add_command(
            label="보고서 내보내기...",
            command=lambda: self._execute_callback('export_report')
        )
    
    def _create_help_menu(self):
        """도움말 메뉴 생성 (레거시)"""
        help_menu = tk.Menu(self, tearoff=0)
        self.add_cascade(label="도움말", menu=help_menu)
        
        help_menu.add_command(
            label="사용 설명서",
            accelerator="F1",
            command=lambda: self._execute_callback('help_docs')
        )
        
        help_menu.add_separator()
        
        help_menu.add_command(
            label="업데이트 확인",
            command=lambda: self._execute_callback('check_updates')
        )
        
        help_menu.add_command(
            label="정보",
            command=lambda: self._execute_callback('about')
        )
    
    def _execute_callback(self, action: str):
        """콜백 실행 (레거시)"""
        callback = self.callbacks.get(action)
        if callback:
            callback()
        else:
            # 기본 동작
            if action == 'help_docs':
                webbrowser.open("https://github.com/yourusername/pdf-quality-checker")
            elif action == 'about':
                self._show_about()
            elif action == 'check_updates':
                messagebox.showinfo("업데이트", "최신 버전을 사용 중입니다.")
    
    def _show_about(self):
        """정보 다이얼로그"""
        about_text = """PDF Quality Checker v2.0

PDF 파일의 인쇄 품질을 자동으로 검사하고
문제점을 수정하는 프로그램입니다.

© 2024 Your Company
All rights reserved."""
        
        messagebox.showinfo("PDF Quality Checker 정보", about_text)
    
    def _update_recent_files(self, files: List[str]):
        """최근 파일 메뉴 업데이트"""
        if not self.recent_menu:
            return
        
        self.recent_menu.delete(0, tk.END)
        
        if not files:
            self.recent_menu.add_command(
                label="(최근 파일 없음)",
                state='disabled'
            )
        else:
            for i, file_path in enumerate(files[:10], 1):
                self.recent_menu.add_command(
                    label=f"{i}. {Path(file_path).name}",
                    command=lambda p=file_path: self._open_recent_file(p)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(
                label="목록 지우기",
                command=self._clear_recent_files
            )
    
    def _open_recent_file(self, file_path: str):
        """최근 파일 열기"""
        if self.event_bus and EVENT_SYSTEM_AVAILABLE:
            self.event_bus.emit(
                EventType.FILE_RECENT_OPEN,
                data={"file_path": file_path, "source": "menubar"}
            )
        
        if self.callbacks.get('recent_files'):
            self.callbacks['recent_files']([Path(file_path)])
    
    def _clear_recent_files(self):
        """최근 파일 목록 지우기"""
        self._update_recent_files([])
        
        if self.event_bus and EVENT_SYSTEM_AVAILABLE:
            self.event_bus.emit(
                EventType.FILE_RECENT_CLEAR,
                data={"source": "menubar"}
            )
    
    def _subscribe_events(self):
        """이벤트 구독"""
        if not self.event_bus:
            return
        
        # 기본 핸들러들
        self.event_bus.subscribe(EventType.HELP_OPEN, self._on_help_open)
        self.event_bus.subscribe(EventType.ABOUT_OPEN, self._on_about_open)
        self.event_bus.subscribe(EventType.UPDATE_CHECK, self._on_update_check)
    
    def _on_help_open(self, event: 'Event'):
        """도움말 열기 핸들러"""
        if event.data.get("source") == "menubar":
            webbrowser.open("https://github.com/yourusername/pdf-quality-checker")
    
    def _on_about_open(self, event: 'Event'):
        """정보 표시 핸들러"""
        if event.data.get("source") == "menubar":
            self._show_about()
    
    def _on_update_check(self, event: 'Event'):
        """업데이트 확인 핸들러"""
        if event.data.get("source") == "menubar":
            messagebox.showinfo("업데이트", "최신 버전을 사용 중입니다.")
    
    # === 공개 API ===
    
    def set_callback(self, action: str, callback: Callable):
        """콜백 설정"""
        if action in self.callbacks:
            self.callbacks[action] = callback
    
    def update_recent_files(self, files: List[str]):
        """최근 파일 업데이트"""
        self._update_recent_files(files)
    
    def enable_menu_item(self, menu: str, item: str, enabled: bool = True):
        """메뉴 항목 활성화/비활성화"""
        # 구현 필요시 추가
        pass
# src/ui/components/menubar_improved.py
"""
개선된 메뉴바 컴포넌트 - 이벤트 버스 통합 버전

기존 콜백 방식과 이벤트 버스를 모두 지원하여 점진적 마이그레이션이 가능합니다.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable, Dict, Any, List
from pathlib import Path
import webbrowser

from ..events import EventBus, Event, EventType, get_event_bus
from ..events.menu_actions import MenuDefinitions, MenuAction


class ImprovedMenuBar(tk.Menu):
    """
    개선된 메뉴바 컴포넌트
    
    이벤트 버스를 통한 느슨한 결합과 기존 콜백 방식을 모두 지원합니다.
    """
    
    def __init__(self, parent, event_bus: Optional[EventBus] = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        # 이벤트 버스 (제공되지 않으면 전역 인스턴스 사용)
        self.event_bus = event_bus or get_event_bus()
        
        # 레거시 콜백 지원 (하위 호환성)
        self.callbacks: Dict[str, Optional[Callable]] = {}
        
        # 메뉴 액션 매핑
        self.actions: Dict[str, MenuAction] = {}
        
        # 최근 파일 메뉴 참조
        self.recent_menu: Optional[tk.Menu] = None
        
        # 체크 변수들 (보기 메뉴용)
        self.sidebar_var = tk.BooleanVar(value=True)
        self.statusbar_var = tk.BooleanVar(value=True)
        
        # 메뉴 생성
        self._build_menus()
        
        # 이벤트 구독
        self._subscribe_events()
    
    def _build_menus(self):
        """메뉴 구성"""
        menu_definitions = MenuDefinitions.get_all_menus()
        
        for menu_name, actions in menu_definitions.items():
            menu = tk.Menu(self, tearoff=0)
            self.add_cascade(label=menu_name, menu=menu)
            
            # 특별 처리가 필요한 메뉴
            if menu_name == "파일":
                self._build_file_menu(menu, actions)
            elif menu_name == "보기":
                self._build_view_menu(menu, actions)
            else:
                self._build_standard_menu(menu, actions)
    
    def _build_standard_menu(self, menu: tk.Menu, actions: List[MenuAction]):
        """표준 메뉴 구성"""
        for action in actions:
            if action.separator_after and menu.index("end") is not None:
                # 이전 항목이 있으면 구분선 추가
                if menu.index("end") != 0:
                    menu.add_separator()
            
            menu.add_command(
                label=action.label,
                accelerator=action.accelerator,
                command=lambda a=action: self._trigger_action(a),
                state=tk.NORMAL if action.enabled else tk.DISABLED
            )
            
            self.actions[action.id] = action
    
    def _build_file_menu(self, menu: tk.Menu, actions: List[MenuAction]):
        """파일 메뉴 구성 (최근 파일 서브메뉴 포함)"""
        for action in actions:
            if action.id == "file.recent":
                # 최근 파일 서브메뉴
                self.recent_menu = tk.Menu(menu, tearoff=0)
                menu.add_cascade(label=action.label, menu=self.recent_menu)
                self._update_recent_files([])  # 초기화
            else:
                menu.add_command(
                    label=action.label,
                    accelerator=action.accelerator,
                    command=lambda a=action: self._trigger_action(a)
                )
            
            if action.separator_after:
                menu.add_separator()
            
            self.actions[action.id] = action
    
    def _build_view_menu(self, menu: tk.Menu, actions: List[MenuAction]):
        """보기 메뉴 구성 (체크박스 항목 포함)"""
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
    
    def _trigger_action(self, action: MenuAction):
        """
        액션 트리거
        
        1. 이벤트 버스로 이벤트 발행
        2. 레거시 콜백 실행 (있는 경우)
        """
        # 이벤트 데이터 준비
        event_data = {
            "action_id": action.id,
            "source": "menubar"
        }
        
        # 특별한 데이터 추가
        if action.id == "view.sidebar":
            event_data["visible"] = self.sidebar_var.get()
        elif action.id == "view.statusbar":
            event_data["visible"] = self.statusbar_var.get()
        
        # 이벤트 발행
        self.event_bus.emit(
            action.event_type,
            data=event_data,
            source="menubar"
        )
        
        # 레거시 콜백 실행 (하위 호환성)
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
    
    def _subscribe_events(self):
        """이벤트 구독"""
        # 도움말 메뉴 기본 핸들러
        self.event_bus.subscribe(EventType.HELP_OPEN, self._on_help_open)
        self.event_bus.subscribe(EventType.ABOUT_OPEN, self._on_about_open)
        self.event_bus.subscribe(EventType.UPDATE_CHECK, self._on_update_check)
    
    def _on_help_open(self, event: Event):
        """도움말 열기 핸들러"""
        if event.data.get("source") == "menubar":
            webbrowser.open("https://github.com/yourusername/pdf-quality-checker")
    
    def _on_about_open(self, event: Event):
        """정보 표시 핸들러"""
        if event.data.get("source") == "menubar":
            about_text = """PDF Quality Checker v2.0

PDF 파일의 인쇄 품질을 자동으로 검사하고
문제점을 수정하는 프로그램입니다.

© 2024 Your Company
All rights reserved."""
            messagebox.showinfo("PDF Quality Checker 정보", about_text)
    
    def _on_update_check(self, event: Event):
        """업데이트 확인 핸들러"""
        if event.data.get("source") == "menubar":
            messagebox.showinfo("업데이트", "최신 버전을 사용 중입니다.")
    
    def _update_recent_files(self, files: List[str]):
        """최근 파일 메뉴 업데이트"""
        if not self.recent_menu:
            return
        
        # 기존 항목 제거
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
        # 이벤트 발행
        self.event_bus.emit(
            EventType.FILE_RECENT_OPEN,
            data={
                "file_path": file_path,
                "source": "menubar"
            }
        )
        
        # 레거시 콜백
        if self.callbacks.get('recent_files'):
            self.callbacks['recent_files']([Path(file_path)])
    
    def _clear_recent_files(self):
        """최근 파일 목록 지우기"""
        self._update_recent_files([])
        
        # 이벤트 발행
        self.event_bus.emit(
            EventType.FILE_RECENT_CLEAR,
            data={"source": "menubar"}
        )
    
    # === 레거시 API (하위 호환성) ===
    
    def set_callback(self, action: str, callback: Callable):
        """
        콜백 설정 (레거시 API)
        
        기존 코드와의 호환성을 위해 유지합니다.
        """
        if action in self.callbacks:
            self.callbacks[action] = callback
    
    def update_recent_files(self, files: List[str]):
        """최근 파일 업데이트 (레거시 API)"""
        self._update_recent_files(files)
    
    def enable_menu_item(self, menu: str, item: str, enabled: bool = True):
        """
        메뉴 항목 활성화/비활성화
        
        Args:
            menu: 메뉴 이름
            item: 항목 이름
            enabled: 활성화 여부
        """
        # 메뉴 찾기
        menu_index = None
        try:
            # 메뉴 이름으로 인덱스 찾기
            for i in range(self.index("end") + 1):
                if self.entryconfig(i).get('label') == menu:
                    menu_index = i
                    break
            
            if menu_index is not None:
                # 서브메뉴 가져오기
                submenu = self.nametowidget(self.entryconfig(menu_index)['menu'])
                
                # 항목 찾아서 상태 변경
                for i in range(submenu.index("end") + 1):
                    try:
                        if submenu.entryconfig(i).get('label') == item:
                            submenu.entryconfig(i, state=tk.NORMAL if enabled else tk.DISABLED)
                            break
                    except tk.TclError:
                        continue
        except (tk.TclError, KeyError):
            pass
    
    def set_check_state(self, var_name: str, state: bool):
        """체크박스 상태 설정"""
        if var_name == "sidebar":
            self.sidebar_var.set(state)
        elif var_name == "statusbar":
            self.statusbar_var.set(state)


# 기존 MenuBar와의 호환성을 위한 별칭
MenuBar = ImprovedMenuBar
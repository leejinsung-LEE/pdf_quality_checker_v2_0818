"""
메인 윈도우 통합 클래스
base.py + event_handler.py + view_manager.py 통합
"""

import customtkinter as ctk
import tkinterdnd2
from typing import Dict, List, Optional
from pathlib import Path
import json

from ...controllers import (
    get_file_controller, get_settings_controller, get_profile_controller,
    FileStatus
)
from ....processing import FolderWatcher
from ...events import EventBus, EventType, Event


class MainWindow(tkinterdnd2.Tk):
    """
    메인 윈도우
    
    애플리케이션의 메인 윈도우로 모든 UI 컴포넌트를 통합합니다.
    이벤트 처리와 뷰 관리 기능을 포함합니다.
    """
    
    def __init__(self):
        super().__init__()
        
        # 윈도우 설정
        self.title("PDF Quality Checker v2.0")
        self.geometry("1400x800")
        self.minsize(1200, 600)
        
        # 아이콘 설정 (있는 경우)
        try:
            self.iconbitmap("resources/icon.ico")
        except Exception:
            pass
        
        # CustomTkinter 설정
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 컨트롤러 초기화
        self.file_controller = get_file_controller()
        self.settings_controller = get_settings_controller()
        self.profile_controller = get_profile_controller()
        
        # 이벤트 버스 초기화
        self.event_bus = EventBus()
        
        # 폴더 감시자
        self.folder_watchers: Dict[str, FolderWatcher] = {}
        
        # 현재 뷰
        self.current_view = "unified_processing"
        self.views: Dict[str, ctk.CTkFrame] = {}
        
        # 최근 파일
        self.recent_files: List[str] = []
        
        # UI 요소 딕셔너리 (호환성을 위해)
        self.widgets = {}
        
        # 헬퍼 클래스는 나중에 초기화 (window_ui.py, window_managers.py)
        self.ui_builder = None
        self.file_manager = None
        self.folder_watcher_manager = None
        self.dialog_manager = None
        
        # 초기화는 헬퍼 클래스 설정 후 진행
    
    def set_helpers(self, ui_builder, file_manager, folder_watcher_manager, dialog_manager):
        """헬퍼 클래스 설정"""
        self.ui_builder = ui_builder
        self.file_manager = file_manager
        self.folder_watcher_manager = folder_watcher_manager
        self.dialog_manager = dialog_manager
        
        # 이제 초기화 진행
        self._initialize()
    
    def _initialize(self):
        """초기화"""
        # 최근 파일 로드
        self.file_manager.load_recent_files()
        
        # UI 생성
        self.ui_builder.create_ui()
        
        # 이벤트 설정
        self.setup_callbacks()
        
        # 이벤트 버스 리스너 설정
        self.setup_event_listeners()
        
        # 초기 설정 적용
        self._apply_initial_settings()
        
        # 윈도우 이벤트
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 단축키 바인딩
        self.bind_shortcuts()
    
    def _apply_initial_settings(self):
        """초기 설정 적용"""
        settings = self.settings_controller.get_settings()
        
        # 윈도우 크기/위치
        if settings.window_geometry:
            self.geometry(settings.window_geometry)
        
        # 사이드바 너비
        if hasattr(self, 'sidebar'):
            self.sidebar.configure(width=settings.sidebar_width)
        
        # 현재 프로파일
        current_profile = self.profile_controller.get_current_profile()[0]
        if hasattr(self, 'statusbar'):
            self.statusbar.set_current_profile(current_profile)
        
        # 폴더 감시 자동 시작
        if settings.auto_start_watching:
            self.folder_watcher_manager.start_all_watchers()
    
    def on_closing(self):
        """종료 처리"""
        # 설정 저장
        self._save_settings()
        
        # 폴더 감시 중지
        self.folder_watcher_manager.stop_all_watchers()
        
        # 창 닫기
        self.destroy()
    
    def _save_settings(self):
        """설정 저장"""
        settings = self.settings_controller.get_settings()
        
        # 윈도우 설정
        settings.window_geometry = self.geometry()
        if hasattr(self, 'sidebar'):
            settings.sidebar_width = self.sidebar.winfo_width()
        
        # 설정 저장
        self.settings_controller.save_settings()
        
        # 최근 파일 저장
        self.file_manager.save_recent_files()
    
    # ========== 이벤트 핸들러 메서드 (event_handler.py) ==========
    
    def setup_callbacks(self):
        """콜백 설정"""
        self._setup_menu_callbacks()
        self._setup_sidebar_callbacks()
        self._setup_controller_callbacks()
    
    def _setup_menu_callbacks(self):
        """메뉴 콜백 설정"""
        if hasattr(self, 'menubar'):
            # 파일 메뉴
            self.menubar.set_callback('open_files', self.file_manager.open_files)
            self.menubar.set_callback('open_folder', self.file_manager.open_folder)
            self.menubar.set_callback('recent_files', self.file_manager.open_recent_files)
            self.menubar.set_callback('exit', self.on_closing)
            
            # 편집 메뉴
            self.menubar.set_callback('preferences', self.dialog_manager.show_preferences)
            self.menubar.set_callback('profiles', self.dialog_manager.show_profile_manager)
            
            # 보기 메뉴
            self.menubar.set_callback('view_processing', lambda: self.notebook.select(0))
            self.menubar.set_callback('view_dashboard', lambda: self.notebook.select(1))
            self.menubar.set_callback('view_statistics', lambda: self.notebook.select(2))
            self.menubar.set_callback('view_profile_settings', lambda: self.notebook.select(3))
            self.menubar.set_callback('toggle_sidebar', self.toggle_sidebar)
            self.menubar.set_callback('toggle_statusbar', self.toggle_statusbar)
            
            # 도구 메뉴
            self.menubar.set_callback('batch_process', self.dialog_manager.show_batch_dialog)
            self.menubar.set_callback('folder_watch', self.dialog_manager.show_folder_watch_dialog)
            self.menubar.set_callback('batch_scheduler', self.dialog_manager.show_batch_scheduler_dialog)
            self.menubar.set_callback('backup_manager', self.dialog_manager.show_backup_manager_dialog)
            self.menubar.set_callback('export_report', self.dialog_manager.export_current_report)
    
    def _setup_sidebar_callbacks(self):
        """사이드바 콜백 설정"""
        if hasattr(self, 'sidebar'):
            self.sidebar.set_callbacks(
                on_view_change=self.switch_tab,
                on_files_dropped=self.file_manager.process_files,
                on_profile_change=self.on_profile_change,
                on_folder_select=self.folder_watcher_manager.add_watch_folder
            )
    
    def _setup_controller_callbacks(self):
        """컨트롤러 콜백 설정"""
        # 파일 컨트롤러 콜백
        self.file_controller.set_ui_callbacks(
            on_file_status_changed=self.on_file_status_changed,
            on_file_progress=self.on_file_progress,
            on_file_completed=self.on_file_completed,
            on_file_error=self.on_file_error
        )
        
        # 프로파일 컨트롤러 콜백
        self.profile_controller.on_current_profile_changed = self.on_profile_change
    
    def bind_shortcuts(self):
        """단축키 바인딩"""
        # 파일 작업
        self.bind('<Control-o>', lambda e: self.file_manager.open_files())
        self.bind('<Control-Shift-O>', lambda e: self.file_manager.open_folder())
        self.bind('<Control-q>', lambda e: self.on_closing())
        
        # 설정
        self.bind('<Control-comma>', lambda e: self.dialog_manager.show_preferences())
        
        # 도구
        self.bind('<Control-b>', lambda e: self.dialog_manager.show_batch_dialog())
        
        # 뷰 전환
        self.bind('<F1>', lambda e: self.notebook.select(0))
        self.bind('<F2>', lambda e: self.notebook.select(1))
        self.bind('<F3>', lambda e: self.notebook.select(2))
        self.bind('<F4>', lambda e: self.notebook.select(3))
    
    # 이벤트 처리 메서드
    
    def on_file_status_changed(self, file_id: str, status):
        """파일 상태 변경 이벤트"""
        if 'unified_processing' in self.views:
            self.views['unified_processing'].update_file_status(file_id, status)
    
    def on_file_progress(self, file_id: str, progress: int, message: str):
        """파일 처리 진행률 이벤트"""
        if 'unified_processing' in self.views:
            self.views['unified_processing'].update_progress(file_id, progress, message)
    
    def on_file_completed(self, file_id: str, file_item):
        """파일 처리 완료 이벤트"""
        # 통합 처리 뷰 업데이트
        if 'unified_processing' in self.views:
            self.views['unified_processing'].update_file_status(file_id, FileStatus.COMPLETED)
        
        # 대시보드 업데이트
        if 'dashboard' in self.views:
            self.views['dashboard'].update_statistics()
        
        # 통계 대시보드 업데이트
        if 'statistics' in self.views:
            self.views['statistics'].add_processed_file(file_item)
        
        # 최근 파일 추가
        self.file_manager.add_recent_file(str(file_item.path))
    
    def on_file_error(self, file_id: str, error: str):
        """파일 처리 에러 이벤트"""
        if 'unified_processing' in self.views:
            self.views['unified_processing'].show_error(file_id, error)
    
    def on_profile_change(self, profile_name: str):
        """프로파일 변경 이벤트"""
        # 상태바 업데이트
        if hasattr(self, 'statusbar'):
            self.statusbar.set_current_profile(profile_name)
        
        # 사이드바 업데이트
        if hasattr(self, 'sidebar'):
            self.sidebar.update_profile_display(profile_name)
    
    # ========== 뷰 매니저 메서드 (view_manager.py) ==========
    
    def on_tab_changed(self, selected_tab: int):
        """탭 변경 이벤트 처리"""
        # 탭별 새로고침
        if selected_tab == 0:  # 통합 처리 탭
            self.current_view = 'unified_processing'
            if 'unified_processing' in self.views:
                self.views['unified_processing'].refresh()
                
        elif selected_tab == 1:  # 대시보드 탭
            self.current_view = 'dashboard'
            if 'dashboard' in self.views:
                self.views['dashboard'].update_statistics()
                
        elif selected_tab == 2:  # 통계 분석 탭
            self.current_view = 'statistics'
            if 'statistics' in self.views:
                self.views['statistics'].refresh_data()
                
        elif selected_tab == 3:  # 프로파일 설정 탭
            self.current_view = 'profile_settings'
            if 'profile_settings' in self.views:
                self.views['profile_settings'].load_profile_list()
    
    def switch_tab(self, view_name: str):
        """뷰 이름으로 탭 전환"""
        tab_index = {
            'unified_processing': 0,
            'dashboard': 1,
            'statistics': 2,
            'profile_settings': 3
        }
        
        if view_name in tab_index:
            if hasattr(self, 'notebook'):
                self.notebook.select(tab_index[view_name])
                
                # 뷰별 새로고침
                if view_name == 'dashboard' and 'dashboard' in self.views:
                    self.views['dashboard'].refresh_data()
                elif view_name == 'unified_processing' and 'unified_processing' in self.views:
                    self.views['unified_processing'].refresh()
                elif view_name == 'statistics' and 'statistics' in self.views:
                    self.views['statistics'].refresh_data()
                elif view_name == 'profile_settings' and 'profile_settings' in self.views:
                    self.views['profile_settings'].load_profile_list()
    
    def toggle_sidebar(self):
        """사이드바 토글"""
        if hasattr(self, 'sidebar'):
            if self.sidebar.winfo_viewable():
                self.sidebar.pack_forget()
            else:
                main_container = self.widgets.get('main_container')
                if main_container:
                    self.sidebar.pack(side='left', fill='y', 
                                    before=self.widgets.get('content_container'))
    
    def toggle_statusbar(self):
        """상태바 토글"""
        if hasattr(self, 'statusbar'):
            if self.statusbar.winfo_viewable():
                self.statusbar.pack_forget()
            else:
                content_container = self.widgets.get('content_container')
                if content_container:
                    self.statusbar.pack(side='bottom', fill='x')
    
    def refresh_current_view(self):
        """현재 뷰 새로고침"""
        if self.current_view == 'unified_processing':
            if 'unified_processing' in self.views:
                self.views['unified_processing'].refresh()
        elif self.current_view == 'dashboard':
            if 'dashboard' in self.views:
                self.views['dashboard'].update_statistics()
        elif self.current_view == 'statistics':
            if 'statistics' in self.views:
                self.views['statistics'].refresh_data()
        elif self.current_view == 'profile_settings':
            if 'profile_settings' in self.views:
                self.views['profile_settings'].load_profile_list()
    
    def get_current_view(self):
        """현재 활성 뷰 반환"""
        return self.views.get(self.current_view)
    
    def update_all_views(self):
        """모든 뷰 업데이트"""
        for view_name, view in self.views.items():
            if hasattr(view, 'refresh'):
                view.refresh()
            elif hasattr(view, 'update_statistics'):
                view.update_statistics()
            elif hasattr(view, 'refresh_data'):
                view.refresh_data()
            elif hasattr(view, 'load_profile_list'):
                view.load_profile_list()
    
    def setup_event_listeners(self):
        """이벤트 버스 리스너 설정"""
        # 설정 관련 이벤트
        self.event_bus.subscribe(EventType.SETTINGS_APPLIED, self.on_settings_applied)
        self.event_bus.subscribe(EventType.THEME_CHANGED, self.on_theme_changed)
        self.event_bus.subscribe(EventType.LANGUAGE_CHANGED, self.on_language_changed)
        
        # 프로파일 관련 이벤트
        self.event_bus.subscribe(EventType.PROFILE_SELECTED, self.on_profile_selected)
        
        # UI 설정 관련 이벤트
        self.event_bus.subscribe(EventType.SIDEBAR_SETTINGS_CHANGED, self.on_sidebar_settings_changed)
        self.event_bus.subscribe(EventType.NOTIFICATION_SETTINGS_CHANGED, self.on_notification_settings_changed)
        
        # 알람 관련 이벤트
        self.event_bus.subscribe(EventType.ALARM_ENABLED, self.on_alarm_enabled)
        self.event_bus.subscribe(EventType.ALARM_DISABLED, self.on_alarm_disabled)
        
        # 도구 관련 이벤트
        self.event_bus.subscribe(EventType.TOOL_TEST_REQUESTED, self.on_tool_test_requested)
    
    # 이벤트 핸들러들
    def on_settings_applied(self, event: Event):
        """설정이 적용되었을 때"""
        print(f"[이벤트] 설정 적용됨: {event.data}")
        self._apply_initial_settings()
        self.update_all_views()
    
    def on_theme_changed(self, event: Event):
        """테마가 변경되었을 때"""
        theme = event.data.get('theme', 'dark')
        print(f"[이벤트] 테마 변경: {theme}")
        if theme == "다크":
            ctk.set_appearance_mode("dark")
        elif theme == "라이트":
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("system")
    
    def on_language_changed(self, event: Event):
        """언어가 변경되었을 때 - 한국어 전용 시스템"""
        # 한국어만 지원하므로 pass 처리
        pass
    
    def on_profile_selected(self, event: Event):
        """프로파일이 선택되었을 때"""
        profile = event.data.get('profile')
        print(f"[이벤트] 프로파일 선택: {profile}")
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.profile_selector.set(profile)
    
    def on_sidebar_settings_changed(self, event: Event):
        """사이드바 설정이 변경되었을 때"""
        width = event.data.get('width')
        print(f"[이벤트] 사이드바 너비 변경: {width}")
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.configure(width=width)
    
    def on_notification_settings_changed(self, event: Event):
        """알림 설정이 변경되었을 때"""
        enabled = event.data.get('enabled')
        print(f"[이벤트] 알림 설정 변경: {enabled}")
        try:
            from ...utils.alarm_manager import get_alarm_manager
            alarm_manager = get_alarm_manager()
            if enabled:
                alarm_manager.start()
            else:
                alarm_manager.stop()
        except Exception as e:
            print(f"알림 설정 변경 실패: {e}")
    
    def on_alarm_enabled(self, event: Event):
        """알람이 활성화되었을 때"""
        print(f"[이벤트] 알람 활성화")
        try:
            from ...utils.alarm_manager import get_alarm_manager
            alarm_manager = get_alarm_manager()
            alarm_manager.start()
        except Exception as e:
            print(f"알람 활성화 실패: {e}")
    
    def on_alarm_disabled(self, event: Event):
        """알람이 비활성화되었을 때"""
        print(f"[이벤트] 알람 비활성화")
        try:
            from ...utils.alarm_manager import get_alarm_manager
            alarm_manager = get_alarm_manager()
            alarm_manager.stop()
        except Exception as e:
            print(f"알람 비활성화 실패: {e}")
    
    def on_tool_test_requested(self, event: Event):
        """도구 테스트가 요청되었을 때"""
        tool_name = event.data.get('tool')
        print(f"[이벤트] 도구 테스트 요청: {tool_name}")
        
        try:
            from tkinter import messagebox
            from ...external import get_tool_manager
            
            tool_manager = get_tool_manager()
            if tool_manager.has_tool(tool_name):
                version = tool_manager.get_tool_version(tool_name)
                if version:
                    messagebox.showinfo("테스트 성공", 
                        f"{tool_name} 테스트 성공!\n버전: {version}")
                else:
                    messagebox.showinfo("테스트 성공", 
                        f"{tool_name} 테스트 성공!")
            else:
                messagebox.showerror("테스트 실패", 
                    f"{tool_name}을(를) 찾을 수 없습니다.")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("오류", f"도구 테스트 실패: {e}")
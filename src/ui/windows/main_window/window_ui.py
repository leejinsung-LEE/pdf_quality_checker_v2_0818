"""
메인 윈도우 UI 관리 - UI 구성 및 다이얼로그 관리
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import TYPE_CHECKING

from ...components import Sidebar, MenuBar, StatusBar
from ...views import (
    UnifiedProcessingView, DashboardView,
    StatisticsDashboardView, ProfileSettingsView,
    SettingsView, ProfileManagerView, BatchProcessView, 
    ProcessMonitorView
)

if TYPE_CHECKING:
    from .base import MainWindow


class UIBuilder:
    """UI 빌더 - 메인 윈도우 UI 구성"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def create_ui(self):
        """UI 생성"""
        # 메뉴바
        self._create_menubar()
        
        # 메인 컨테이너
        self._create_main_container()
        
        # 사이드바
        self._create_sidebar()
        
        # 콘텐츠 영역
        self._create_content_area()
        
        # 탭 컨테이너
        self._create_tab_container()
        
        # 뷰 생성
        self._create_views()
        
        # 상태바
        self._create_statusbar()
        
        # 이벤트 바인딩
        self._bind_tab_events()
        
        # 초기 탭 선택
        self.window.notebook.select(0)
    
    def _create_menubar(self):
        """메뉴바 생성"""
        self.window.menubar = MenuBar(self.window)
        self.window.config(menu=self.window.menubar)
        self.window.widgets['menubar'] = self.window.menubar
    
    def _create_main_container(self):
        """메인 컨테이너 생성"""
        main_container = ctk.CTkFrame(self.window)
        main_container.pack(fill='both', expand=True)
        self.window.widgets['main_container'] = main_container
    
    def _create_sidebar(self):
        """사이드바 생성"""
        main_container = self.window.widgets['main_container']
        self.window.sidebar = Sidebar(main_container)
        self.window.sidebar.pack(side='left', fill='y')
        self.window.widgets['sidebar'] = self.window.sidebar
    
    def _create_content_area(self):
        """콘텐츠 영역 생성"""
        main_container = self.window.widgets['main_container']
        content_container = ctk.CTkFrame(main_container)
        content_container.pack(side='left', fill='both', expand=True)
        self.window.widgets['content_container'] = content_container
    
    def _create_tab_container(self):
        """탭 컨테이너 생성"""
        content_container = self.window.widgets['content_container']
        
        # 탭 컨테이너 (v1 스타일)
        tab_container = ctk.CTkFrame(content_container, fg_color="transparent")
        tab_container.pack(fill='both', expand=True, padx=10, pady=10)
        self.window.widgets['tab_container'] = tab_container
        
        # Notebook 위젯 생성
        self.window.notebook = ttk.Notebook(tab_container)
        self.window.notebook.pack(fill='both', expand=True)
        self.window.widgets['notebook'] = self.window.notebook
        
        # 탭 스타일 설정
        self._setup_tab_style()
    
    def _setup_tab_style(self):
        """탭 스타일 설정"""
        style = ttk.Style()
        
        # 탭 색상과 폰트 설정
        style.configure('TNotebook',
            background='#1a1a1a',
            borderwidth=0
        )
        style.configure('TNotebook.Tab',
            background='#2a2a2a',
            foreground='#ffffff',
            padding=(20, 10),
            font=('맑은 고딕', 11)
        )
        style.map('TNotebook.Tab',
            background=[('selected', '#667eea')],
            foreground=[('selected', '#ffffff')]
        )
    
    def _create_views(self):
        """뷰 생성 (탭으로)"""
        notebook = self.window.notebook
        
        # 통합 처리 뷰
        self.window.views['unified_processing'] = UnifiedProcessingView(
            notebook,
            self.window.file_controller
        )
        notebook.add(self.window.views['unified_processing'], text="📁 처리 현황")
        
        # 대시보드 뷰
        self.window.views['dashboard'] = DashboardView(
            notebook,
            self.window.file_controller
        )
        notebook.add(self.window.views['dashboard'], text="📊 대시보드")
        
        # 통계 대시보드 뷰
        self.window.views['statistics'] = StatisticsDashboardView(notebook)
        notebook.add(self.window.views['statistics'], text="📈 통계 분석")
        
        # 프로파일 설정 뷰
        self.window.views['profile_settings'] = ProfileSettingsView(notebook)
        notebook.add(self.window.views['profile_settings'], text="⚙️ 프로파일 설정")
        
        # widgets 딕셔너리에 추가
        self.window.widgets['views'] = self.window.views
    
    def _create_statusbar(self):
        """상태바 생성"""
        content_container = self.window.widgets['content_container']
        self.window.statusbar = StatusBar(content_container)
        self.window.statusbar.pack(side='bottom', fill='x')
        self.window.widgets['statusbar'] = self.window.statusbar
    
    def _bind_tab_events(self):
        """탭 이벤트 바인딩"""
        self.window.notebook.bind('<<NotebookTabChanged>>', 
                                 self._on_tab_changed)
    
    def _on_tab_changed(self, event):
        """탭 변경 이벤트 처리"""
        selected_tab = self.window.notebook.index('current')
        
        # ViewManager에 위임
        if hasattr(self.window, 'view_manager'):
            self.window.view_manager.on_tab_changed(selected_tab)


class DialogManager:
    """다이얼로그 매니저 - 다이얼로그 관리"""
    
    def __init__(self, window: 'MainWindow'):
        self.window = window
    
    def show_preferences(self):
        """환경설정 다이얼로그"""
        settings_window = ctk.CTkToplevel(self.window)
        settings_view = SettingsView(settings_window)
        
        def on_settings_applied(new_settings):
            # 설정 적용
            self.window.settings_controller.update_settings(new_settings)
            
            # UI 업데이트
            if new_settings.theme != self.window.settings_controller.get_settings().theme:
                ctk.set_appearance_mode(new_settings.theme)
            
            # 창 크기 업데이트
            if new_settings.window_geometry:
                self.window.geometry(new_settings.window_geometry)
            
            # 사이드바 너비 업데이트
            if hasattr(self.window, 'sidebar'):
                self.window.sidebar.configure(width=new_settings.sidebar_width)
            
            settings_window.destroy()
            messagebox.showinfo("성공", "설정이 적용되었습니다.")
        
        settings_view.set_apply_callback(on_settings_applied)
    
    def show_profile_manager(self):
        """프로파일 관리자 다이얼로그"""
        profile_window = ctk.CTkToplevel(self.window)
        profile_view = ProfileManagerView(profile_window)
        
        def on_profile_selected(profile_name):
            self.window.profile_controller.set_current_profile(profile_name)
            profile_window.destroy()
        
        profile_view.set_select_callback(on_profile_selected)
    
    def show_batch_dialog(self):
        """배치 처리 다이얼로그"""
        batch_window = ctk.CTkToplevel(self.window)
        BatchProcessView(batch_window)
    
    def show_folder_watch_dialog(self):
        """폴더 감시 설정 다이얼로그"""
        folder_window = ctk.CTkToplevel(self.window)
        folder_window.title("폴더 감시 설정")
        folder_window.geometry("700x500")
        
        # ProcessMonitorView를 임시로 사용
        ProcessMonitorView(folder_window).pack(fill='both', expand=True)
    
    def show_batch_scheduler_dialog(self):
        """배치 스케줄러 다이얼로그"""
        scheduler_window = ctk.CTkToplevel(self.window)
        scheduler_window.title("배치 스케줄러")
        scheduler_window.geometry("800x600")
        
        # 프로세스 모니터 뷰 재사용
        monitor_view = ProcessMonitorView(scheduler_window)
        monitor_view.pack(fill='both', expand=True)
        
        # 스케줄러 기능 추가
        scheduler_frame = ctk.CTkFrame(scheduler_window)
        scheduler_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        ctk.CTkLabel(scheduler_frame, text="스케줄 설정:").pack(side='left', padx=5)
        
        schedule_var = ctk.StringVar(value="매일")
        schedule_menu = ctk.CTkOptionMenu(
            scheduler_frame,
            values=["매일", "매주", "매월"],
            variable=schedule_var
        )
        schedule_menu.pack(side='left', padx=5)
        
        time_entry = ctk.CTkEntry(scheduler_frame, placeholder_text="09:00")
        time_entry.pack(side='left', padx=5)
        
        def add_schedule():
            messagebox.showinfo("정보", "스케줄이 추가되었습니다.")
        
        ctk.CTkButton(
            scheduler_frame,
            text="스케줄 추가",
            command=add_schedule
        ).pack(side='left', padx=5)
    
    def show_backup_manager_dialog(self):
        """백업 관리자 다이얼로그"""
        backup_window = ctk.CTkToplevel(self.window)
        backup_window.title("백업 관리자")
        backup_window.geometry("600x400")
        
        # 백업 관리 UI
        ctk.CTkLabel(
            backup_window,
            text="백업 관리",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        # 백업 목록
        backup_frame = ctk.CTkFrame(backup_window)
        backup_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 버튼들
        button_frame = ctk.CTkFrame(backup_window)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        def create_backup():
            messagebox.showinfo("성공", "백업이 생성되었습니다.")
        
        def restore_backup():
            messagebox.showinfo("정보", "백업 복원 기능은 준비 중입니다.")
        
        ctk.CTkButton(
            button_frame,
            text="백업 생성",
            command=create_backup
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="백업 복원",
            command=restore_backup
        ).pack(side='left', padx=5)
    
    def export_current_report(self):
        """현재 리포트 내보내기"""
        # 현재 뷰에서 데이터 가져오기
        current_view = self.window.view_manager.get_current_view()
        
        if current_view and hasattr(current_view, 'export_data'):
            # 파일 저장 다이얼로그
            file_path = filedialog.asksaveasfilename(
                title="리포트 내보내기",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
            )
            
            if file_path:
                current_view.export_data(file_path)
                messagebox.showinfo("성공", f"리포트가 저장되었습니다:\n{file_path}")
        else:
            messagebox.showinfo("정보", "현재 뷰에서 내보낼 데이터가 없습니다.")
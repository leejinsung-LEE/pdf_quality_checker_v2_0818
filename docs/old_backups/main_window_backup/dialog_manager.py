"""
다이얼로그 매니저 - 다이얼로그 관리
"""

from tkinter import messagebox, filedialog
from typing import TYPE_CHECKING
import customtkinter as ctk

from ...views import (
    SettingsView, ProfileManagerView, BatchProcessView, 
    ProcessMonitorView
)

if TYPE_CHECKING:
    from .base import MainWindow


class DialogManager:
    """다이얼로그 매니저"""
    
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
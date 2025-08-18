"""
Process Monitor View 이벤트 핸들러 모듈
기능: 사용자 인터랙션 처리, 필터 적용, 선택 관리
의존성: tkinter, tkcalendar, FileItem
최종 수정: 2025-01-11
"""

from typing import TYPE_CHECKING
from tkinter import messagebox
import tkinter as tk
from datetime import datetime

if TYPE_CHECKING:
    from .base import ProcessMonitorView


class EventHandler:
    """이벤트 처리 헬퍼 클래스"""
    
    def __init__(self, view: 'ProcessMonitorView'):
        """
        초기화
        
        Args:
            view: ProcessMonitorView 인스턴스
        """
        self.view = view
    
    def on_realtime_double_click(self, event):
        """실시간 트리 더블클릭 이벤트"""
        selection = self.view.realtime_tree.selection()
        if selection:
            item_id = selection[0]
            file_id = self.view.realtime_tree.item(item_id)['tags'][0]
            file_item = self.view.controller.get_file(file_id)
            if file_item:
                self._show_file_details(file_item)
    
    def on_realtime_selection(self, event):
        """실시간 트리 선택 변경 이벤트"""
        selection = self.view.realtime_tree.selection()
        self.view.selected_items = {
            self.view.realtime_tree.item(item_id)['tags'][0]
            for item_id in selection
        }
    
    def on_history_double_click(self, event):
        """이력 트리 더블클릭 이벤트"""
        selection = self.view.history_tree.selection()
        if selection:
            item_id = selection[0]
            entry_id = int(self.view.history_tree.item(item_id)['tags'][0])
            entry = next((e for e in self.view.current_entries if e.id == entry_id), None)
            if entry:
                self.view.action_handler.view_report_for_entry(entry)
    
    def on_history_selection(self, event):
        """이력 트리 선택 변경 이벤트"""
        selection = self.view.history_tree.selection()
        self.view.selected_history_ids = {
            int(self.view.history_tree.item(item_id)['tags'][0])
            for item_id in selection
        }
    
    def on_date_range_changed(self):
        """날짜 범위 변경 이벤트"""
        if self.view.date_range.get() == "custom":
            self._show_custom_date_dialog()
        else:
            # 날짜 범위 변경 시 첫 페이지로 이동
            self.view.current_page = 1
            self.view.tree_handler.refresh_history()
    
    def apply_filters(self):
        """필터 적용"""
        self.view.tree_handler.refresh()
        self.view.tree_handler.refresh_history()
    
    def reset_filters(self):
        """필터 초기화"""
        self.view.filter_status.set("all")
        self.view.search_var.set("")
        self.view.folder_filter.set("all")
        self.view.date_range.set("today")
        self.view.profile_filter.set("all")
        
        self.apply_filters()
    
    def _show_file_details(self, file_item):
        """파일 상세 정보 표시"""
        details_window = tk.Toplevel(self.view)
        details_window.title(f"파일 상세 정보 - {file_item.filename}")
        details_window.geometry("600x500")
        details_window.resizable(False, False)
        
        # 정보 표시
        info_frame = tk.Frame(details_window, padx=20, pady=20)
        info_frame.pack(fill='both', expand=True)
        
        # 기본 정보
        tk.Label(info_frame, text="기본 정보", font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10, sticky='w')
        
        tk.Label(info_frame, text="파일명:").grid(row=1, column=0, sticky='w', pady=2)
        tk.Label(info_frame, text=file_item.filename).grid(row=1, column=1, sticky='w', pady=2)
        
        tk.Label(info_frame, text="경로:").grid(row=2, column=0, sticky='w', pady=2)
        tk.Label(info_frame, text=str(file_item.filepath)).grid(row=2, column=1, sticky='w', pady=2)
        
        tk.Label(info_frame, text="프로파일:").grid(row=3, column=0, sticky='w', pady=2)
        tk.Label(info_frame, text=file_item.profile or "default").grid(row=3, column=1, sticky='w', pady=2)
        
        tk.Label(info_frame, text="상태:").grid(row=4, column=0, sticky='w', pady=2)
        tk.Label(info_frame, text=file_item.status.value).grid(row=4, column=1, sticky='w', pady=2)
        
        # 처리 정보
        tk.Label(info_frame, text="처리 정보", font=('Arial', 12, 'bold')).grid(row=5, column=0, columnspan=2, pady=(20, 10), sticky='w')
        
        tk.Label(info_frame, text="추가 시간:").grid(row=6, column=0, sticky='w', pady=2)
        tk.Label(info_frame, text=file_item.added_time.strftime("%Y-%m-%d %H:%M:%S")).grid(row=6, column=1, sticky='w', pady=2)
        
        if file_item.start_time:
            tk.Label(info_frame, text="시작 시간:").grid(row=7, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=file_item.start_time.strftime("%Y-%m-%d %H:%M:%S")).grid(row=7, column=1, sticky='w', pady=2)
        
        if file_item.end_time:
            tk.Label(info_frame, text="종료 시간:").grid(row=8, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=file_item.end_time.strftime("%Y-%m-%d %H:%M:%S")).grid(row=8, column=1, sticky='w', pady=2)
            
            duration = file_item.end_time - file_item.start_time
            tk.Label(info_frame, text="처리 시간:").grid(row=9, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=f"{duration.seconds}초").grid(row=9, column=1, sticky='w', pady=2)
        
        # 결과 정보
        if file_item.result:
            tk.Label(info_frame, text="검사 결과", font=('Arial', 12, 'bold')).grid(row=10, column=0, columnspan=2, pady=(20, 10), sticky='w')
            
            tk.Label(info_frame, text="페이지 수:").grid(row=11, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=str(file_item.result.page_count)).grid(row=11, column=1, sticky='w', pady=2)
            
            tk.Label(info_frame, text="오류 수:").grid(row=12, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=str(file_item.result.error_count)).grid(row=12, column=1, sticky='w', pady=2)
            
            tk.Label(info_frame, text="경고 수:").grid(row=13, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=str(file_item.result.warning_count)).grid(row=13, column=1, sticky='w', pady=2)
            
            # 점수 계산
            score = max(0, 100 - (file_item.result.error_count * 10) - (file_item.result.warning_count * 5))
            tk.Label(info_frame, text="품질 점수:").grid(row=14, column=0, sticky='w', pady=2)
            tk.Label(info_frame, text=f"{score}점").grid(row=14, column=1, sticky='w', pady=2)
        
        # 오류 메시지
        if file_item.error_message:
            tk.Label(info_frame, text="오류 메시지", font=('Arial', 12, 'bold')).grid(row=15, column=0, columnspan=2, pady=(20, 10), sticky='w')
            
            error_text = tk.Text(info_frame, height=5, width=60, wrap='word')
            error_text.grid(row=16, column=0, columnspan=2, pady=5)
            error_text.insert('1.0', file_item.error_message)
            error_text.config(state='disabled')
        
        # 버튼
        button_frame = tk.Frame(details_window)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="보고서 보기",
            command=lambda: self.view.action_handler.view_report()
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="닫기",
            command=details_window.destroy
        ).pack(side='left', padx=5)
    
    def _show_custom_date_dialog(self):
        """사용자 정의 날짜 범위 선택 대화상자"""
        dialog = tk.Toplevel(self.view)
        dialog.title("날짜 범위 선택")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # 날짜 선택
        tk.Label(dialog, text="시작 날짜:").grid(row=0, column=0, padx=10, pady=10, sticky='w')
        start_entry = tk.Entry(dialog)
        start_entry.grid(row=0, column=1, padx=10, pady=10)
        start_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        tk.Label(dialog, text="종료 날짜:").grid(row=1, column=0, padx=10, pady=10, sticky='w')
        end_entry = tk.Entry(dialog)
        end_entry.grid(row=1, column=1, padx=10, pady=10)
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        def apply_custom_range():
            try:
                start_date = datetime.strptime(start_entry.get(), "%Y-%m-%d").date()
                end_date = datetime.strptime(end_entry.get(), "%Y-%m-%d").date()
                
                if start_date > end_date:
                    messagebox.showerror("오류", "시작 날짜는 종료 날짜보다 이전이어야 합니다.")
                    return
                
                self.view.custom_start_date = start_date
                self.view.custom_end_date = end_date
                self.view.current_page = 1
                self.view.tree_handler.refresh_history()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("오류", "올바른 날짜 형식을 입력하세요. (YYYY-MM-DD)")
        
        # 버튼
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        tk.Button(
            button_frame,
            text="적용",
            command=apply_custom_range
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="취소",
            command=dialog.destroy
        ).pack(side='left', padx=5)
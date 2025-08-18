"""
처리 이력 이벤트 핸들러
기능: 사용자 액션 처리
최종 수정: 2025-01-12
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from pathlib import Path
import webbrowser
import os
from typing import TYPE_CHECKING

# 순환 참조 방지
if TYPE_CHECKING:
    from .base import HistoryView
    from ....data import HistoryEntry


class EventHandler:
    """이벤트 처리 헬퍼 클래스"""
    
    def __init__(self, view: 'HistoryView'):
        self.view = view
        
    def on_date_range_change(self, value):
        """날짜 범위 변경"""
        if value == "사용자 지정":
            # 날짜 선택 다이얼로그 표시
            self.show_date_picker()
        else:
            self.view.apply_filters()
    
    def on_per_page_change(self, value):
        """페이지당 항목 수 변경"""
        self.view.items_per_page = int(value)
        self.view.current_page = 1
        self.view.apply_filters()
    
    def show_date_picker(self):
        """날짜 선택 다이얼로그"""
        # 간단한 구현 - 실제로는 달력 위젯 사용
        messagebox.showinfo("알림", "날짜 선택 기능은 추후 구현 예정입니다.")
        self.view.date_range.set("전체")
    
    def show_details(self, entry: 'HistoryEntry'):
        """상세 정보 표시"""
        # 보고서가 있으면 열기
        if entry.report_paths:
            # HTML 보고서 우선
            if 'html' in entry.report_paths:
                report_path = Path(entry.report_paths['html'])
                if report_path.exists():
                    webbrowser.open(str(report_path))
                else:
                    messagebox.showwarning("경고", "보고서 파일을 찾을 수 없습니다.")
            else:
                messagebox.showinfo("정보", "HTML 보고서가 없습니다.")
        else:
            # 간단한 정보 다이얼로그
            processed_date = entry.processed_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(entry, 'processed_at') else entry.processed_date_str
            info = f"""파일: {entry.filename}
처리일시: {processed_date}
프로파일: {entry.profile_used}
품질점수: {entry.quality_score:.1f}
오류: {entry.error_count}개
경고: {entry.warning_count}개
처리시간: {entry.processing_time:.1f}초"""
            
            messagebox.showinfo("처리 상세 정보", info)
    
    def prev_page(self):
        """이전 페이지"""
        if self.view.current_page > 1:
            self.view.current_page -= 1
            self.view.apply_filters()
    
    def next_page(self):
        """다음 페이지"""
        total_pages = max(1, (self.view.total_items + self.view.items_per_page - 1) // self.view.items_per_page)
        if self.view.current_page < total_pages:
            self.view.current_page += 1
            self.view.apply_filters()
    
    def delete_selected(self):
        """선택 항목 삭제"""
        if not self.view.selected_ids:
            return
        
        count = len(self.view.selected_ids)
        if messagebox.askyesno("확인", f"{count}개 항목을 삭제하시겠습니까?"):
            deleted = self.view.data_manager.delete_history(list(self.view.selected_ids))
            
            if deleted > 0:
                messagebox.showinfo("완료", f"{deleted}개 항목이 삭제되었습니다.")
                self.view.refresh_data()
            else:
                messagebox.showerror("오류", "삭제 중 오류가 발생했습니다.")
    
    def export_to_csv(self):
        """CSV로 내보내기"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
            initialfile=f"history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            # 현재 필터 적용된 날짜 범위 사용
            if hasattr(self.view, 'filter_manager'):
                start_date, end_date = self.view.filter_manager.calculate_date_range()
            else:
                start_date, end_date = None, None
            
            if self.view.data_manager.export_to_csv(Path(filename), start_date, end_date):
                messagebox.showinfo("완료", "CSV 파일이 저장되었습니다.")
                
                # 파일 열기 여부 확인
                if messagebox.askyesno("확인", "파일을 열어보시겠습니까?"):
                    try:
                        os.startfile(filename)  # Windows
                    except:
                        webbrowser.open(filename)  # 다른 OS
            else:
                messagebox.showerror("오류", "CSV 저장 중 오류가 발생했습니다.")
    
    def clear_all_history(self):
        """전체 이력 삭제"""
        if messagebox.askyesno(
            "경고", 
            "모든 처리 이력을 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."
        ):
            if messagebox.askyesno(
                "최종 확인",
                "정말로 모든 이력을 삭제하시겠습니까?"
            ):
                if self.view.data_manager.clear_all_history():
                    messagebox.showinfo("완료", "모든 이력이 삭제되었습니다.")
                    self.view.refresh_data()
                else:
                    messagebox.showerror("오류", "이력 삭제 중 오류가 발생했습니다.")
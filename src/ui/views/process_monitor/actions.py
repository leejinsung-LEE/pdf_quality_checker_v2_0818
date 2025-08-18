"""
Process Monitor View 액션 핸들러 모듈
기능: 파일 추가, 처리 제어, 데이터 내보내기, 보고서 생성
의존성: tkinter.filedialog, webbrowser, pathlib
최종 수정: 2025-01-11
"""

from typing import TYPE_CHECKING
from tkinter import filedialog, messagebox
import webbrowser
import os
from pathlib import Path
from datetime import datetime
import json
import csv

from ...controllers import FileStatus
from ....data import HistoryEntry

if TYPE_CHECKING:
    from .base import ProcessMonitorView


class ActionHandler:
    """액션 처리 헬퍼 클래스"""
    
    def __init__(self, view: 'ProcessMonitorView'):
        """
        초기화
        
        Args:
            view: ProcessMonitorView 인스턴스
        """
        self.view = view
    
    def add_files(self):
        """파일 추가"""
        files = filedialog.askopenfilenames(
            title="PDF 파일 선택",
            filetypes=[("PDF 파일", "*.pdf"), ("모든 파일", "*.*")]
        )
        
        if files:
            for filepath in files:
                self.view.controller.add_file(Path(filepath))
            
            # 처리 시작
            if not self.view.controller.is_processing:
                self.view.controller.start_processing()
    
    def pause_processing(self):
        """처리 일시정지/재개"""
        if self.view.controller.is_processing:
            self.view.controller.pause_processing()
            messagebox.showinfo("알림", "처리가 일시정지되었습니다.")
        else:
            self.view.controller.resume_processing()
            messagebox.showinfo("알림", "처리가 재개되었습니다.")
    
    def clear_completed(self):
        """완료된 항목 제거"""
        files = self.view.controller.get_all_files()
        completed_files = [
            f for f in files 
            if f.status in [FileStatus.COMPLETED, FileStatus.ERROR, FileStatus.CANCELLED]
        ]
        
        if completed_files:
            if messagebox.askyesno("확인", f"{len(completed_files)}개의 완료된 항목을 제거하시겠습니까?"):
                for file_item in completed_files:
                    self.view.controller.remove_file(file_item.id)
        else:
            messagebox.showinfo("알림", "제거할 완료된 항목이 없습니다.")
    
    def open_selected_file(self):
        """선택된 파일 열기"""
        if self.view.selected_items:
            file_id = next(iter(self.view.selected_items))
            file_item = self.view.controller.get_file(file_id)
            if file_item and file_item.filepath.exists():
                os.startfile(file_item.filepath)
    
    def view_report(self):
        """선택된 파일의 보고서 보기"""
        if self.view.selected_items:
            file_id = next(iter(self.view.selected_items))
            file_item = self.view.controller.get_file(file_id)
            if file_item and file_item.report_path and file_item.report_path.exists():
                webbrowser.open(str(file_item.report_path))
            else:
                messagebox.showinfo("알림", "보고서가 아직 생성되지 않았습니다.")
    
    def view_report_for_entry(self, entry: HistoryEntry):
        """이력 항목의 보고서 보기"""
        if entry.report_path:
            report_file = Path(entry.report_path)
            if report_file.exists():
                webbrowser.open(str(report_file))
            else:
                messagebox.showwarning("경고", "보고서 파일을 찾을 수 없습니다.")
        else:
            messagebox.showinfo("알림", "이 항목에는 보고서가 없습니다.")
    
    def delete_history(self):
        """선택된 이력 삭제"""
        if self.view.selected_history_ids:
            if messagebox.askyesno("확인", f"{len(self.view.selected_history_ids)}개의 이력을 삭제하시겠습니까?"):
                for entry_id in self.view.selected_history_ids:
                    self.view.data_manager.delete_history(entry_id)
                
                self.view.selected_history_ids.clear()
                self.view.tree_handler.refresh_history()
                messagebox.showinfo("완료", "선택된 이력이 삭제되었습니다.")
    
    def export_data(self):
        """데이터 내보내기"""
        # 내보낼 형식 선택
        export_format = messagebox.askquestion(
            "내보내기 형식",
            "CSV 형식으로 내보내시겠습니까?\n(아니오를 선택하면 JSON 형식)",
            icon='question'
        )
        
        # 파일 선택 대화상자
        if export_format == 'yes':
            file_path = filedialog.asksaveasfilename(
                title="데이터 내보내기",
                defaultextension=".csv",
                filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")]
            )
            if file_path:
                self._export_to_csv(file_path)
        else:
            file_path = filedialog.asksaveasfilename(
                title="데이터 내보내기",
                defaultextension=".json",
                filetypes=[("JSON 파일", "*.json"), ("모든 파일", "*.*")]
            )
            if file_path:
                self._export_to_json(file_path)
    
    def _export_to_csv(self, file_path: str):
        """CSV로 내보내기"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    '처리일시', '파일명', '프로파일', '페이지수',
                    '오류수', '경고수', '점수', '보고서경로'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for entry in self.view.current_entries:
                    score = max(0, 100 - (entry.error_count * 10) - (entry.warning_count * 5))
                    writer.writerow({
                        '처리일시': entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        '파일명': entry.filename,
                        '프로파일': entry.profile or "default",
                        '페이지수': entry.page_count or 0,
                        '오류수': entry.error_count,
                        '경고수': entry.warning_count,
                        '점수': score,
                        '보고서경로': entry.report_path or ""
                    })
            
            messagebox.showinfo("완료", f"데이터를 {file_path}에 내보냈습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"내보내기 실패: {str(e)}")
    
    def _export_to_json(self, file_path: str):
        """JSON으로 내보내기"""
        try:
            data = []
            for entry in self.view.current_entries:
                score = max(0, 100 - (entry.error_count * 10) - (entry.warning_count * 5))
                data.append({
                    'id': entry.id,
                    'timestamp': entry.timestamp.isoformat(),
                    'filename': entry.filename,
                    'filepath': entry.filepath,
                    'profile': entry.profile,
                    'page_count': entry.page_count,
                    'error_count': entry.error_count,
                    'warning_count': entry.warning_count,
                    'score': score,
                    'processing_time': entry.processing_time,
                    'report_path': entry.report_path
                })
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("완료", f"데이터를 {file_path}에 내보냈습니다.")
            
        except Exception as e:
            messagebox.showerror("오류", f"내보내기 실패: {str(e)}")
    
    def load_more(self):
        """더 많은 항목 로드"""
        # 페이지당 항목 수 증가
        self.view.items_per_page = min(500, self.view.items_per_page + 100)
        self.view.tree_handler.refresh_history()
    
    def prev_page(self):
        """이전 페이지"""
        if self.view.current_page > 1:
            self.view.current_page -= 1
            self.view.tree_handler.refresh_history()
    
    def next_page(self):
        """다음 페이지"""
        total_pages = (self.view.total_items + self.view.items_per_page - 1) // self.view.items_per_page
        if self.view.current_page < total_pages:
            self.view.current_page += 1
            self.view.tree_handler.refresh_history()
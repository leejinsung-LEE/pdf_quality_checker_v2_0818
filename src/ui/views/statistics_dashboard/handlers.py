"""
이벤트 핸들러 - 통계 대시보드 이벤트 처리
"""

from tkinter import messagebox, filedialog
from typing import TYPE_CHECKING
import csv
from datetime import datetime

if TYPE_CHECKING:
    from .base import StatisticsDashboardView


class EventHandler:
    """이벤트 핸들러"""
    
    def __init__(self, view: 'StatisticsDashboardView'):
        self.view = view
        
    def export_statistics(self):
        """통계 내보내기"""
        # 파일 경로 선택
        file_path = filedialog.asksaveasfilename(
            title="통계 내보내기",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            # 현재 통계 가져오기
            stats = self.view.data_processor.get_statistics(self.view.current_period)
            
            # CSV 파일로 저장
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # 헤더
                writer.writerow(["PDF Quality Checker - 통계 리포트"])
                writer.writerow([f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
                writer.writerow([f"기간: {self.view.current_period}"])
                writer.writerow([])
                
                # 요약 통계
                writer.writerow(["요약 통계"])
                writer.writerow(["항목", "값"])
                writer.writerow(["총 처리 파일", stats.get('total_files', 0)])
                writer.writerow(["성공", stats.get('success_count', 0)])
                writer.writerow(["실패", stats.get('error_count', 0)])
                writer.writerow(["성공률", f"{stats.get('success_rate', 0):.1f}%"])
                writer.writerow(["평균 처리 시간", f"{stats.get('avg_processing_time', 0):.1f}초"])
                writer.writerow(["총 에러 수", stats.get('total_errors', 0)])
                writer.writerow([])
                
                # 최근 처리 내역
                writer.writerow(["최근 처리 내역"])
                writer.writerow(["파일명", "상태", "처리시간", "프로파일", "타임스탬프"])
                
                recent_history = self.view.history_manager.get_recent_history(50)
                for history in recent_history:
                    writer.writerow([
                        history.file_name,
                        history.status,
                        f"{history.processing_time:.1f}초" if history.processing_time else "-",
                        history.profile_name or "기본",
                        history.timestamp.strftime('%Y-%m-%d %H:%M:%S') if history.timestamp else "-"
                    ])
                    
            messagebox.showinfo("성공", f"통계를 내보냈습니다:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("오류", f"통계 내보내기 실패:\n{str(e)}")
            
    def show_more_history(self):
        """더 많은 이력 보기"""
        # 히스토리 뷰 열기 (별도 창으로)
        import customtkinter as ctk
        from tkinter import ttk
        
        history_window = ctk.CTkToplevel(self.view)
        history_window.title("처리 이력")
        history_window.geometry("800x600")
        
        # 트리뷰 생성
        columns = ("파일명", "상태", "처리시간", "프로파일", "타임스탬프")
        tree = ttk.Treeview(history_window, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 스크롤바
        scrollbar = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 전체 히스토리 로드
        all_history = self.view.history_manager.get_all_history()
        
        for history in all_history:
            status = "✅ 성공" if history.status == "completed" else "❌ 실패"
            processing_time = f"{history.processing_time:.1f}초" if history.processing_time else "-"
            timestamp = history.timestamp.strftime('%Y-%m-%d %H:%M:%S') if history.timestamp else "-"
            
            tree.insert("", "end", values=(
                history.file_name,
                status,
                processing_time,
                history.profile_name or "기본",
                timestamp
            ))
            
        # 닫기 버튼
        close_btn = ctk.CTkButton(
            history_window,
            text="닫기",
            command=history_window.destroy
        )
        close_btn.pack(pady=10)